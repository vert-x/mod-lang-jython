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

"""
This module adds the http support to the python vert.x platform 
"""

import org.vertx.java.platform.impl.JythonVerticleFactory
import org.vertx.java.core.http.RouteMatcher
import core.tcp_support
import core.ssl_support
import core.buffer
import core.streams

from core.javautils import map_from_java, map_to_java
from core.handlers import CloseHandler, ExceptionHandler
from core.handlers import ContinueHandler, BufferHandler, AsyncHandler
from UserDict import DictMixin

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

class HttpServer(core.tcp_support.ServerTCPSupport, core.ssl_support.ServerSSLSupport, object):
    """An HTTP and websockets server"""
    def __init__(self, server, **kwargs):
        self.java_obj = server
        for item in kwargs.keys():
           setattr(self, item, kwargs[item])

    def get_compression_supported(self):
        """true if the server should compress http response if the connected client supports it."""
        return self.java_obj.isCompressionSupported()

    def set_compression_supported(self, supported):
        """Set if the server should compress the http response if the connected client supports it."""
        self.java_obj.setCompressionSupported(supported)
        return self

    compression_supported = property(get_compression_supported, set_compression_supported)

    def get_max_web_socket_frame_size(self):
        """Get the maximum websocket frame size in bytes"""
        return self.java_obj.getMaxWebSocketFrameSize()

    def set_max_web_socket_frame_size(self, max_frame_size):
        """Set the maximum websocket frame size in bytes."""
        self.java_obj.setMaxWebSocketFrameSize(max_frame_size)
        return self

    max_web_socket_frame_size = property(get_max_web_socket_frame_size, set_max_web_socket_frame_size)

    def request_handler(self, handler):
        """Set the HTTP request handler for the server.
        As HTTP requests arrive on the server a new HttpServerRequest instance will be created and passed to the handler.

        Keyword arguments:
        @param handler: the function used to handle the request. 
        
        @return: self
        """
        self.java_obj.requestHandler(HttpServerRequestHandler(handler))
        return self

    def websocket_handler(self, handler):
        """Set the websocket handler for the server.
        As websocket requests arrive on the server a new ServerWebSocket instance will be created and passed to the handler.

        Keyword arguments:
        @param handler: the function used to handle the request. 

        @return self
        """
        self.java_obj.websocketHandler(ServerWebSocketHandler(handler))
        return self

    def listen(self, port=80, host="0.0.0.0", handler=None):
        """Instruct the server to listen for incoming connections. If host is None listens on all.

        Keyword arguments:
        @param port:    The port to listen on.
        @param host:    The host name or ip address to listen on. (default 0.0.0.0)
        @param handler: The handler to notify once the listen operation completes. (default None)
    
        @return self
        """
        if handler is None:
            self.java_obj.listen(port, host)
        else:
            def converter(server):
                return self
            self.java_obj.listen(port, host, AsyncHandler(handler, converter))
        return self

    def close(self, handler=None):
        """Close the server. Any open HTTP connections will be closed. This can be used as a decorator.

        Keyword arguments:
        @param handler: a handler that is called when the connection is closed. The handler is wrapped in a CloseHandler.
        """
        if handler is None:
            self.java_obj.close()
        else:
            self.java_obj.close(AsyncHandler(handler))

    def _to_java_server(self):
        """private """
        return self.java_obj

