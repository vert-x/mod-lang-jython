# Copyright 2011-2012 the original author or authors.
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

import vertx
from test_utils import TestUtils

tu = TestUtils()
tu.check_thread()
dns = vertx.create_dns_client(('127.0.0.1',53530))
logger = vertx.logger()

# This is just a basic test. Most testing occurs in the Java tests
class HttpTest(object):
    def test_resolve_a(self):
        tu.test_complete()

    def test_resolve_aaaa(self):
        tu.test_complete()

    def test_resolve_mx(self):
        tu.test_complete()

    def test_resolve_txt(self):
        tu.test_complete()

    def test_resolve_ns(self):
        tu.test_complete()

    def test_resolve_cname(self):
        tu.test_complete()

    def test_resolve_ptr(self):
        tu.test_complete()

    def test_resolve_srv(self):
        tu.test_complete()

    def test_lookup_6(self):
        tu.test_complete()

    def test_lookup_4(self):
        tu.test_complete()

    def test_lookup(self):
        tu.test_complete()


    def vertx_stop():
        tu.check_thread()
        tu.unregister_all()
        tu.app_stopped()


tu.register_all(HttpTest())
tu.app_ready()
