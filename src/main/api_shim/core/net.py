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
Net support to the python vert.x platform 
"""

import org.vertx.java.core.Handler
import org.vertx.java.platform.impl.JythonVerticleFactory
import core.tcp_support
import core.ssl_support
import core.buffer
import core.streams

from core.javautils import inetsocketaddress_to_tuple
from core.handlers import CloseHandler, NullDoneHandler, AsyncHandler
from core.event_bus import EventBus

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

class NetServer(core.ssl_support.ServerSSLSupport, core.tcp_support.ServerTCPSupport):
    """Represents a TCP or SSL Server

    When connections are accepted by the server
    they are supplied to the user in the form of a NetSocket instance that is passed via the handler
    set using connect_handler.
    """
    def __init__(self, server, **kwargs):
        self.java_obj = server
        for item in kwargs.keys():
           setattr(self, item, kwargs[item])

    def connect_handler(self, handler):
        """Supply a connect handler for this server. The server can only have at most one connect handler at any one time.
        As the server accepts TCP or SSL connections it creates an instance of NetSocket and passes it to the
        connect handler.

        Keyword arguments:
        @param handler: connection handler
        
        @return: a reference to self so invocations can be chained
        """
        self.java_obj.connectHandler(ConnectHandler(handler))
        return self


    def listen(self, port, host="0.0.0.0", handler=None):
        """Instruct the server to listen for incoming connections.

        Keyword arguments:
        @param port:    The port to listen on.
        @param host:    The host name or ip address to listen on.
        @param handler: The handler to notify once the listen operations completes (default None)
        
        @return: a reference to self so invocations can be chained
        """
        if (handler is None):
            self.java_obj.listen(port, host)
        else:
            def converter(server):
                return self
            self.java_obj.listen(port, host, AsyncHandler(handler, converter))
        return self


    def close(self, handler=None):
        """Close the server. The handler will be called when the close is complete."""
        if (handler is None):
            self.java_obj.close()
        else:
            self.java_obj.close(AsyncHandler(handler))

    @property
    def port(self):
        """The actual port the server is listening on. This is useful if you bound the server specifying 0 as port number
        signifying an ephemeral port
        """
        return self.java_obj.port()

    @property
    def host(self):
        """The host to which the server is bound."""
        return self.java_obj.host()


class NetClient(core.ssl_support.ClientSSLSupport, core.tcp_support.TCPSupport):
    """NetClient is an asynchronous factory for TCP or SSL connections.

    Multiple connections to different servers can be made using the same instance.
    """
    def __init__(self, **kwargs):
        self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createNetClient()
        for item in kwargs.keys():
           setattr(self, item, kwargs[item])

    def connect(self, port, host, handler):
        """Attempt to open a connection to a server. The connection is opened asynchronously and the result returned in the
        handler.

        Keyword arguments:
        @param port: The port to connect to.
        @param host: The host or ip address to connect to.
        @param handler: The connection handler

        @return: a reference to self so invocations can be chained
        """
        def converter(socket):
            return NetSocket(socket)

        self.java_obj.connect(port, host, AsyncHandler(handler, converter))
        return self

    def set_reconnect_attempts(self, val):
        """Set the number of reconnection attempts. In the event a connection attempt fails, the client will attempt
        to connect a further number of times, before it fails. Default value is zero.
        """
        self.java_obj.setReconnectAttempts(val)
        return self

    def get_reconnect_attempts(self):
        """Get the number of reconnect attempts"""
        return self.java_obj.getReconnectAttempts()

    property(get_reconnect_attempts, set_reconnect_attempts)

    def set_reconnect_interval(self, val):
        """Set the reconnect interval, in milliseconds"""
        self.java_obj.setReconnectInterval(val)
        return self

    def get_reconnect_interval(self):
        """Get the reconnect interval, in milliseconds."""
        return self.java_obj.getReconnectInterval()

    property(get_reconnect_interval, set_reconnect_interval)

    def set_connect_timeout(self, val):
        """Set the connect timeout in milliseconds."""
        self.java_obj.setConnectTimeout(val)
        return self

    def get_connect_timeout(self):
        """Returns the connect timeout in milliseconds"""
        return self.java_obj.getConnectTimeout()

    property(get_connect_timeout, set_connect_timeout)

    def close(self):
        """Close the NetClient. Any open connections will be closed."""
        self.java_obj.close()

class NetSocket(core.streams.ReadStream, core.streams.WriteStream):
    """NetSocket is a socket-like abstraction used for reading from or writing
    to TCP connections.
    """     
    def __init__(self, j_socket):
        self.java_obj = j_socket
        self.remote_addr = None
        self.local_addr = None

        def simple_handler(msg):
            self.write(msg.body)

        self.write_handler_id = EventBus.register_simple_handler(False, simple_handler)
        
        def wrapped_close_handler():
            EventBus.unregister_handler(self.write_handler_id)
            if hasattr(self, "_close_handler"):
                self._close_handler()
        self.java_obj.closeHandler(CloseHandler(wrapped_close_handler))

    @property
    def is_ssl(self):
        """Indicates whether the socket is an SSL connection."""
        return self.java_obj.isSsl()

    def ssl(self, handler):
        """Upgrades the channel to use SSL/TLS. Be aware for this to work SSL must be configured.

        Keyword arguments:
        @param handler: a function to be called once complete
        @return: self
        """
        self.java_obj.ssl(NullDoneHandler(handler))
        return self

    def write_str(self, str, enc="UTF-8"):
        """Write a String to the socket. The handler will be called when the string has actually been written to the wire.

        Keyword arguments:
        @param str: The string to write.
        @param enc: The encoding to use.
        """
        self.java_obj.write(str, enc)
        return self
      
    def close_handler(self, handler):
        """Set a close handler on the socket.

        Keyword arguments:
        @param handler: A block to be used as the handler
        """
        self._close_handler = handler
        return self

    def send_file(self, file_path):
        """Tell the kernel to stream a file directly from disk to the outgoing connection, bypassing userspace altogether
        (where supported by the underlying operating system. This is a very efficient way to stream files.

        Keyword arguments:
        @param file_path: Path to file to send.
        """
        self.java_obj.sendFile(file_path)
        return self

    @property
    def remote_address(self):
        """Returns the remote address as tuple in form of ('ipaddress', port)"""
        if self.remote_addr is None:
            self.remote_addr =  inetsocketaddress_to_tuple(self.java_obj.remoteAddress())
        return self.remote_addr

    @property
    def local_address(self):
        """Returns the local address as tuple in form of ('ipaddress', port)"""
        if self.local_addr is None:
            self.local_addr =  inetsocketaddress_to_tuple(self.java_obj.localAddress())
        return self.local_addr

    def close(self):
        """Close the socket"""
        self.java_obj.close()

class ConnectHandler(org.vertx.java.core.Handler):
    """Connection handler """
    def __init__(self, handler):
        self.handler = handler

    def handle(self, socket):
        """Call the handler after connection is established"""
        self.handler(NetSocket(socket))

