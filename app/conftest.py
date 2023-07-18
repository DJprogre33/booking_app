import os
from unittest import mock

# Enable the test mode for working with the database
os.environ["MODE"] = "TEST"

# Disable caching
mock.patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()

