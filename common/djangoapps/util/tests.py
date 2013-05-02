""" Tests for utility app """

from django.test import TestCase
from django.core.cache import get_cache
from .memcache import safe_key


class MemcacheTest(TestCase):
    """ Test memcache key cleanup """

    def setUp(self):
        """ Choose a cache to test """
        self.cache = get_cache('default')

    def test_safe_key(self):

        key = safe_key('test', 'prefix', 'version')
        self.assertEqual(key, 'prefix:version:test')

    def test_safe_key_long(self):

        # Choose lengths close to memcached's cutoff (250)
        for length in [248, 249, 250, 251, 252]:

            # Generate a key of that length
            key = 'a' * length

            # Make the key safe
            key = safe_key(key, '', '')

            # The key should now be valid
            self.assertTrue(self._is_valid_key(key),
                            msg="Failed for key length {0}".format(length))

    def test_safe_key_unicode(self):

        # Try all UTF-16 characters
        for unicode_char in range(0, 2**16):

            # Generate a key with that character
            key = unichr(unicode_char)

            # Make the key safe
            key = safe_key(key, '', '')

            # The key should now be valid
            self.assertTrue(self._is_valid_key(key),
                            msg="Failed for unicode character {0}".format(unicode_char))

    def test_safe_key_prefix_unicode(self):
        # Try all UTF-16 characters
        for unicode_char in range(0, 2**16):

            # Generate a prefix with that character
            prefix = unichr(unicode_char)

            # Make the key safe
            key = safe_key('test', prefix, '')

            # The key should now be valid
            self.assertTrue(self._is_valid_key(key),
                            msg="Failed for unicode character {0}".format(unicode_char))

    def test_safe_key_version_unicode(self):

        # Try all UTF-16 characters
        for unicode_char in range(0, 2**16):

            # Generate a version with that character
            version = unichr(unicode_char)

            # Make the key safe
            key = safe_key('test', '', version)

            # The key should now be valid
            self.assertTrue(self._is_valid_key(key),
                            msg="Failed for unicode character {0}".format(unicode_char))


    def _is_valid_key(self, key):
        """ Test that a key is memcache-compatible.
        Based on Django's validator in core.cache.backends.base"""

        # Check the length
        if len(key) > 250:
            return False

        # Check that there are no spaces or control characters
        for char in key:
            if ord(char) < 33 or ord(char) == 127:
                return False

        return True
