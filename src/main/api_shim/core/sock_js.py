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

import core.streams
import core.ssl_support
import org.vertx.java.core
import org.vertx.java.core.sockjs.EventBusBridgeHook
import org.vertx.java.core.impl.DefaultFutureResult
import org.vertx.java.core.json.JsonObject
import org.vertx.java.core.json.JsonArray
import org.vertx.java.platform.impl.JythonVerticleFactory

from core.handlers import AsyncHandler
from core.javautils import map_from_java, map_to_java
from core.event_bus import EventBus

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

class SockJSServer(object):
    """This is an implementation of the server side part of https://github.com/sockjs

    SockJS enables browsers to communicate with the server using a simple WebSocket-like api for sending
    and receiving messages. Under the bonnet SockJS chooses to use one of several protocols depending on browser
    capabilities and what apppears to be working across the network.

    Available protocols include:

    WebSockets
    xhr-polling
    xhr-streaming
    json-polling
    event-source
    html-file

    This means, it should just work irrespective of what browser is being used, and whether there are nasty
    things like proxies and load balancers between the client and the server.

    For more detailed information on SockJS, see their website.

    On the server side, you interact using instances of SockJSSocket - this allows you to send data to the
    client or receive data via the ReadStream data_handler.

    You can register multiple applications with the same SockJSServer, each using different path prefixes, each
    application will have its own handler, and configuration is described in a Hash.
    """

    def __init__(self, http_server):
      self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createSockJSServer(http_server._to_java_server())

    def install_app(self, config, handler):
        """Install an application

        Keyword arguments:
        @param config: Configuration for the application
        @param proc: Proc representing the handler
        @param handler: Handler to call when a new SockJSSocket is created
        """
        java_config = org.vertx.java.core.json.JsonObject(map_to_java(config))
        self.java_obj.installApp(java_config, SockJSSocketHandler(handler))

    def bridge(self, config, inbound_permitted, outbound_permitted, auth_timeout=5*60*1000, auth_address=None):
        return self.bridge_with_config(config, inbound_permitted, outbound_permitted, {"auth_timeout": auth_timeout, "auth_address": auth_address})
        
    def bridge_with_config(self, config, inbound_permitted, outbound_permitted, bridge_config):
        a_ijson = org.vertx.java.core.json.JsonArray(map_to_java(inbound_permitted))
        a_ojson = org.vertx.java.core.json.JsonArray(map_to_java(outbound_permitted))
        self.java_obj.bridge(org.vertx.java.core.json.JsonObject(map_to_java(config)), a_ijson, a_ojson, org.vertx.java.core.json.JsonObject(map_to_java(bridge_config)))
        hook = _EventBusBridgeHook()
        self.java_obj.setHook(hook)
        return EventBusBridge(hook)

class SockJSSocket(core.streams.ReadStream, core.streams.WriteStream):
    """You interact with SockJS clients through instances of SockJS socket.
    The API is very similar to WebSocket. It implements both
    ReadStream and WriteStream so it can be used with Pump to enable
    flow control.
    """
    
    def __init__(self, java_sock):
        self.java_obj = java_sock
        self.remote_addr = None
        self.local_addr = None

        def simple_handler(msg):
            self.write(msg.body)

        self.handler_id = EventBus.register_simple_handler(True, simple_handler)

    def close(self):
        """Close the socket"""
        EventBus.unregister_handler(self.handler_id)
        self.java_obj.close()

    def handler_id(self):
        """When a SockJSSocket is created it automatically registers an event handler with the system, the ID of that
        handler is given by handler_id.
        Given this ID, a different event loop can send a buffer to that event handler using the event bus. This
        allows you to write data to other SockJSSockets which are owned by different event loops.
        """
        return self.handler_id
        
    @property
    def remote_address(self):
        """Returns the remote address as tuple in form of ('ipaddress', port)"""
        if self.remote_addr is None:
            self.remote_addr =  self.java_obj.remoteAddress().getAddress().getHostAddress() , self.java_obj.remoteAddress().getPort();
        return self.remote_addr

    @property
    def local_address(self):
        """Returns the local address as tuple in form of ('ipaddress', port)"""
        if self.local_addr is None:
            self.local_addr =  self.java_obj.localAddress().getAddress().getHostAddress() , self.java_obj.localAddress().getPort();
        return self.local_addr

    def _to_java_socket(self):
      return self.java_obj

