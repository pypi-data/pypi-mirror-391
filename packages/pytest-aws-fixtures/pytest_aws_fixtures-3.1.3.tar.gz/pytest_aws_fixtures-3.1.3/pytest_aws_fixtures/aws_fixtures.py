import json
import signal
import time
import uuid
from collections import defaultdict
from contextlib import suppress
from threading import Timer

import boto3
import jsonpath_ng
import pytest
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


@pytest.fixture(scope="session", autouse=True)
def term_handler():
    """An autouse fixture to redirect SIGTERM to SIGINT so that pytest fixtures teardown
    correctly.

    See this documentation for more details:
    https://docs.pytest.org/en/latest/explanation/fixtures.html#a-note-about-fixture-cleanup
    """
    orig = signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    yield
    signal.signal(signal.SIGTERM, orig)


@pytest.fixture(scope="session")
def current_aws_region():
    """Returns current region in use by the configured credentials.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.session.Session().region_name


@pytest.fixture(scope="session")
def event_bridge_client():
    """Returns a boto3 client for AWS EventBridge.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("events")


@pytest.fixture
def event_bridge_list_targets_by_rule(event_bridge_client):
    """Provides a method to list targets by the given rule for the given event bus. This
    fixture will automatically paginate through the list to get the entire result set.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a rule can be found in the
    documentation for EventBridge API permissions. Specifically the `ListTargetsByRule`
    permission.
    https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-permissions-reference.html
    """

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's
        `list_targets_by_rule` method of the EventBridge client. This will also paginate
        through the list to get the entire result set.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events/client/list_targets_by_rule.html
        """
        result = event_bridge_client.list_targets_by_rule(**kwargs)
        # Pop off any NextToken passed in the original kwargs.
        kwargs.pop("NextToken", None)
        # Loop to retrieve all the targets if there are many.
        while result.get("NextToken"):
            next_page = event_bridge_client.list_targets_by_rule(
                NextToken=result["NextToken"], **kwargs
            )
            result["Targets"].extend(next_page["Targets"])
            result["NextToken"] = next_page["NextToken"]

        return result

    return _inner


@pytest.fixture
def event_bridge_remove_targets(event_bridge_client):
    """Provides a method to remove targets from the given rule for the given event bus.
    This fixture will automatically retry the removals in case of a
    ConcurrentModificationException.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a rule can be found in the
    documentation for EventBridge API permissions. Specifically the `RemoveTargets`
    permission.
    https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-permissions-reference.html
    """

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `remove_targets`
        method of the EventBridge client. This will also automatically retry the
        removals in case of a ConcurrentModificationException. Other errors are
        unhandled and will cause an assertion failure.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events/client/remove_targets.html
        """
        result = event_bridge_client.remove_targets(**kwargs)

        # Check that the targets that failed to be removed due to concurrent
        # modification errors. Other errors we can't handle, and need to fail.
        failed_targets = tuple(
            target
            for target in result["FailedEntries"]
            if target["ErrorCode"] == "ConcurrentModificationException"
        )
        assert len(result["FailedEntries"]) == len(failed_targets)

        # Pop off the IDs from the original kwargs as we are now going to use the failed
        # target IDs only.
        kwargs.pop("Ids", None)

        while failed_targets:
            result = event_bridge_client.remove_targets(
                Rule=kwargs["Rule"],
                EventBusName=kwargs["EventBusName"],
                Ids=tuple(target["TargetId"] for target in failed_targets),
            )
            # Check that the targets that failed to be removed due to concurrent
            # modification errors. Other errors we can't handle, and need to fail.
            failed_targets = tuple(
                target
                for target in result["FailedEntries"]
                if target["ErrorCode"] == "ConcurrentModificationException"
            )
            assert len(result["FailedEntries"]) == len(failed_targets)

    return _inner