class HttpClient(core.ssl_support.ClientSSLSupport, core.tcp_support.TCPSupport, object):
    """An HTTP client.

    A client maintains a pool of connections to a specific host, at a specific port. The HTTP connections can act
    as pipelines for HTTP requests.
    It is used as a factory for HttpClientRequest instances which encapsulate the actual HTTP requests. It is also
    used as a factory for HTML5 WebSocket websockets.
    """
    def __init__(self, **kwargs):
        self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createHttpClient()
        for item in kwargs.keys():
           setattr(self, item, kwargs[item])

    def exception_handler(self, handler):
        """Set the exception handler.

        Keyword arguments:
        @param handler: function to be used as the handler
        """
        self.java_obj.exceptionHandler(ExceptionHandler(handler))
        return self
    
    def get_max_pool_size(self):
        """The maxium number of connections this client will pool."""
        return self.java_obj.getMaxPoolSize()

    def set_max_pool_size(self, val):
        """Set the maximum pool size.
        The client will maintain up to this number of HTTP connections in an internal pool

        Keyword arguments:
        @param val: The maximum number of connections (default to 1).
        """
        self.java_obj.setMaxPoolSize(val)
        return self

    max_pool_size = property(get_max_pool_size, set_max_pool_size)

    def get_keep_alive(self):
        """Return if the client use keep alive."""
        return self.java_obj.getKeepAlive()

    def set_keep_alive(self, val):
        """If val is true then, after the request has ended the connection will be returned to the pool
        where it can be used by another request. In this manner, many HTTP requests can be pipe-lined over an HTTP connection.
        Keep alive connections will not be closed until the close method is invoked.
        If val is false then a new connection will be created for each request and it won't ever go in the pool,
        the connection will closed after the response has been received. Even with no keep alive, the client will not allow more
        than max_pool_size connections to be created at any one time.

        Keyword arguments:
        @param val: The value to use for keep_alive
        """
        self.java_obj.setKeepAlive(val)
        return self

    keep_alive = property(get_keep_alive, set_keep_alive)

    def get_port(self):
        """Return the port the client will attempt to ."""
        return self.java_obj.getPort()

    def set_port(self, val):
        """Set the port that the client will attempt to connect to on the server on. The default value is 80

        Keyword arguments:
        @param val: The port value.
        """
        self.java_obj.setPort(val)
        return self

    port = property(get_port, set_port)

    def get_host(self):
        return self.java_obj.getHost()

    def set_host(self, val):
        """Set the host name or ip address that the client will attempt to connect to on the server on.

        Keyword arguments:
        @param val: The host name or ip address to connect to.
        """
        self.java_obj.setHost(val)
        return self
    
    host = property(get_host, set_host)

    def get_verify_host(self):
        return self.java_obj.getVerifyHost()

    def set_verify_host(self, val):
        """If set then the client will try to validate the remote server's certificate
         hostname against the requested host. Should default to 'true'.
         This method should only be used in SSL mode.

        Keyword arguments:
        @param val: true if verify hostname
        """
        self.java_obj.setVerifyHost(val)
        return self

    verify_host = property(get_verify_host, set_verify_host)

    def get_try_use_compression(self):
        """true if the client should try to use compression."""
        return self.java_obj.getTryUseCompression()

    def set_try_use_compression(self, use_compression):
        """Set if the client should try to use compression."""
        self.java_obj.setTryUseCompression(use_compression)
        return self

    try_use_compression = property(get_try_use_compression, set_try_use_compression)

    def get_max_web_socket_frame_size(self):
        """Get the maximum websocket frame size in bytes"""
        return self.java_obj.getMaxWebSocketFrameSize()

    def set_max_web_socket_frame_size(self, max_frame_size):
        """Set the maximum websocket frame size in bytes."""
        self.java_obj.setMaxWebSocketFrameSize(max_frame_size)
        return self

    max_web_socket_frame_size = property(get_max_web_socket_frame_size, set_max_web_socket_frame_size)

    def connect_web_socket(self, uri, handler):
        """Attempt to connect an HTML5 websocket to the specified URI.
        The connect is done asynchronously and the handler is called with a WebSocket on success.

        Keyword arguments:
        @param uri: A relative URI where to connect the websocket on the host, e.g. /some/path
        @param handler: The handler to be called with the WebSocket
        """
        if (handler is None):
            self.java_obj.connectWebsocket(uri, WebSocketHandler(handler))
        else:
            self.java_obj.connectWebsocket(uri, WebSocketHandler(handler))
        return self

    def get_now(self, uri, handler, **headers):
        """This is a quick version of the get method where you do not want to do anything with the request
        before sing.
        With this method the request is immediately sent.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the GET on the server.
        @param handler: The handler to be called with the HttpClientResponse
        @param headers: A dictionary of headers to pass with the request.
        """
        if len(headers) == 0:
            self.java_obj.getNow(uri, HttpClientResponseHandler(handler))    
        else:
            self.java_obj.getNow(uri, map_to_java(headers), HttpClientResponseHandler(handler))
        return self
        
    def options(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP OPTIONS request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the OPTIONS on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.options(uri, HttpClientResponseHandler(handler)))

    def get(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP GET request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the GET on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.get(uri, HttpClientResponseHandler(handler)))

    def head(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP HEAD request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the HEAD on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.head(uri, HttpClientResponseHandler(handler)))

    def post(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP POST request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the POST on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.post(uri, HttpClientResponseHandler(handler)))

    def put(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP PUT request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.
        
        Keyword arguments:
        @param uri: A relative URI where to perform the PUT on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.put(uri, HttpClientResponseHandler(handler)))

    def delete(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP DELETE request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the DELETE on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.delete(uri, HttpClientResponseHandler(handler)))

    def trace(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP TRACE request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the TRACE on the server.
        handler. The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.trace(uri, HttpClientResponseHandler(handler)))

    def connect(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP CONNECT request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.
        
        Keyword arguments:
        @param uri: A relative URI where to perform the CONNECT on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.connect(uri, HttpClientResponseHandler(handler)))

    def patch(self, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP PATCH request with the specified uri.
        When an HTTP response is received from the server the handler is called passing in the response.

        Keyword arguments:
        @param uri: A relative URI where to perform the PATCH on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.patch(uri, HttpClientResponseHandler(handler)))

    def request(self, method, uri, handler):
        """This method returns an HttpClientRequest instance which represents an HTTP request with the specified method and uri.
        When an HTTP response is received from the server the handler is called passing in the response.
        method. The HTTP method. Can be one of OPTIONS, HEAD, GET, POST, PUT, DELETE, TRACE, CONNECT.

        Keyword arguments:
        @param uri: A relative URI where to perform the OPTIONS on the server.
        @param handler: The handler to be called with the HttpClientResponse
        """
        return HttpClientRequest(self.java_obj.request(method, uri, HttpClientResponseHandler(handler)))

    def close(self):
        """Close the client. Any unclosed connections will be closed."""
        self.java_obj.close()

