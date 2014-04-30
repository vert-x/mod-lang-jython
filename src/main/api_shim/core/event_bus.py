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

import org.vertx.java.platform.impl.JythonVerticleFactory
import org.vertx.java.core.Handler
import org.vertx.java.core.AsyncResultHandler
import org.vertx.java.core.eventbus.ReplyException
import java.util.UUID

from core.javautils import map_to_vertx, map_from_vertx

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

class EventBus(object):
    """This class represents a distributed lightweight event bus which can encompass multiple vert.x instances.
    It is very useful for otherwise isolated vert.x application instances to communicate with each other.

    The event bus implements a distributed publish / subscribe network.

    Messages are sent to an address. There can be multiple handlers registered against that address.

    All messages sent over the bus are transient. On event of failure of all or part of the event bus messages
    may be lost. Applications should be coded to cope with lost messages, e.g. by resending them, and making application
    services idempotent.

    The order of messages received by any specific handler from a specific sender will match the order of messages
    sent from that sender.

    When sending a message, a reply handler can be provided. If so, it will be called when the reply from the receiver
    has been received.
    """
    handler_dict = {}

    @staticmethod
    def send(address, message, reply_handler=None):
        """Send a message on the event bus

        Keyword arguments:
        @param address: the address to send to
        @param message: The message to send
        @param reply_handler: An optional reply handler.
        It will be called when the reply from a receiver is received.
        """
        EventBus.send_or_pub(True, address, message, None, reply_handler)

    @staticmethod
    def send_with_timeout(address, message, timeout, reply_handler):
        """Send a message on the event bus with a reply timeout

        Keyword arguments:
        @param address: the address to send to
        @param message: The message to send
        @param timeout: A reply timeout
        @param reply_handler: An optional reply handler.
        It will be called when the reply from a receiver is received.
        """
        EventBus.send_or_pub(True, address, message, timeout, reply_handler)

    @staticmethod
    def publish(address, message):
        """Publish a message on the event bus

        Keyword arguments:
        @param address: the address to publish to
        @param message: The message to publish
        """
        EventBus.send_or_pub(False, address, message)

    @staticmethod
    def send_or_pub(send, address, message, timeout=None, reply_handler=None):
        if not address:
            raise RuntimeError("An address must be specified")
        if message is None:
            raise RuntimeError("A message must be specified")
        message = EventBus.convert_msg(message)
        if send:
            if reply_handler != None:
                if timeout is not None:
                    EventBus.java_eventbus().sendWithTimeout(address, message, timeout, AsyncInternalHandler(reply_handler))
                else:
                    EventBus.java_eventbus().send(address, message, InternalHandler(reply_handler))
            else:
                EventBus.java_eventbus().send(address, message)
        else:
            EventBus.java_eventbus().publish(address, message)


    @staticmethod
    def register_handler(address, local_only=False, handler=None):
        """Register a handler.

        Keyword arguments:
        @param address: the address to register for. A single handler can be registered against many addresses.
        @param local_only: if True then handler won't be propagated across cluster
        @param handler: The handler

        @return: id of the handler which can be used in EventBus.unregister_handler
        """
        if handler is None:
            raise RuntimeError("handler is required")
        internal = InternalHandler(handler)
        if local_only:
            EventBus.java_eventbus().registerLocalHandler(address, internal)
        else:
            EventBus.java_eventbus().registerHandler(address, internal)
        id = java.util.UUID.randomUUID().toString()
        EventBus.handler_dict[id] = address, internal
        return id

    @staticmethod
    def handler(address, local_only=False):
        """Decorator for registering a handler.

        Keyword arguments:
        @param address: the address to register for.
        """
        def wrap(handler):
            EventBus.register_handler(address, local_only, handler)
            return handler
        return wrap

    @staticmethod
    def register_simple_handler(local_only=False, handler=None):
        """
        Registers a handler against a uniquely generated address, the address is returned as the id
        received by the handler. A single handler can be registered against many addresses.

        Keyword arguments:
        @param local_only: If Rrue then handler won't be propagated across cluster
        @param handler: The handler

        @return: id of the handler which can be used in EventBus.unregister_handler
        """
        if handler is None:
            raise RuntimeError("Handler is required")
        internal = InternalHandler(handler)
        id = java.util.UUID.randomUUID().toString()
        if local_only:
            EventBus.java_eventbus().registerLocalHandler(id, internal)
        else:
            EventBus.java_eventbus().registerHandler(id, internal)
        EventBus.handler_dict[id] = id, internal
        return id

    @staticmethod
    def unregister_handler(handler_id):
        """Unregisters a handler

        Keyword arguments:
        @param handler_id: the id of the handler to unregister. Returned from EventBus.register_handler
        """
        [address, handler] = EventBus.handler_dict.pop(handler_id)
        EventBus.java_eventbus().unregisterHandler(address, handler)

    @staticmethod
    def convert_msg(message):
        return map_to_vertx(message)

    @staticmethod
    def java_eventbus():
        return org.vertx.java.platform.impl.JythonVerticleFactory.vertx.eventBus()

# Allow the event bus reply timeout to be set directly as
# a property of the event bus.
EventBus.default_reply_timeout = property(lambda: EventBus.java_eventbus().getDefaultReplyTimeout(), lambda x: EventBus.java_eventbus().setDefaultReplyTimeout(x))

class InternalHandler(org.vertx.java.core.Handler):
    def __init__(self, handler):
        self.handler = handler

    def handle(self, message):
        self.handler(Message(message))

class AsyncInternalHandler(org.vertx.java.core.AsyncResultHandler):
    def __init__(self, handler):
        self.handler = handler

    def handle(self, result):
        if result.failed():
            self.handler(ReplyError(result.cause()), None)
        else:
            self.handler(None, Message(result.result()))
  
class Message(object):
    """Represents a message received from the event bus"""
    def __init__(self, message):
        self.java_obj = message
        self.body = map_from_vertx(message.body())

    @property
    def address(self):
        return self.java_obj.address()

    def reply(self, reply, handler=None):
        """Reply to this message. If the message was sent specifying a receipt handler, that handler will be
        called when it has received a reply. If the message wasn't sent specifying a receipt handler
        this method does nothing.

        Keyword arguments:
        @param reply: message to send as reply
        @param handler: the reply handler 
        """
        reply = EventBus.convert_msg(reply)
        if handler is None:
            self.java_obj.reply(reply)
        else:
            self.java_obj.reply(reply, InternalHandler(handler))

class ReplyError(Exception):
    """An event bus reply error."""
    TIMEOUT = 0
    NO_HANDLERS = 1
    RECIPIENT_FAILURE = 2

    def __init__(self, exception):
        self.exception = exception

    @property
    def type(self):
        return self.exception.failureType().toInt()