@pytest.fixture
def event_bridge_put_rule(
    event_bridge_client, event_bridge_list_targets_by_rule, event_bridge_remove_targets
):
    """Provides a method to put a test event bridge rule using the provided kwargs. It
    then returns the result of describing the rule as the default return of just the ARN
    is not useful.

    If the rule name is not passed, it will be automatically populated with a unique
    value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same rule name can run into conflicts when running tests in rapid succession,
    leading to a slow down of the test suite as it retries to create the new rule with
    the conflicting name.

    This fixture will automatically remove the rule, and all of its targets, when
    leaving the scope the fixture was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a rule can be found in the
    documentation for EventBridge API permissions. Specifically the `PutRule`,
    `DescribeRule`, `ListTargetsByRule`, `RemoveTargets` and `DeleteRule` permissions.
    https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-permissions-reference.html
    """
    rules = []

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `put_rule` method
        of the EventBridge client.

        If a rule name is not passed, it will be automatically populated with a unique
        value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#EventBridge.Client.put_rule
        """
        # Add a unique rule name if it is not provided.
        if "Name" not in kwargs:
            kwargs["Name"] = str(uuid.uuid4())

        event_bridge_client.put_rule(**kwargs)
        # Can't just pass a `None` argument as boto3 requires any present kwargs to
        # actually be populated.
        event_bus_kwarg = (
            {"EventBusName": kwargs["EventBusName"]}
            if kwargs.get("EventBusName")
            else {}
        )
        rule = event_bridge_client.describe_rule(Name=kwargs["Name"], **event_bus_kwarg)
        rules.append(rule)
        return rule

    yield _inner

    # Now remove the test rules.
    for rule in rules:
        result = event_bridge_list_targets_by_rule(
            Rule=rule["Name"], EventBusName=rule["EventBusName"]
        )
        targets = result["Targets"]

        # Remove all the targets if present. Can't pass an empty list/tuple into this
        # call or it will fail.
        if targets:
            event_bridge_remove_targets(
                Rule=rule["Name"],
                EventBusName=rule["EventBusName"],
                Ids=tuple(target["Id"] for target in targets),
            )

        # Now that the targets are gone, remove the rule.
        event_bridge_client.delete_rule(
            Name=rule["Name"], EventBusName=rule["EventBusName"]
        )


@pytest.fixture
def event_bridge_put_targets(
    event_bridge_client, event_bridge_list_targets_by_rule, event_bridge_remove_targets
):
    """Provides a method to put event bridge targets using the provided kwargs. It then
    returns the result of describing the targets as the default return just provides the
    failed entries.

    If the target IDs are not passed, they will be automatically populated with a unique
    value.

    It is recommended to let the IDs be automatically generated. Otherwise re-use of
    the same target name can run into conflicts when running tests in rapid succession,
    leading to a slow down of the test suite as it retries to create the new target with
    the conflicting ID.

    This fixture will automatically remove the target(s) when leaving the scope the
    fixture was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a rule can be found in the
    documentation for EventBridge API permissions. Specifically the `PutTargets`,
    `DescribeRule`, `ListTargetsByRule`, `RemoveTargets` and `DeleteRule` permissions.
    https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-permissions-reference.html
    """
    targets_map = defaultdict(list)

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `put_targets`
        method of the EventBridge client.

        If a target(s) ID is not passed, it will be automatically populated with a
        unique value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#EventBridge.Client.put_targets
        """
        # Add a unique target ID if it is not provided.
        for target in kwargs["Targets"]:
            if "Id" not in target:
                target["Id"] = str(uuid.uuid4())

        result = event_bridge_client.put_targets(**kwargs)
        # Check that the targets that failed to be added due to concurrent
        # modification errors. Other errors we can't handle.
        failed_target_ids = tuple(
            failed_target["TargetId"]
            for failed_target in result["FailedEntries"]
            if failed_target["ErrorCode"] == "ConcurrentModificationException"
        )
        assert len(failed_target_ids) == len(result["FailedEntries"])

        # Remove the targets from kwargs as we are going to specify our own in the retry
        # logic.
        original_targets = kwargs.pop("Targets")

        while failed_target_ids:
            result = event_bridge_client.put_targets(
                Targets=(
                    target
                    for target in original_targets
                    if target["Id"] in failed_target_ids
                ),
                **kwargs,
            )
            failed_target_ids = tuple(
                failed_target["TargetId"]
                for failed_target in result["FailedEntries"]
                if failed_target["ErrorCode"] == "ConcurrentModificationException"
            )
            assert len(failed_target_ids) == len(result["FailedEntries"])

        # Now list the targets applied to the specified rule. We can reuse kwargs here
        # as the Targets list has been popped off at this point.
        result = event_bridge_list_targets_by_rule(**kwargs)

        # Only return the targets added in this request.
        originally_requested_target_ids = tuple(
            target["Id"] for target in original_targets
        )
        added_targets = tuple(
            target
            for target in result["Targets"]
            if target["Id"] in originally_requested_target_ids
        )
        # Use a tuple of rule_name, event_bus_name to key into the dictionary.
        targets_map[(kwargs["Rule"], kwargs.get("EventBusName", "default"))].extend(
            added_targets
        )

        return result

    yield _inner

    # Now clean up the targets.
    for rule_tuple, targets in targets_map.items():
        rule_name, event_bus_name = rule_tuple
        # Remove all the targets.
        event_bridge_remove_targets(
            Rule=rule_name,
            EventBusName=event_bus_name,
            Ids=tuple(target["Id"] for target in targets),
        )