class HttpClientRequest(core.streams.WriteStream):
    """Instances of this class are created by an HttpClient instance, via one of the methods corresponding to the
     specific HTTP methods, or the generic HttpClient request method.

     Once an instance of this class has been obtained, headers can be set on it, and data can be written to its body,
     if required. Once you are ready to send the request, the end method must called.

     Nothing is sent until the request has been internally assigned an HTTP connection. The HttpClient instance
     will return an instance of this class immediately, even if there are no HTTP connections available in the pool. Any requests
     sent before a connection is assigned will be queued internally and actually sent when an HTTP connection becomes
     available from the pool.

     The headers of the request are actually sent either when the end method is called, or, when the first
     part of the body is written, whichever occurs first.

     This class supports both chunked and non-chunked HTTP.
    """
    def __init__(self, java_obj):
        self.java_obj = java_obj
        self.hdrs = None

    @property
    def headers(self):
        """Headers for the request"""
        if self.hdrs is None:
            self.hdrs = MultiMap(self.java_obj.headers())
        return self.hdrs

    def put_header(self, key, value):
        """Inserts a header into the request.

        Keyword arguments:
        @param key: The header key
        @param value: The header value.

        @return: self so multiple operations can be chained.
        """
        self.java_obj.putHeader(key, value)
        return self


    def write_str(self, str, enc="UTF-8"):
        """Write a to the request body.

        Keyword arguments:
        @param str: The string to write.
        @param enc: The encoding to use.
        
        @return: self So multiple operations can be chained.
        """
        self.java_obj.write(str, enc)
        return self

    def send_head(self):
        """Forces the head of the request to be written before end is called on the request. This is normally used
        to implement HTTP 100-continue handling, see continue_handler for more information.
        
        @return: self So multiple operations can be chained.
        """
        self.java_obj.sendHead()
        return self

    def end(self):
        """Ends the request. If no data has been written to the request body, and send_head has not been called then
        the actual request won't get written until this method gets called.
        Once the request has ended, it cannot be used any more, and if keep alive is true the underlying connection will
        be returned to the HttpClient pool so it can be assigned to another request.
        """
        self.java_obj.end()

    def write_str_and_end(self, str, enc="UTF-8"):
        """Same as write_buffer_and_end but writes a String

        Keyword arguments:
        @param str: The String to write
        @param enc: The encoding
        """
        self.java_obj.end(str, enc)

    def write_buffer_and_end(self, chunk):
        """Same as end but writes some data to the response body before ending. If the response is not chunked and
        no other data has been written then the Content-Length header will be automatically set

        Keyword arguments:
        @param chunk: The Buffer to write
        """
        self.java_obj.end(chunk._to_java_buffer())

    def set_chunked(self, val):
        """Sets whether the request should used HTTP chunked encoding or not.

        Keyword arguments:
        @param val: If val is true, this request will use HTTP chunked encoding, and each call to write to the body
        will correspond to a new HTTP chunk sent on the wire. If chunked encoding is used the HTTP header
        'Transfer-Encoding' with a value of 'Chunked' will be automatically inserted in the request.

        If chunked is false, this request will not use HTTP chunked encoding, and therefore if any data is written the
        body of the request, the total size of that data must be set in the 'Content-Length' header before any
        data is written to the request body.
        
        @return: self So multiple operations can be chained.
        """
        self.java_obj.setChunked(val)
        return self

    def is_chunked(self):
        return self.java_obj.isChunked()

    chunked = property(is_chunked, set_chunked)

    def set_timeout(self, val):
        """Set's the amount of time after which if a response is not received TimeoutException()
        will be sent to the exception handler of this request. Calling this method more than once
        has the effect of canceling any existing timeout and starting the timeout from scratch.


        Keyword arguments:
        @param val: The quantity of time in milliseconds.

        @return: self So multiple operations can be chained.
        """
        self.java_obj.setTimeout(val)
        return self

    timeout = property(fset=set_timeout)

    def continue_handler(self, handler):
        """If you send an HTTP request with the header 'Expect' set to the value '100-continue'
        and the server responds with an interim HTTP response with a status code of '100' and a continue handler
        has been set using this method, then the handler will be called.
        You can then continue to write data to the request body and later end it. This is normally used in conjunction with
        the send_head method to force the request header to be written before the request has ended.

        Keyword arguments:
        @param handler: The handler
        """
        self.java_obj.continueHandler(ContinueHandler(handler))
        return self

   
