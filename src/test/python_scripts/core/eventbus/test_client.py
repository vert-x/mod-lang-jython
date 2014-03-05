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
from core.event_bus import EventBus, ReplyError

tu = TestUtils()

tu.check_thread()

class EventBusTest(object):
    def test_simple_send(self):
        json = {'message' : 'hello world!'}
        address = "some-address"

        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            EventBus.unregister_handler(id)
            tu.test_complete()
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)
        EventBus.send(address, json)

    def test_send_empty(self):
        json = {}
        address = "some-address"
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body == {})
            EventBus.unregister_handler(id)
            tu.test_complete()
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)
        EventBus.send(address, json)

    def test_reply(self):
        json = {'message' : 'hello world!'}
        address = "some-address"
        reply = {'cheese' : 'stilton!'}
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            msg.reply(reply)
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)

        def reply_handler(msg):
            tu.azzert(msg.body['cheese'] == reply['cheese'])
            EventBus.unregister_handler(id)
            tu.test_complete()
        EventBus.send(address, json, reply_handler)

    def test_handler_decorator(self):
        json = {'message': 'hello world!'}
        address = 'some-address'
        reply = {'cheese': 'stilton!'}
        @EventBus.handler(address)
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            msg.reply(reply)

        def reply_handler(msg):
            tu.azzert(msg.body['cheese'] == reply['cheese'])
            tu.test_complete()    
        EventBus.send(address, json, reply_handler)

    def test_reply_with_timeout(self):
        json = {'message': 'hello world!'}
        address = 'some-address'
        reply = {'cheese': 'stilton!'}
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            msg.reply(reply)
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)

        def reply_handler(error, msg):
            tu.azzert(error == None)
            tu.azzert(msg.body['cheese'] == reply['cheese'])
            EventBus.unregister_handler(id)
            tu.test_complete()
        EventBus.send_with_timeout(address, json, 10000, reply_handler)

    def test_reply_timeout(self):
        json = {'message': 'hello world!'}
        address = 'some-address'
        reply = {'cheese': 'stilton!'}
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)

        def reply_handler(error, msg):
            tu.azzert(error != None)
            tu.azzert(isinstance(error, ReplyError))
            tu.azzert(error.type == ReplyError.TIMEOUT)
            EventBus.unregister_handler(id)
            tu.test_complete()
        EventBus.send_with_timeout(address, json, 10, reply_handler)

    def test_default_reply_timeout(self):
        EventBus.default_reply_timeout = 10000
        tu.azzert(EventBus.default_reply_timeout == 10000)
        EventBus.default_reply_timeout = 30000
        tu.azzert(EventBus.default_reply_timeout == 30000)
        tu.test_complete()

    def test_empty_reply(self):
        json = {'message' : 'hello world!'}
        address = "some-address"
        reply = {}
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            msg.reply(reply)

        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)

        def reply_handler(msg):
            tu.azzert(msg.body == {})
            EventBus.unregister_handler(id)
            tu.test_complete()
        EventBus.send(address, json, reply_handler)

    def test_send_unregister_send(self):

        json = {'message' : 'hello world!'}
        address = "some-address"
        self.received = False

        def handler(msg):
            if self.received:
                tu.azzert(False, "handler already called") 
            tu.azzert(msg.address == address)
            tu.azzert(msg.body['message'] == json['message'])
            EventBus.unregister_handler(id)
            self.received = True

            def timer_complete(id):
                tu.test_complete()
            
            # End test on a timer to give time for other messages to arrive
            vertx.set_timer(100, timer_complete)
        id = EventBus.register_handler(address, handler=handler)
        tu.azzert(id != None)

        for i in range(0,2):
            EventBus.send(address, json)

    def test_send_multiple_matching_handlers(self):
        json = {'message' : 'hello world!'}
        address = "some-address"
        num_handlers = 10
        count = [0] # use an array to ensure pass by ref

        for i in range(0,num_handlers):
            class Handler(object):
                def __init__(self, count):
                    self.count = count
                def handler_func(self, msg):
                    tu.azzert(msg.address == address)
                    tu.azzert(msg.body['message'] == json['message'])
                    EventBus.unregister_handler(self.id)
                    self.count[0] += 1
                    if self.count[0] == num_handlers:
                        tu.test_complete()
            handler = Handler(count)
            handler.id = EventBus.register_handler(address, handler=handler.handler_func)
        EventBus.publish(address, json)

    def test_echo_string(self):
        self.echo("foo")


    def test_echo_fixnum(self):
        self.echo(12345)

    def test_echo_float(self):
        self.echo(1.2345)

    def test_echo_boolean_true(self):
        self.echo(True)

    def test_echo_boolean_false(self):
        self.echo(False)

    def test_echo_json(self):
        json = {"foo" : "bar", "x" : 1234, "y" : 3.45355, "z" : True, "a" : False}
        self.echo(json)

    def echo(self, msg):
        address = "some-address"
        class Handler(object):
            def handler_func(self, received):
                tu.check_thread()
                EventBus.unregister_handler(self.id)
                tu.azzert(received.address == address)
                received.reply(received.body)
        handler = Handler()
        handler.id = EventBus.register_handler(address, handler=handler.handler_func)
        
        def reply_handler(reply):
            if isinstance(reply.body, dict):
                for k,v in reply.body.iteritems():
                    tu.azzert(msg[k] == v)
            else:
                tu.azzert(msg == reply.body)
            tu.test_complete()
        EventBus.send(address, msg, reply_handler)

    def test_reply_of_reply_of_reply(self):
        address = "some-address"
        def handler(msg):
            tu.azzert(msg.address == address)
            tu.azzert("message" == msg.body)
            def reply_handler1(reply):
                tu.azzert("reply-of-reply" == reply.body)
                reply.reply("reply-of-reply-of-reply")  
            msg.reply("reply", reply_handler1)
          
        id = EventBus.register_handler(address, handler=handler)

        def reply_handler2(reply):
            tu.azzert("reply" == reply.body)
            def reply_handler3(reply2):
                tu.azzert("reply-of-reply-of-reply" == reply2.body)
                EventBus.unregister_handler(id)
                tu.test_complete()
            reply.reply("reply-of-reply", reply_handler3)
          
        EventBus.send(address, "message", reply_handler2)

def vertx_stop():
    tu.check_thread()
    tu.unregister_all()
    tu.app_stopped()

tu.register_all(EventBusTest())
tu.app_ready()
