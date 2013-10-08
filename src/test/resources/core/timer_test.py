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

class TimerTest(object):
    def test_one_off(self):
        def handler(timer_id):
            Test.complete()
        vertx.set_timer(10, handler)

    def test_periodic(self):
        fires = 10
        self.count = 0
        def handler(timer_id):
            self.count += 1
            if self.count == fires:
                vertx.cancel_timer(timer_id)
                # End test in another timer in case the first timer fires again - we want to catch that
                def complete(timer_id):
                    Test.complete()            
                vertx.set_timer(100, complete)
            elif self.count > fires:
                Assert.true(false, message='Fired too many times')
        vertx.set_periodic(10, handler)

Test.run(TimerTest())