class HttpClientResponse(core.streams.ReadStream):
    """Encapsulates a client-side HTTP response.

    An instance of this class is provided to the user via a handler that was specified when one of the
    HTTP method operations, or the generic HttpClientrequest method was called on an instance of HttpClient.
    """
    def __init__(self, java_obj):
        self.java_obj = java_obj
        self.hdrs = None
        self.trls = None
        self.cookies_set = None
   
    @property
    def status_code(self):
        """return the HTTP status code of the response."""
        return self.java_obj.statusCode()
  
    @property
    def headers(self):
        """Get all the headers in the response.
        If the response contains multiple headers with the same key, the values
        will be concatenated together into a single header with the same key value, with each value separated by a comma,
        as specified by {http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.htmlsec4.2}.
        return headers.
        """
        if self.hdrs is None:
            self.hdrs = MultiMap(self.java_obj.headers())
        return self.hdrs

    @property
    def trailers(self):
        """Get all the trailers in the response.
        If the response contains multiple trailers with the same key, the values
        will be concatenated together into a single header with the same key value, with each value separated by a comma,
        as specified by {http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.htmlsec4.2}.
        Trailers will only be available in the response if the server has sent a HTTP chunked response where headers have
        been inserted by the server on the last chunk. In such a case they won't be available on the client until the last chunk has
        been received.
        
        return trailers."""
        if self.trls is None:
            self.trls = MultiMap(self.java_obj.trailers())
        return self.trls

    @property
    def cookies(self):
        """The Set-Cookie headers (including trailers)"""
        if self.cookies_set is None:
            self.cookies_set = map_from_java(self.java_obj.cookies())
        return self.cookies_set

    def body_handler(self, handler):
        """Set a handler to receive the entire body in one go - do not use this for large bodies"""
        self.java_obj.bodyHandler(BufferHandler(handler))
        return self
  
class HttpServerRequest(core.streams.ReadStream):
    """Encapsulates a server-side HTTP request.
  
    An instance of this class is created for each request that is handled by the server and is passed to the user via the
    handler specified using HttpServer.request_handler.

    Each instance of this class is associated with a corresponding HttpServerResponse instance via the property response.
    """
    def __init__(self, java_obj):
        self.java_obj = java_obj
        self.http_server_response = HttpServerResponse(java_obj.response())
        self.hdrs = None
        self.prms = None
        self.vrsn = None
        self.attrs = None
        self.expect_mp = False

    @property
    def version(self):
        """The HTTP version - either HTTP_1_0 or HTTP_1_1"""
        if self.vrsn is None:
            self.vrsn = self.java_obj.version().toString()
        return self.vrsn
    
    @property
    def method(self):
        """The HTTP method, one of HEAD, OPTIONS, GET, POST, PUT, DELETE, CONNECT, TRACE"""
        return self.java_obj.method()

    @property
    def uri(self):
        """The uri of the request. For example 'http://www.somedomain.com/somepath/somemorepath/somresource.foo?someparam=32&someotherparam=x """
        return self.java_obj.uri()

    @property
    def path(self):
        """The path part of the uri. For example /somepath/somemorepath/somresource.foo """
        return self.java_obj.path()

    @property
    def query(self):
        """The query part of the uri. For example someparam=32&someotherparam=x """
        return self.java_obj.query()

    @property
    def params(self):
        """The request parameters """
        if self.prms is None:
            self.prms = MultiMap(self.java_obj.params())
        return self.prms

    @property
    def response(self):
        """The response HttpServerResponse object."""
        return self.http_server_response

    @property
    def headers(self):
        """The request headers """
        if self.hdrs is None:
            self.hdrs = MultiMap(self.java_obj.headers())
        return self.hdrs

    def body_handler(self, handler):
        """Set the body handler for this request, the handler receives a single Buffer object as a parameter. 
        This can be used as a decorator. 

        Keyword arguments:
        @param handler: a handler that is called when the body has been received. The handler is wrapped in a BufferHandler.

        """
        self.java_obj.bodyHandler(BufferHandler(handler))
        return self

    @property
    def remote_address(self):
        """Return the remote (client side) address of the request"""
        return self.java_obj.remoteAddress()

    @property
    def absolute_uri(self):
        """Return the absolute URI corresponding to the the HTTP request"""
        return self.java_obj.absoluteURI()

    @property
    def peer_certificate_chain(self):
        return self.java_obj.peerCertificateChain()

    def set_expect_multipart(self, expect):
        """You must call this function with true before receiving the request body if you expect it to
        contain a multi-part form.

        Keyword arguments:
        @param expect: true if you are expecting a multipart form
        """
        self.java_obj.expectMultiPart(expect)
        self.expect_mp = expect
        return self

    def is_expect_multipart(self):
        return self.expect_mp

    @property
    def form_attributes(self):
        if self.attrs is None:
            self.attrs = MultiMap(self.java_obj.formAttributes())
        return self.attrs

    expect_multipart = property(is_expect_multipart, set_expect_multipart)

    def upload_handler(self, handler):
        """
        Set the upload handler. The handler will get notified once a new file upload was received and so allow to
        get notified by the upload in progress.
        """
        self.java_obj.uploadHandler(HttpServerFileUploadHandler(handler))

    def _to_java_request(self):
        """
        Returns a dict of all form attributes which was found in the request. Be aware that this message should only get
        called after the endHandler was notified as the map will be filled on-the-fly.
        """
        return self.java_obj