@pytest.fixture(scope="session")
def scheduler_client():
    """Returns a boto3 client for AWS EventBridge Scheduler.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("scheduler")


@pytest.fixture(scope="session")
def sqs_resource():
    """Return a boto3 resource for SQS.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the
    resource multiple times.
    """
    return boto3.resource("sqs")


@pytest.fixture
def create_sqs_queue(sqs_resource):
    """Provides a method to create an SQS queue using the provided kwargs.

    If the queue name is not passed, it will be automatically populated with a unique
    value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same rule name can run into conflicts when running tests in rapid succession,
    leading to a slow down of the test suite as it retries to create the new queue with
    the conflicting name.

    This fixture will automatically delete the created queue(s) when leaving the scope
    the fixture was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a queue can be found in the
    documentation for SQS API permissions below. Specifically the `CreateQueue` and
    `DeleteQueue` permissions.
    https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-api-permissions-reference.html
    """
    queues = []

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's SQS Resource's
        `create_queue` method.

        If a queue name is not passed, it will be automatically populated with a unique
        value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.ServiceResource.create_queue
        """

        # Add a unique rule name if it is not provided.
        if "QueueName" not in kwargs:
            # If it's a FIFO queue, we have to add ".fifo" to the name.
            fifo = (
                ".fifo"
                if kwargs.get("Attributes", {}).get("FifoQueue") == "true"
                else ""
            )
            kwargs["QueueName"] = f"{uuid.uuid4()}{fifo}"

        queue = sqs_resource.create_queue(**kwargs)
        queues.append(queue)
        return queue

    yield _inner

    # Now delete all created queues.
    for queue in queues:
        queue.delete()


@pytest.fixture(scope="session")
def secretsmanager_client():
    """Return a secrets manager client for use in the test.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture is skipped.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the
    SecretsManager client multiple times.
    """
    return boto3.client("secretsmanager")


@pytest.fixture
def secretsmanager_create_secret(secretsmanager_client):
    """Provides a method to create a test secret using the provided kwargs, except if a
    secret name is not passed, it will be automatically generated to be a unique value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same secret name can run into conflicts when running tests in rapid succession,
    leading to a slow down of the test suite as it retries to create the new secret with
    the conflicting name.

    This fixture will automatically remove the secret when leaving the scope the fixture
    was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a secret can be found in the
    documentation for `create_secret` and `delete_secret`, respectively:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.delete_secret
    """
    secret_list = []

    # We need to have this retry mechanism as there can be errors from trying to delete
    # the same named secret if tests run in rapid succession.
    @retry(
        retry=retry_if_exception_type(
            exception_types=secretsmanager_client.exceptions.InvalidRequestException
        ),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        stop=stop_after_attempt(max_attempt_number=10),
    )
    def _inner(**kwargs):
        """This is a function that passes through to boto3's create_secret method of the
        SecretsManager client, except if a secret name is not passed, it will be
        automatically generated to be a unique value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
        """
        # Add a unique secret name if it is not provided.
        if "Name" not in kwargs:
            kwargs["Name"] = str(uuid.uuid4())

        secret = secretsmanager_client.create_secret(**kwargs)
        secret_list.append(secret)
        return secret

    yield _inner

    # Now remove the test secrets. We force deletion without recovery because these are
    # test secrets so we don't care about the recovery window.
    for secret in secret_list:
        secretsmanager_client.delete_secret(
            SecretId=secret["ARN"], ForceDeleteWithoutRecovery=True
        )


@pytest.fixture
def secretsmanager_poll_for_version_stage_change(secretsmanager_client):
    """This returns a function that can be used to poll for a change in the version
    stage of a given SecretId and VersionId and return the result of describing the
    secret once the state changes.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions to describe a secret can be found in the documentation for
    `describe_secret`:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.describe_secret
    """

    def _inner(secret_id, version_id, from_stage, to_stage, timeout=15):
        """Polls for the version stage label to change from `from_stage` to `to_stage`
        for `timeout` seconds, and returns the `describe_secret` result when it does.

        If the version never changes a built in assertion will fail.
        """
        result = secretsmanager_client.describe_secret(SecretId=secret_id)

        # Make sure the version id is present in the metadata of the secret.
        assert version_id in result["VersionIdsToStages"]
        # Make sure the version id has the from stage label.
        assert from_stage in result["VersionIdsToStages"][version_id]

        # Do an initial check to see if the change has occurred before starting the
        # timer.
        if to_stage in result["VersionIdsToStages"][version_id]:
            return result

        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=timeout, function=lambda: None)

        # Start the timer and poll until the time runs out or the stage label changes.
        timer.start()
        while timer.is_alive():
            time.sleep(1)
            result = secretsmanager_client.describe_secret(SecretId=secret_id)

            if to_stage in result["VersionIdsToStages"][version_id]:
                timer.cancel()
                break

        timer.join()
        # Make sure the change ocurred before transitioning.
        assert to_stage in result["VersionIdsToStages"][version_id]
        return result

    return _inner


