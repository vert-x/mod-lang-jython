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
from testtools import Test, Assert
from core.event_bus import EventBus

print "in test"

class DeployTest(object):

    def test_deploy(self):

        def handler(message):
            if message.body == "started":
                Test.complete()
        EventBus.register_handler("test-handler", False, handler)
        conf = {'foo' : 'bar'}
        def deploy_handler(err, ok):
            Assert.none(err)

        vertx.deploy_verticle("core/deploy/child.py", conf, 1, deploy_handler)

    def test_undeploy(self):
        print "in test undeploy"
        def handler(message):
            return

        EventBus.register_handler("test-handler", False, handler)

        conf = {'foo' : 'bar'}

        def undeploy_handler(err):
            Assert.none(err)
            Test.complete()

        def deploy_handler(err, id):
            Assert.none(err)
            vertx.undeploy_verticle(id, handler=undeploy_handler)

        vertx.deploy_verticle("core/deploy/child.py", conf, handler=deploy_handler)

    def test_deploy2(self):

        def deploy_handler(err, id):

            Assert.none(err)
            Assert.not_none(id)

            def undeploy_handler(err):
                Assert.none(err)
                Test.complete()

            vertx.undeploy_verticle(id, handler=undeploy_handler)

        vertx.deploy_verticle("core/deploy/child2.py", handler=deploy_handler)

    def test_deploy_fail(self):

        def deploy_handler(err, id):
            Assert.not_none(err)
            Assert.none(id)
            Test.complete()

        vertx.deploy_verticle("core/deploy/notexists.py", handler=deploy_handler)

    def test_undeploy_fail(self):

        def undeploy_handler(err):
            Assert.not_none(err)
            Test.complete()

        vertx.undeploy_verticle("qijdqwijd", handler=undeploy_handler)

Test.run(DeployTest())