class HttpServerResponse(core.streams.WriteStream):
    """Encapsulates a server-side HTTP response.

    An instance of this class is created and associated to every instance of HttpServerRequest that is created.

    It allows the developer to control the HTTP response that is sent back to the client for the corresponding HTTP
    request. It contains methods that allow HTTP headers and trailers to be set, and for a body to be written out
    to the response.

    """
    def __init__(self, java_obj):
        self.java_obj = java_obj
        self.hdrs = None
        self.trls = None

    def get_status_code(self):
        """Get the status code of the response. """
        return self.java_obj.getStatusCode()

    def set_status_code(self, code):
        """Set the status code of the response. Default is 200 """
        self.java_obj.setStatusCode(code)
        return self

    status_code = property(get_status_code, set_status_code)

    def get_status_message(self):
        """Get the status message the goes with status code """
        return self.java_obj.getStatusMessage()

    def set_status_message(self, message):
        """Set the status message for a response """
        self.java_obj.setStatusMessage(message)
        return self

    status_message = property(get_status_message, set_status_message)

    @property
    def headers(self):
        """Get reponse headers """
        if (self.hdrs is None):
            self.hdrs = MultiMap(self.java_obj.headers());
        return self.hdrs

    def put_header(self, key, value):
        """Inserts a header into the response.

        Keyword arguments:
        @param key: The header key
        @param value: The header value.
        
        @return: HttpServerResponse so multiple operations can be chained.
        """
        self.java_obj.putHeader(key, value)
        return self

    @property
    def trailers(self):
        """Get a copy of the trailers as a dictionary """
        if (self.trls is None):
            self.trls = MultiMap(self.java_obj.trailers())
        return self.trls

    def put_trailer(self, key, value):
        """Inserts a trailer into the response. 

        Keyword arguments:
        @param key: The header key
        @param value: The header value.
        @return: HttpServerResponse so multiple operations can be chained.

        """
        self.java_obj.putTrailer(key, value)
        return self

    def write_str(self, str, enc="UTF-8"):
        """Write a String to the response. The handler will be called when the String has actually been written to the wire.

        Keyword arguments:
        @param str: The string to write
        @param enc: Encoding to use.

        @param handler: The handler to be called when writing has been completed. It is wrapped in a AsyncHandler (default None)
        
        @return: a HttpServerResponse so multiple operations can be chained.
        """
        self.java_obj.write(str, enc)
        return self

    def send_file(self, path, not_found_file=None, handler=None):
        """Tell the kernel to stream a file directly from disk to the outgoing connection, bypassing userspace altogether
        (where supported by the underlying operating system. This is a very efficient way to serve files.

        Keyword arguments:
        @param path: Path to file to send.
        @param handler: An optional asynchronous handler to be called once complete.
        
        @return: a HttpServerResponse so multiple operations can be chained.
        """
        if not_found_file is not None and handler is not None:
            self.java_obj.sendFile(path, not_found_file, AsyncHandler(handler))
        elif not_found_file is not None:
            self.java_obj.sendFile(path, not_found_file)
        elif handler is not None:
            self.java_obj.sendFile(path, AsyncHandler(handler))
        else:
            self.java_obj.sendFile(path)
        return self

    def set_chunked(self, val):
        """Sets whether this response uses HTTP chunked encoding or not.

        Keyword arguments:
        @param val: If val is true, this response will use HTTP chunked encoding, and each call to write to the body
        will correspond to a new HTTP chunk sent on the wire. If chunked encoding is used the HTTP header
        'Transfer-Encoding' with a value of 'Chunked' will be automatically inserted in the response.

        If chunked is false, this response will not use HTTP chunked encoding, and therefore if any data is written the
        body of the response, the total size of that data must be set in the 'Content-Length' header before any
        data is written to the response body.
        An HTTP chunked response is typically used when you do not know the total size of the request body up front.
        
        @return: a HttpServerResponse so multiple operations can be chained.
        """
        self.java_obj.setChunked(val)
        return self

    def is_chunked(self):
        """Get whether this response uses HTTP chunked encoding or not. """
        return self.java_obj.isChunked()

    chunked = property(is_chunked, set_chunked)

    def end(self, data=None):
        """Ends the response. If no data has been written to the response body, the actual response won't get written until this method gets called.
        Once the response has ended, it cannot be used any more, and if keep alive is true the underlying connection will
        be closed.

        Keywords arguments
        @param data: Optional String or Buffer to write before ending the response

        """
        if data is None:
            self.java_obj.end()
        else:
            self.java_obj.end(data)

    def close(self):
        """Close the underlying TCP connection """
        self.java_obj.close()