@pytest.fixture(scope="session")
def step_functions_client():
    """Returns a boto3 client for AWS Step Functions.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("stepfunctions")


@pytest.fixture
def step_functions_list_executions(step_functions_client):
    """Provides a method to list executions for the given step function ARN. This
    fixture will automatically paginate through the list to get the entire result set.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to use this fixture can be found in the
    documentation for Step Functions API permissions below. Specifically the
    `ListExecutions` permission.
    https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstepfunctions.html
    """

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's
        `list_executions` method of the Step Functions client. This will also paginate
        through the list to get the entire result set.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/list_executions.html
        """
        result = step_functions_client.list_executions(**kwargs)
        # Pop off any nextToken passed in the original kwargs.
        kwargs.pop("nextToken", None)
        # Loop to retrieve all the executions if there are many.
        while result.get("nextToken"):
            next_page = step_functions_client.list_executions(
                NextToken=result["NextToken"], **kwargs
            )
            result["executions"].extend(next_page["executions"])
            result["nextToken"] = next_page["nextToken"]

        return result

    return _inner


@pytest.fixture
def step_functions_stop_executions(
    step_functions_client, step_functions_list_executions
):
    """Returns a function to be used to clean up all running executions of a given state
    machine ARN.

    This state machine must be a standard workflow type, otherwise this fixture will
    fail.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to use this fixture can be found in the
    documentation for Step Functions API permissions below. Specifically the
    `ListExecutions` and `StopExecution` permissions.
    https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstepfunctions.html
    """
    step_function_arns = []

    def _inner(step_function_arn):
        """This function adds the step function ARN to the list of step functions to
        have any running executions stopped at the end of the test session.
        """
        step_function_arns.append(step_function_arn)

    yield _inner

    # Now list and stop all running executions for each step function specified.
    for step_function_arn in step_function_arns:
        executions = step_functions_list_executions(
            stateMachineArn=step_function_arn, statusFilter="RUNNING"
        )
        # For each running execution, stop it.
        for execution in executions["executions"]:
            step_functions_client.stop_execution(
                executionArn=execution["executionArn"],
                cause="Stopping test executions so we can tear down the review step"
                " function.",
            )


@pytest.fixture
def step_functions_poll_for_execution_completion(step_functions_client):
    """Return a function that will wait for the most recent running Step Function
    execution to complete and return the results.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.
    """

    def _inner(state_machine_arn, timeout=300):
        """Waits for the latest execution of the provided state machine ARN to show as
        no longer running and returns the results.

        A timeout in seconds controls how long until this method will give up waiting
        and fail. If one is not passed, this defaults to 300 seconds. This is required
        to allow for lambda cold start times and the long time it takes for the step
        functions API to return the actual results of executions.
        """
        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=timeout, function=lambda: None)

        # Check if the execution is finished already.
        result = step_functions_client.list_executions(
            stateMachineArn=state_machine_arn, statusFilter="RUNNING"
        )

        # Now start the timer and start polling.
        timer.start()
        while not result["executions"] and timer.is_alive():
            time.sleep(0.5)
            result = step_functions_client.list_executions(
                stateMachineArn=state_machine_arn
            )

        timer.cancel()
        # Wait for the timer to stop.
        timer.join()

        # Ensure there are some executions listed.
        assert result["executions"]
        execution_arn = result["executions"][0]["executionArn"]
        result = step_functions_client.describe_execution(executionArn=execution_arn)
        # Now start the timer and start polling for the execution status to change.
        timer = Timer(interval=timeout, function=lambda: None)
        timer.start()
        while result["status"] == "RUNNING" and timer.is_alive():
            time.sleep(0.5)
            result = step_functions_client.describe_execution(
                executionArn=execution_arn
            )

        timer.cancel()
        timer.join()

        # Fail if we got no results.
        assert result["status"] != "RUNNING"

        return result

    return _inner


@pytest.fixture
def step_functions_poll_for_specific_execution_completion(step_functions_client):
    """Return a function that will wait for the given Step Function execution ARN to
    complete and return the results.

    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.
    """

    def _inner(execution_arn, timeout=30):
        """Waits for the provided execution ARN to show as no longer running and returns
        the results.

        A timeout in seconds controls how long until this method will give up waiting
        and fail. If one is not passed, this defaults to 30 seconds. This is required to
        allow for lambda cold start times.
        """
        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=timeout, function=lambda: None)
        result = {}
        # Now start the timer and start polling.
        timer.start()
        while result.get("status", "RUNNING") == "RUNNING" and timer.is_alive():
            time.sleep(0.5)
            with suppress(step_functions_client.exceptions.ExecutionDoesNotExist):
                result = step_functions_client.describe_execution(
                    executionArn=execution_arn
                )

        # Fail if we got no results.
        timer.cancel()
        timer.join()
        assert result.get("status", "RUNNING") != "RUNNING"

        return result

    return _inner


