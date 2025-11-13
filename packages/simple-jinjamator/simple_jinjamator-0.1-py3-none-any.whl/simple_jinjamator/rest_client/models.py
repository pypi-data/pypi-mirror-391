from collections import namedtuple

Request = namedtuple(
    "Request",
    ["url", "method", "params", "body", "headers", "timeout", "ssl_verify","files", "kwargs"],
)
Response = namedtuple(
    "Response", ["url", "method", "body", "headers", "status_code", "client_response"]
)
