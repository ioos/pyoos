#!/usr/bin/env python

import unittest

# First, discover all tests in the project
loader = unittest.TestLoader()
tests = loader.discover('./pyoos/test')

# Create a runner and run those tests.
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)