@pytest.fixture
def get_state_definition():
    """Returns a function that returns the requested state from the state machine
    definition in a format suitable for use with the TestState API as specified here:
    https://docs.aws.amazon.com/step-functions/latest/apireference/API_TestState.html

    The state machine definition can be provided either as a dictionary, a string,
    a bytes object, a bytearray, an open file object, or a file path to retrieve the
    JSON from.

    The path to the state definition to pull out is able to be specified using a JSON
    path.
    """

    def _inner(state_machine_definition, state_path):
        """A function that returns the requested state from the state machine definition
        in a format suitable for use with the TestState API as specified here:
        https://docs.aws.amazon.com/step-functions/latest/apireference/API_TestState.html

        The state machine definition can be provided either as a dictionary, a string,
        a bytes object, a bytearray, an open file object, or a file path to retrieve the
        JSON from.

        The path to the state definition to pull out is able to be specified using a
        JSON path.
        """
        json_path = jsonpath_ng.parse(state_path)

        with suppress(json.JSONDecodeError, TypeError, AttributeError):
            parsed_state_machine_definition = json.loads(state_machine_definition)
            return json.dumps(json_path.find(parsed_state_machine_definition)[0].value)

        with suppress(json.JSONDecodeError, TypeError, AttributeError):
            parsed_state_machine_definition = json.load(state_machine_definition)
            return json.dumps(json_path.find(parsed_state_machine_definition)[0].value)

        with open(state_machine_definition, encoding="utf-8") as definition_json_file:
            parsed_state_machine_definition = json.load(definition_json_file)
            return json.dumps(json_path.find(parsed_state_machine_definition)[0].value)

    return _inner


@pytest.fixture(scope="session")
def iam_client():
    """Returns a boto3 client for AWS IAM.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("iam")


@pytest.fixture
def iam_create_role(iam_client):
    """Provides a method to create an IAM role using the provided kwargs and returns
    the result.

    If the role name is not passed, it will be automatically populated with a unique
    value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same name can run into conflicts when running tests in rapid succession, leading
    to a slow down of the test suite as it retries to create the new role with the
    conflicting name.

    This fixture will automatically remove the role(s) when leaving the scope the
    fixture was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a role can be found in the
    documentation for IAM API permissions. Specifically the `CreateRole`,
    `ListRolePolicies`, `DeleteRolePolicy`, and `DeleteRole` permissions.
    https://docs.aws.amazon.com/IAM/latest/UserGuide/access_permissions-required.html
    """
    iam_roles = []

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `create_role`
        method of the IAM client.

        If a role's(s) name is not passed, it will be automatically populated with a
        unique value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_role
        """
        # Add a unique role name if it is not provided.
        if "RoleName" not in kwargs:
            kwargs["RoleName"] = str(uuid.uuid4())

        result = iam_client.create_role(**kwargs)
        iam_roles.append(result)
        return result

    yield _inner

    # Now remove all the policies that were created.
    for role in iam_roles:
        # Remove any attached role policies.
        result = iam_client.list_role_policies(RoleName=role["Role"]["RoleName"])
        role_policy_names = result["PolicyNames"]
        # Paginate through the results if we have to.
        while result.get("Marker"):
            result = iam_client.list_role_policies(
                RoleName=role["Role"]["RoleName"], Marker=result["Marker"]
            )
            role_policy_names.extend(result["PolicyNames"])

        # Now delete all of the role policies.
        for role_policy_name in role_policy_names:
            # Could have been deleted by the put_role_policy fixture as we have little
            # to no control of fixture ordering. So if the role policy no longer exists,
            # we don't worry about it.
            with suppress(iam_client.exceptions.NoSuchEntityException):
                iam_client.delete_role_policy(
                    PolicyName=role_policy_name, RoleName=role["Role"]["RoleName"]
                )

        # Can finally delete the role.
        iam_client.delete_role(RoleName=role["Role"]["RoleName"])


