# Pytest AWS fixtures

This is a collection of fixtures we've been using to perform integration tests using
real AWS services.

Usage of any of these fixture requires that the credentials be configured for boto3 via
one of the following documented methods that does not involve setting the credentials on
the client or session objects:

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

The fixtures themselves are heavily documented so please view their docstrings for more
information on their usage.
