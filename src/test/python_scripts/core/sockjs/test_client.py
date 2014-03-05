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
from core.sock_js import SockJSSocket
from core.handlers import AsyncHandler
from test_utils import TestUtils

tu = TestUtils()

class SockJSTest(object):

    def test_socket_created_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.socket_created_handler
        def handler(socket):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.test_complete()

        bridge.hook.handleSocketCreated(None)

    def test_socket_closed_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.socket_closed_handler
        def handler(socket):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.test_complete()

        bridge.hook.handleSocketClosed(None)

    def test_send_or_pub_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.send_or_pub_handler
        def handler(socket, send, message, address):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.azzert(send == True)
            tu.azzert(message['foo'] == 'bar')
            tu.azzert(address == 'some-address')
            tu.test_complete()

        bridge.hook.handleSendOrPub(None, True, {'foo': 'bar'}, 'some-address')

    def test_pre_register_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.pre_register_handler
        def handler(socket, address):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.azzert(address == 'some-address')
            tu.test_complete()

        bridge.hook.handlePreRegister(None, 'some-address')

    def test_post_register_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.post_register_handler
        def handler(socket, address):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.azzert(address == 'some-address')
            tu.test_complete()

        bridge.hook.handlePostRegister(None, 'some-address')

    def test_unregister_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.unregister_handler
        def handler(socket, address):
            tu.azzert(isinstance(socket, SockJSSocket))
            tu.azzert(address == 'some-address')
            tu.test_complete()

        bridge.hook.handleUnregister(None, 'some-address')

    def test_authorise_hook(self):
        server = vertx.create_sockjs_server(vertx.create_http_server())
        bridge = server.bridge({'prefix': '/eventbus'}, [], [])

        @bridge.authorise_handler
        def handler(message, session_id, handler):
            tu.azzert(message['foo'] == 'bar')
            tu.azzert(session_id == 'some-id')
            handler(True)

        def done_handler(error, result):
            tu.azzert(error is None)
            tu.azzert(result)
            tu.test_complete()
        bridge.hook.handleAuthorise({'foo': 'bar'}, 'some-id', AsyncHandler(done_handler))

def vertx_stop():
  tu.unregister_all()
  tu.app_stopped()

tu.register_all(SockJSTest())
tu.app_ready()