@pytest.fixture
def iam_put_role_policy(iam_client):
    """Provides a method to put an inline policy to an IAM role using the provided
    kwargs and returns the result.

    If the policy name is not passed, it will be automatically populated with a unique
    value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same name can run into conflicts when running tests in rapid succession, leading
    to a slow down of the test suite as it retries to create the new policy with the
    conflicting name.

    This fixture will automatically remove the policy(s) when leaving the scope the
    fixture was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a role can be found in the
    documentation for IAM API permissions. Specifically the `PutRolePolicy` and
    `DeleteRolePolicy` permissions.
    https://docs.aws.amazon.com/IAM/latest/UserGuide/access_permissions-required.html
    """
    iam_policies = []

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `put_role_policy`
        method of the IAM client.

        If a policy(s) name is not passed, it will be automatically populated with a
        unique value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.put_role_policy
        """
        # Add a unique policy name if it is not provided.
        if "PolicyName" not in kwargs:
            kwargs["PolicyName"] = str(uuid.uuid4())

        result = iam_client.put_role_policy(**kwargs)
        iam_policies.append(
            {"RoleName": kwargs["RoleName"], "PolicyName": kwargs["PolicyName"]}
        )
        return result

    yield _inner

    # Now remove all the policies that were created.
    for policy in iam_policies:
        iam_client.delete_role_policy(**policy)


@pytest.fixture(scope="session")
def lambda_client():
    """Return a lambda client for use in the test.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the
    SecretsManager client multiple times.
    """
    return boto3.client("lambda")


@pytest.fixture
def lambda_poll_for_update_status(lambda_client):
    """Returns a method to be used to wait for the update to succeed.

    The updates to the function are not immediate, so this will wait for the updates to
    apply before returning. If the update does not occur before the timeout is reached,
    an assertion error will be raised. The time it waits can be controlled by passing
    the `poll_timeout` parameter to configure the number of seconds to wait. It defaults
    to 30 seconds. Note that because we use Lambda container image support, it takes
    quite a long time to update the function.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """

    def _inner(initial_result, poll_timeout=30):
        """Polls for the status to change to "Successful"."""
        # We need to check if the update is still pending.
        if initial_result["LastUpdateStatus"] == "Successful":
            return initial_result

        # If it's not successful, ensure it is not failed.
        if initial_result["LastUpdateStatus"] == "Failed":
            raise ValueError(
                "Unable to update function configuration with reason"
                f" {initial_result['LastUpdateStatusReason']} and reason code"
                f" {initial_result['LastUpdateStatusReasonCode']}"
            )

        # Otherwise it is still pending, so poll for it to be ready.
        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=poll_timeout, function=lambda: None)

        # Start the timer and poll until the time runs out or the stage label changes.
        timer.start()
        while timer.is_alive():
            time.sleep(1)
            result = lambda_client.get_function_configuration(
                FunctionName=initial_result["FunctionName"]
            )

            if result["LastUpdateStatus"] == "Successful":
                timer.cancel()
                break

        # Make sure the update stuck before returning.
        timer.join()
        assert result["LastUpdateStatus"] == "Successful"
        return result

    return _inner


@pytest.fixture
def lambda_poll_for_active_status(lambda_client):
    """Returns a method to be used to wait for the lambda to become active.

    The the function becoming active after publish is not immediate, especially when
    snap start is enabled. If the function does not become active before the timeout is
    reached, an assertion error will be raised. The time it waits can be controlled by
    passing the `poll_timeout` parameter to configure the number of seconds to wait. It
    defaults to 120 seconds.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """

    def _inner(initial_result, poll_timeout=120):
        """Polls for the status to change to "Active"."""
        # We need to check if the state is already active.
        if initial_result["State"] == "Active":
            return initial_result

        # If it's not successful, ensure it is not failed.
        assert initial_result["State"] != "Failed", (
            f"Function was not active with reason {initial_result['StateReason']} and"
            f" reason code {initial_result['StateReasonCode']}"
        )

        # Otherwise it is still pending, so poll for it to be ready.
        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=poll_timeout, function=lambda: None)

        # Start the timer and poll until the time runs out or the stage label changes.
        timer.start()
        while timer.is_alive():
            time.sleep(1)
            result = lambda_client.get_function_configuration(
                FunctionName=initial_result["FunctionName"],
                Qualifier=initial_result["Version"],
            )

            if result["State"] == "Active":
                timer.cancel()
                break

        # Make sure the update stuck before returning.
        timer.join()
        assert result["State"] == "Active", (
            f"Function was not active with reason {result['StateReason']} and reason"
            f" code {result['StateReasonCode']}"
        )
        return result

    return _inner


@pytest.fixture
def lambda_update_function_configuration_and_publish(
    lambda_client, lambda_poll_for_update_status, lambda_poll_for_active_status
):
    """This fixture provides a function to update a lambda function's configuration and
    publish a new version with those changes. The function will pass the arguments
    through to the boto3 lambda client's `update_function_configuration` method, publish
    a new version, and returns the version number of the new published version.

    The updates to the function are not immediate, so this will wait for the updates to
    apply before returning. If the update does not occur before the timeout is reached,
    an assertion error will be raised. The time it waits can be controlled by passing
    the `poll_timeout` parameter to configure the number of seconds to wait. It defaults
    to 30 seconds. Note that because we use Lambda container image support, it takes
    quite a long time to update the function.

    This fixture will delete the created function versions after the test is completed.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """
    created_test_versions = []

    def _inner(poll_timeout=120, **kwargs):
        """This function will pass the values through to the boto3 lambda client's
        `update_function_configuration` method.

        For a description of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.update_function_configuration
        """

        result = lambda_client.update_function_configuration(**kwargs)
        # We need to check if the update is still pending.
        result = lambda_poll_for_update_status(
            initial_result=result, poll_timeout=poll_timeout
        )

        # Now that it is updated, publish a new version.
        result = lambda_client.publish_version(
            FunctionName=result["FunctionArn"], RevisionId=result["RevisionId"]
        )
        # Append the result now because we will want to delete if even if we fail to
        # have it go active.
        created_test_versions.append(result)

        # Now wait for the lambda to go active.
        result = lambda_poll_for_active_status(
            initial_result=result, poll_timeout=poll_timeout
        )

        return result["Version"]

    yield _inner

    # Now delete the test versions.
    for version in created_test_versions:
        lambda_client.delete_function(
            FunctionName=version["FunctionArn"], Qualifier=version["Version"]
        )


@pytest.fixture(scope="session")
def sts_client():
    """Returns a boto3 client for STS.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("sts")