class EventBusBridge(object):
    """Event bus bridge."""
    def __init__(self, j_bridge):
        self.java_obj = j_bridge
        self.hook = _EventBusBridgeHook()

    def socket_created_handler(self, func):
        """Registers a socket created handler."""
        return self.hook.socket_created_handler(func)

    def socket_closed_handler(self, func):
        """Registers a socket closed handler."""
        return self.hook.socket_closed_handler(func)

    def send_or_pub_handler(self, func):
        """Registers a send or pub handler."""
        return self.hook.send_or_pub_handler(func)

    def pre_register_handler(self, func):
        """Registers a pre-register handler."""
        return self.hook.pre_register_handler(func)

    def post_register_handler(self, func):
        """Registers a post-register handler."""
        return self.hook.post_register_handler(func)

    def unregister_handler(self, func):
        """Registers an unregister handler."""
        return self.hook.unregister_handler(func)

    def authorise_handler(self, func):
        """Registers an authorise handler."""
        return self.hook.authorise_handler(func)

class _EventBusBridgeHook(org.vertx.java.core.sockjs.EventBusBridgeHook):
    _socket_created_handler = None
    _socket_closed_handler = None
    _send_or_pub_handler = None
    _pre_register_handler = None
    _post_register_handler = None
    _unregister_handler = None
    _authorise_handler = None

    def socket_created_handler(self, func):
        self._socket_created_handler = func
        return func

    def handleSocketCreated(self, j_sock):
        if self._socket_created_handler is not None:
            result = self._socket_created_handler(SockJSSocket(j_sock))
            return result if result is not None else True
        return True

    def socket_closed_handler(self, func):
        self._socket_closed_handler = func
        return func

    def handleSocketClosed(self, j_sock):
        if self._socket_closed_handler is not None:
            self._socket_closed_handler(SockJSSocket(j_sock))

    def send_or_pub_handler(self, func):
        self._send_or_pub_handler = func
        return func

    def handleSendOrPub(self, j_sock, send, message, address):
        if self._send_or_pub_handler is not None:
            result = self._send_or_pub_handler(SockJSSocket(j_sock), send, map_from_java(message), address)
            return result if result is not None else True
        return True

    def pre_register_handler(self, func):
        self._pre_register_handler = func
        return func

    def handlePreRegister(self, j_sock, address):
        if self._pre_register_handler is not None:
            result = self._pre_register_handler(SockJSSocket(j_sock), address)
            return result if result is not None else True
        return True

    def post_register_handler(self, func):
        self._post_register_handler = func
        return func

    def handlePostRegister(self, j_sock, address):
        if self._post_register_handler is not None:
            self._post_register_handler(SockJSSocket(j_sock), address)

    def unregister_handler(self, func):
        self._unregister_handler = func
        return func

    def handleUnregister(self, j_sock, address):
        if self._unregister_handler is not None:
            result = self._unregister_handler(SockJSSocket(j_sock), address)
            return result if result is not None else True
        return True

    def authorise_handler(self, func):
        self._authorise_handler = func
        return func

    def handleAuthorise(self, message, session_id, handler):
        if self._authorise_handler is not None:
            async_handler = AsyncHandler(handler)
            def func(result):
                if isinstance(result, Exception):
                    org.vertx.java.core.impl.DefaultFutureResult().setHandler(handler).setFailure(result)
                else:
                    org.vertx.java.core.impl.DefaultFutureResult().setHandler(handler).setResult(bool(result))
            result = self._authorise_handler(map_from_java(message), session_id, func)
            return result if result is not None else True
        return True

class SockJSSocketHandler(org.vertx.java.core.Handler):
    """SockJS Socket handler"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, sock):
        """Call the handler after SockJS Socket is ready"""
        self.handler(SockJSSocket(sock))
