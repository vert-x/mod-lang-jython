# Copyright 2011 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module provides test tools for Vert.x Python applications.
"""

import org.vertx.java.platform.impl.JythonVerticleFactory.vertx
import org.vertx.java.platform.impl.JythonVerticleFactory.container
import org.vertx.testtools.VertxAssert
from core.javautils import map_from_java, map_to_java

def run_test(test):
    """Runs a Python test."""
    org.vertx.testtools.VertxAssert.initialize(org.vertx.java.platform.impl.JythonVerticleFactory.vertx)
    method = org.vertx.java.platform.impl.JythonVerticleFactory.container.config().getString('methodName')
    getattr(test, method)()

class Test(object):
    """
    Static test helper methods.
    """
    @staticmethod
    def run(test):
        """Runs a test."""
        run_test(test)

    @staticmethod
    def complete():
        """Completes a test."""
        org.vertx.testtools.VertxAssert.testComplete()

class Assert(object):
    """
    Static assertion methods.
    """
    @staticmethod
    def true(condition, message=None):
        """Asserts that an expression is true."""
        if message is not None:
            org.vertx.testtools.VertxAssert.assertTrue(message, condition)
        else:
            org.vertx.testtools.VertxAssert.assertTrue(condition)

    @staticmethod
    def false(condition, message=None):
        """Asserts that an expression is false."""
        if message is not None:
            org.vertx.testtools.VertxAssert.assertFalse(message, condition)
        else:
            org.vertx.testtools.VertxAssert.assertFalse(condition)

    @staticmethod
    def equals(expected, actual, message=None):
        """Asserts that two values are equal."""
        if message is not None:
            org.vertx.testtools.VertxAssert.assertEquals(message, map_to_java(expected), map_to_java(actual))
        else:
            org.vertx.testtools.VertxAssert.assertEquals(map_to_java(expected), map_to_java(actual))

    @staticmethod
    def same(expected, actual, message=None):
        """Asserts that two values are the same."""
        if message is not None:
          org.vertx.testtools.VertxAssert.assertTrue(message, expected == actual)
        else:
          org.vertx.testtools.VertxAssert.assertTrue(expected == actual)

    @staticmethod
    def none(value, message=None):
        """Asserts that a value is null."""
        if message is not None:
            org.vertx.testtools.VertxAssert.assertNull(message, value)
        else:
            org.vertx.testtools.VertxAssert.assertNull(value)

    @staticmethod
    def not_none(value, message=None):
        """Asserts that a value is not null."""
        if message is not None:
            org.vertx.testtools.VertxAssert.assertNotNull(message, value)
        else:
            org.vertx.testtools.VertxAssert.assertNotNull(value)