@pytest.fixture(scope="session")
def s3_client():
    """Returns a boto3 client for S3.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("s3")


@pytest.fixture
def upload_file(s3_client):
    """This fixture provides a function that can be used to upload a file to S3. This
    file will be removed from the S3 bucket after the test completes.

    The arguments to this function are the same as the arguments to the `upload_file`
    method of the S3 client documented here:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/upload_file.html#upload-file

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The credentials used must have the correct permissions to upload and delete objects
    from the S3 bucket that the file will be uploaded to.
    """
    uploaded_files = []

    def _inner(*args, **kwargs):

        if len(args) >= 3:
            uploaded_files.append((args[1], args[2]))
        elif len(args) == 2:
            uploaded_files.append((args[1], kwargs["Key"]))
        else:
            uploaded_files.append((kwargs["Bucket"], kwargs["Key"]))

        s3_client.upload_file(*args, **kwargs)

    yield _inner

    # Now remove the uploaded files.
    for bucket, key in uploaded_files:
        s3_client.delete_object(Bucket=bucket, Key=key)


def upload_fileobj(s3_client):
    """This fixture provides a function that can be used to upload the contents of an
    already opened binary file to S3. This file will be removed from the S3 bucket after
    the test completes.

    The arguments to this function are the same as the arguments to the `upload_fileobj`
    method of the S3 client documented here:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/upload_fileobj.html#upload-fileobj

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The credentials used must have the correct permissions to upload and delete objects
    from the S3 bucket that the file will be uploaded to.
    """
    uploaded_files = []

    def _inner(*args, **kwargs):

        if len(args) >= 3:
            uploaded_files.append((args[1], args[2]))
        elif len(args) == 2:
            uploaded_files.append((args[1], kwargs["Key"]))
        else:
            uploaded_files.append((kwargs["Bucket"], kwargs["Key"]))

        s3_client.upload_fileobj(*args, **kwargs)

    yield _inner

    # Now remove the uploaded files.
    for bucket, key in uploaded_files:
        s3_client.delete_object(Bucket=bucket, Key=key)


@pytest.fixture(scope="session")
def appsync_client():
    """Returns a boto3 client for AWS AppSync.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("appsync")


@pytest.fixture
def appsync_mock_context():
    """This returns a function that can be used to generate a mock context with
    placeholders for any unspecified elements.

    This mimics the behavior of EvaluateCode, where it fills in placeholder values for
    keys if not specified in the mock context, so that any assertion done on the
    contents of the mock_context match the results returned from EvaluateCode.

    EvaluateCode is documented here:
    https://docs.aws.amazon.com/appsync/latest/APIReference/API_EvaluateCode.html
    """

    def _inner(partial_context):
        """This is a function that can be used to generate a mock context with
        placeholders for any unspecified elements.

        This mimics the behavior of EvaluateCode, where it fills in placeholder values
        for keys if not specified in the mock context, so that any assertion done on the
        contents of the mock_context match the results returned from EvaluateCode.

        EvaluateCode is documented here:
        https://docs.aws.amazon.com/appsync/latest/APIReference/API_EvaluateCode.html
        """
        defaults = {
            "identity": None,
            "result": None,
            "request": None,
            "info": {
                "fieldName": "",
                "parentTypeName": "",
                "variables": {},
                "selectionSetList": [],
                "selectionSetGraphQL": "",
            },
            "env": None,
            "error": None,
            "prev": None,
            "stash": {},
            "outErrors": [],
            "arguments": None,
            "args": None,
            "source": None,
        }
        return {**defaults, **partial_context}

    return _inner


