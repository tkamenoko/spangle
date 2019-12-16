try:
    from unittest import IsolatedAsyncioTestCase as _Case
except ImportError:
    from unittest import TestCase as _Case