class WebSocket(core.streams.ReadStream, core.streams.WriteStream):
    """Encapsulates an HTML 5 Websocket.

    Instances of this class are created by an HttpClient instance when a client succeeds in a websocket handshake with a server.
    Once an instance has been obtained it can be used to s or receive buffers of data from the connection,
    a bit like a TCP socket.
    """
    def __init__(self, websocket):
        self.java_obj = websocket
        self.remote_addr = None
        self.local_addr = None

    @property
    def binary_handler_id(self):
        """
        When a WebSocket is created it automatically registers an event handler with the eventbus, the ID of that
        handler is returned.

        Given this ID, a different event loop can send a binary frame to that event handler using the event bus and
        that buffer will be received by this instance in its own event loop and written to the underlying connection. This
        allows you to write data to other websockets which are owned by different event loops.
        """
        return self.java_obj.binaryHandlerID()

    @property
    def text_handler_id(self):
        """
        When a WebSocket is created it automatically registers an event handler with the eventbus, the ID of that
        handler is returned.

        Given this ID, a different event loop can send a text frame to that event handler using the event bus and
        that buffer will be received by this instance in its own event loop and written to the underlying connection. This
        allows you to write data to other websockets which are owned by different event loops.
        """
        return self.java_obj.textHandlerID()

    def write_binary_frame(self, buf):
        """
        Write data to the websocket as a binary frame 

        Keyword arguments:
        @param buffer: Buffer data to write to socket.

        """
        self.java_obj.writeBinaryFrame(buf._to_java_buffer())
        return self

    def write_text_frame(self, text):
        """
        Write data to the websocket as a text frame 

        Keyword arguments:
        @param text: text to write to socket
        """
        self.java_obj.writeTextFrame(text)
        return self
        
    @property
    def remote_address(self):
        """
        Returns the remote address as tuple in form of ('ipaddress', port)
        """
        if self.remote_addr is None:
            self.remote_addr =  self.java_obj.remoteAddress().getAddress().getHostAddress() , self.java_obj.remoteAddress().getPort();
        return self.remote_addr

    @property
    def local_address(self):
        """
        Returns the local address as tuple in form of ('ipaddress', port)
        """
        if self.local_addr is None:
            self.local_addr =  self.java_obj.localAddress().getAddress().getHostAddress() , self.java_obj.localAddress().getPort();
        return self.local_addr

    def close(self):
        """Close the websocket """
        self.java_obj.close()

    def close_handler(self, handler):
        """Set a closed handler on the connection, the handler receives a no parameters. 
        This can be used as a decorator. 

        Keyword arguments:
        handler - The handler to be called when writing has been completed. It is wrapped in a CloseHandler.
        """
        self.java_obj.closeHandler(CloseHandler(handler))
        return self

class ServerWebSocket(WebSocket):
    """Instances of this class are created when a WebSocket is accepted on the server.
    It extends WebSocket and adds methods to reject the WebSocket and an
    attribute for the path.

    """
    def __init__(self, websocket):
        self.java_obj = websocket
        self.hdrs = None

    def reject(self):
        """Reject the WebSocket. Sends 404 to client """
        self.java_obj.reject()
        return self

    @property
    def headers(self):
        if (self.hdrs is None):
            self.hdrs = MultiMap(self.java_obj.headers())
        return self.hdrs

    @property
    def path(self):
        """The path the websocket connect was attempted at. """
        return self.java_obj.path()

    @property
    def uri(self):
        """The uri at which the websocket handshake occurred."""
        return self.java_obj.uri()

