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
from core.buffer import Buffer

server = vertx.create_http_server()
client = vertx.create_http_client()
client.port = 8080

class WebsocketTest(object):
    def test_echo_binary(self):
        self.echo(True)

    def test_echo_text(self):
        self.echo(False)

    def echo(self, binary):
        @server.websocket_handler
        def websocket_handler(ws):
            @ws.data_handler
            def data_handler(buff):
                ws.write(buff)

        if binary:
            self.buff = TestUtils.gen_buffer(1000)
        else:
            self.str_ = TestUtils.random_unicode_string(1000)

        def connect_handler(ws):
            received = Buffer.create()

            @ws.data_handler
            def data_handler(buff):
                received.append_buffer(buff)
                if received.length == buff.length:
                    Assert.true(TestUtils.buffers_equal(buff, received))
                    Test.complete()
        
            if binary:
                ws.write_binary_frame(self.buff)
            else:
                ws.write_text_frame(self.str_)

        def listen_handler(err, serv):
            Assert.none(err)
            Assert.equals(serv, server)
            client.connect_web_socket("/someurl", connect_handler)

        server.listen(8080, "0.0.0.0", listen_handler)


    def test_write_from_connect_handler(self):
        @server.websocket_handler
        def websocket_handler(ws):
            ws.write_text_frame("foo")
  

        def connect_handler(ws):
            @ws.data_handler
            def data_handler(buff):
                Assert.equals("foo", buff.to_string())
                Test.complete()

        def listen_handler(err, serv):
            Assert.none(err)
            Assert.equals(serv, server)
            client.connect_web_socket("/someurl", connect_handler)

        server.listen(8080, "0.0.0.0", listen_handler)

    def test_close(self):
        @server.websocket_handler
        def websocket_handler(ws):
            @ws.data_handler
            def data_handler(buff):
                ws.close()
    
        def connect_handler(ws):
            @ws.close_handler
            def close_handler():
                Test.complete()
            ws.write_text_frame("foo")

        def listen_handler(err, serv):
            Assert.none(err)
            Assert.equals(serv, server)
            client.connect_web_socket("/someurl",connect_handler)

        server.listen(8080, "0.0.0.0", listen_handler)


    def test_close_from_connect(self):
        @server.websocket_handler
        def websocket_handler(ws):
            ws.close()

        def connect_handler(ws):
            @ws.close_handler
            def close_handler():
                Test.complete()

        def listen_handler(err, serv):
            Assert.none(err)
            Assert.equals(serv, server)
            client.connect_web_socket("/someurl", connect_handler)

        server.listen(8080, "0.0.0.0", listen_handler)


def vertx_stop():
    client.close()
    server.close()

Test.run(WebsocketTest())
