#!/usr/bin/env python3

import sys
import unittest
from tests.mobile_album_test import AlbumTest


if __name__ == '__main__':
    suite = unittest.TestSuite((
        unittest.makeSuite(AlbumTest),
    ))
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