class HttpServerRequestHandler(org.vertx.java.core.Handler):
    """A handler for Http Server Requests"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, req):
        """Called when a request is being handled. Argument is a HttpServerRequest object """
        self.handler(HttpServerRequest(req))

class HttpClientResponseHandler(org.vertx.java.core.Handler):
    """A handler for Http Client Responses"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, res):
        """Called when a response is being handled. Argument is a HttpClientResponse object """
        self.handler(HttpClientResponse(res))

class ServerWebSocketHandler(org.vertx.java.core.Handler):
    """A handler for WebSocket Server Requests"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, req):
        """Calls the Handler with the ServerWebSocket when connected """
        self.handler(ServerWebSocket(req))

class WebSocketHandler(org.vertx.java.core.Handler):
    """A handler for WebSocket  Requests"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, req):
        """Calls the Handler with the WebSocket when connected """
        self.handler(WebSocket(req))

class HttpServerFileUploadHandler(org.vertx.java.core.Handler):
    """A handler for Http Server File Uploads"""
    def __init__(self, handler):
        self.handler = handler

    def handle(self, upload):
        self.handler(HttpServerFileUpload(upload))

class RouteMatcher(object):
    """This class allows you to do route requests based on the HTTP verb and the request URI, in a manner similar
    to <a href="http://www.sinatrarb.com/">Sinatra</a> or <a href="http://expressjs.com/">Express</a>.

    RouteMatcher also lets you extract parameters from the request URI either a simple pattern or using
    regular expressions for more complex matches. Any parameters extracted will be added to the requests parameters
    which will be available to you in your request handler.

    It's particularly useful when writing REST-ful web applications.

    To use a simple pattern to extract parameters simply prefix the parameter name in the pattern with a ':' (colon).

    Different handlers can be specified for each of the HTTP verbs, GET, POST, PUT, DELETE etc.

    For more complex matches regular expressions can be used in the pattern. When regular expressions are used, the extracted
    parameters do not have a name, so they are put into the HTTP request with names of param0, param1, param2 etc.

    Multiple matches can be specified for each HTTP verb. In the case there are more than one matching patterns for
    a particular request, the first matching one will be used.
    """
    def __init__(self):
        self.java_obj = org.vertx.java.core.http.RouteMatcher()

    def __call__(self, data):
        self.input(data)

    def input(self, request):
        """This method is called to provide the matcher with data.

        Keyword arguments:
        @param request: input request to the parser.
        """
        self.java_obj.handle(request._to_java_request())

    def get(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP GET

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.

        Keyword arguments:
        @param pattern: pattern to match
        @param handler: handler for match
        """
        if len(args) > 0:
            self.java_obj.get(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapget(handler):
                self.java_obj.get(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapget

    def put(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP PUT

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.

        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.put(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapput(handler):
                self.java_obj.put(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapput

    def post(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP POST

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.post(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrappost(handler):
                self.java_obj.post(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrappost
    
    def delete(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP DELETE

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
               
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.delete(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapdelete(handler):
                self.java_obj.delete(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapdelete

    def options(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP OPTIONS

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler"""
        if len(args) > 0:
            self.java_obj.options(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapoptions(handler):
                self.java_obj.options(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapoptions

    def head(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP HEAD

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.head(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wraphead(handler):
                self.java_obj.head(pattern, HttpServerRequestHandler(handler))
                return handler
            return wraphead

    def trace(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP TRACE

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """ 
        if len(args) > 0:
            self.java_obj.trace(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wraptrace(handler):
                self.java_obj.trace(pattern, HttpServerRequestHandler(handler))
                return handler
            return wraptrace

    def patch(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP PATCH

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.patch(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrappatch(handler):
                self.java_obj.patch(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrappatch

    def connect(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP CONNECT

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.connect(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapconnect(handler):
                self.java_obj.connect(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapconnect

    def all(self, pattern, *args):
        """Specify a handler that will be called for any matching HTTP request

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler"""
        if len(args) > 0:
            self.java_obj.all(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapall(handler):
                self.java_obj.all(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapall

    def get_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP GET

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.

        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.getWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapget_re(handler):
                self.java_obj.getWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapget_re

    def put_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP PUT

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
    
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.putWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapput_re(handler):
                self.java_obj.putWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapput_re

    def post_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP POST

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.

        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.postWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrappost_re(handler):
                self.java_obj.postWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrappost_re

    def delete_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP DELETE

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.deleteWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapdelete_re(handler):
                self.java_obj.deleteWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapdelete_re

    def options_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP OPTIONS

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """ 
        if len(args) > 0:
            self.java_obj.optionsWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapoptions_re(handler):
                self.java_obj.optionsWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapoptions_re

    def head_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP HEAD

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.headWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wraphead_re(handler):
                self.java_obj.headWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wraphead_re

    def trace_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP TRACE

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """ 
        if len(args) > 0:
            self.java_obj.traceWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wraptrace_re(handler):
                self.java_obj.traceWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wraptrace_re

    def patch_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP PATCH

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.patchWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrappatch_re(handler):
                self.java_obj.patchWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrappatch_re

    def connect_re(self, pattern, *args):
        """Specify a handler that will be called for a matching HTTP CONNECT

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """
        if len(args) > 0:
            self.java_obj.connectWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapconnect_re(handler):
                self.java_obj.connectWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapconnect_re

    def all_re(self, pattern, *args):
        """Specify a handler that will be called for any matching HTTP request

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.
           
        Keyword arguments:
        @param pattern: pattern to match
        @param handler: http server request handler
        """ 
        if len(args) > 0:
            self.java_obj.allWithRegEx(pattern, HttpServerRequestHandler(args[0]))
            return self
        else:
            def wrapall_re(handler):
                self.java_obj.allWithRegEx(pattern, HttpServerRequestHandler(handler))
                return handler
            return wrapall_re

    def no_match(self, handler):
        """Specify a handler that will be called when nothing matches
        Default behaviour is to return a 404

        This method can be called either as a normal instance method or
        used as a decorator to a request handler. If decorating a handler
        the decorator accepts a single pattern argument.

        Keyword arguments:
        @param handler: http server request handler"""
        self.java_obj.noMatch(HttpServerRequestHandler(handler))
        return self


class MultiMap(DictMixin, object):
    """A map which can hold multiple values for one name / key"""
    def __init__(self, map):
        self.map = map

    @property
    def size(self):
        """Return the number of names in this instance"""
        return self.map.size()

    def __getitem__(self, key):
        """Returns the value of with the specified name.  If there are
        more than one values for the specified name, the first value is returned.

        @param name The name of the header to search
        @return The first header value or raise a KeyError if there is no such entry
        """
        value = self.map.get(key)
        if (value is None):
            raise KeyError
        return value


    def get_all(self, key):
        """Returns the values with the specified name

        @param name The name to search
        @return A immutable list of values which or KeyError if no entries for the key exist
        """
        values = self.map.getAll(key)
        if values.isEmpty():
            raise KeyError
        return map_from_java(values)

    def add(self, key, value):
        """Adds a new value with the specified name and value.

        @param name The name
        @param value The value being added
        @return self
        """
        self.map.add(key, value)
        return self

    def __setitem__(self, key, value):
        self.map.set(key, value)

    def set(self, key, value):
        """Set a value with the specified name and value.

        @param name The name
        @param value The value being added
        @return self
        """
        self[key] = value
        return self

    def set_all(self, other):
        """Sets all the entries from another MultiMap

        @param other The other MultiMap
        @return self
        """
        self.map.set(other.map)
        return self

    def __delitem__(self, key):
        """Remove the values with the given name

        @param name The name
        @return self
        """
        if self.map.contains(key):
            self.map.remove(key)
        else:
            raise KeyError

    def remove(self, key):
        """Remove the values with the given name

        @param name The name
        @return self
        """
        self.map.remove(key)
        return self

    def keys(self):
        return self.names()

    def contains(self, key):
        """Returns true if an entry with the given name was found"""
        return self.map.contains(key)

    def names(self):
        """Return a Set which holds all names of the entries

        @return The set which holds all names or an empty set if it is empty
        """
        return map_from_java(self.map.names())

    @property
    def is_empty(self):
        """Returns true if the map is empty"""
        return self.map.isEmpty()

    def clear(self):
        """Remove all entries

        @return self
        """
        self.map.clear()
        return self

class HttpServerFileUpload(core.streams.ReadStream):
    """An Upload which was found in the HttpServerMultipartRequest while handling it."""
    def __init__(self, upload):
        self.java_obj = upload

    def stream_to_file_system(self, filename):
        """Stream the content of this upload to the given filename."""
        self.java_obj.streamToFileSystem(filename)
        return self

    @property
    def filename(self):
        """Returns the filename of the attribute"""
        return self.java_obj.filename()

    @property
    def name(self):
        """Returns the filename of the attribute"""
        return self.java_obj.name()

    @property
    def content_type(self):
        """Returns the contentType for the upload"""
        return self.java_obj.contentType()

    @property
    def content_transfer_encoding(self):
        """Returns the contentTransferEncoding for the upload"""
        return self.java_obj.contentTransferEncoding()

    @property
    def charset(self):
        """Returns the charset for the upload"""
        return self.java_obj.charset()

    @property
    def size(self):
        """Returns the charset for the upload"""
        return self.java_obj.size()