@pytest.fixture(scope="session")
def dynamodb_client():
    """Returns a boto3 client for AWS DynamoDB.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If credentials are not found, or any other configuration error occurs, the test
    requesting this fixture will likely fail.

    This fixture is session scoped as the AWS credentials are not expected to change
    during the session, so we can save time by not needing to re-instantiate the client
    multiple times.
    """
    return boto3.client("dynamodb")


@pytest.fixture
def dynamodb_poll_for_active_status(dynamodb_client):
    """Returns a method to be used to wait for the table to become active.

    The table is not immediately ready for work, so this will wait for the table status
    to become ACTIVE before returning. If the status does not change before the timeout
    is reached, an assertion error will be raised. The time it waits can be controlled
    by passing the `poll_timeout` parameter to configure the number of seconds to wait.
    It defaults to 30 seconds.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """

    def _inner(initial_result, poll_timeout=30):
        """Polls for the status to change to "ACTIVE"."""
        # Since the response for `DescribeTable` is nested under the "Table" key, but
        # the response for `CreateTable` is nested under the "TableDescription" key, we
        # need to check for both.
        table = initial_result.get("Table") or initial_result.get("TableDescription")

        # We need to check if the update is still in progress.
        if table["TableStatus"] == "ACTIVE":
            return table

        # If it's not successful, ensure it is not an unexpected state.
        assert table["TableStatus"] not in (
            "DELETING",
            "INACCESSIBLE_ENCRYPTION_CREDENTIALS",
            "ARCHIVING",
            "ARCHIVED",
        )

        # Otherwise it is still pending, so poll for it to be ready.
        # Set up a timer for the specified timeout. We use a dummy lambda for the
        # function argument because we are only using it to check if we've hit the
        # timeout.
        timer = Timer(interval=poll_timeout, function=lambda: None)

        # Start the timer and poll until the time runs out or the stage label changes.
        timer.start()
        while timer.is_alive():
            time.sleep(1)
            result = dynamodb_client.describe_table(TableName=table["TableName"])

            if result["Table"]["TableStatus"] == "ACTIVE":
                timer.cancel()
                break

        # Make sure the update stuck before returning.
        timer.join()
        assert result["Table"]["TableStatus"] == "ACTIVE"
        return result

    return _inner


@pytest.fixture
def dynamodb_delete_table(dynamodb_client):
    """Provides a method to delete a test DynamoDB table using the provided kwargs.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a table can be found in the
    documentation for DynamoDB API permissions. Specifically the `DeleteTable`
    permission.
    https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html
    """

    @retry(
        retry=retry_if_exception_type(
            exception_types=dynamodb_client.exceptions.ResourceInUseException
        ),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        stop=stop_after_attempt(max_attempt_number=10),
    )
    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `delete_table`
        method of the DynamoDB client.

        This will suppress ResourceNotFound errors and retry ResourceInUse errors.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/delete_table.html
        """
        with suppress(dynamodb_client.exceptions.ResourceNotFoundException):
            dynamodb_client.delete_table(**kwargs)

    return _inner


@pytest.fixture
def dynamodb_create_table(
    dynamodb_client, dynamodb_poll_for_active_status, dynamodb_delete_table
):
    """Provides a method to create a test DynamoDB table using the provided kwargs,
    waits for the table to go ACTIVE, and returns the result.

    If the table name is not passed, it will be automatically populated with a unique
    value.

    It is recommended to let the name be automatically generated. Otherwise re-use of
    the same table name can run into conflicts when running tests in rapid succession,
    leading to a slow down of the test suite as it retries to create the new table with
    the conflicting name.

    This fixture will automatically remove the table when leaving the scope the fixture
    was used within.

    Usage of this fixture requires that the credentials be configured for boto3 via one
    of the following documented methods that does not involve setting the credentials on
    the client or session objects:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    The minimum permissions required to create and delete a table can be found in the
    documentation for DynamoDB API permissions. Specifically the `CreateTable`,
    `DeleteTable`, and `DescribeTable` permissions.
    https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html
    """
    tables = []

    def _inner(**kwargs):
        """This is a function that passes arguments through to boto3's `create_table`
        method of the DynamoDB client.

        If a table name is not passed, it will be automatically populated with a unique
        value.

        For descriptions of the arguments see:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html
        """
        # Add a unique rule name if it is not provided.
        if "TableName" not in kwargs:
            kwargs["TableName"] = str(uuid.uuid4())

        table = dynamodb_client.create_table(**kwargs)
        dynamodb_poll_for_active_status(initial_result=table)
        tables.append(table)
        return table

    yield _inner

    # Now remove the tables, ignoring any not found exceptions.
    for table in tables:
        dynamodb_delete_table(TableName=table["TableDescription"]["TableName"])
