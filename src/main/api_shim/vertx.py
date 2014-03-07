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
This module provides the entry point to the vert.x platform 
"""

import org.vertx.java.platform.impl.JythonVerticleFactory
import java.lang.System
import org.vertx.java.core.json.JsonObject

from core.dns import DnsClient
from core.file_system import FileSystem
from core.datagram import DatagramSocket
from core.http import HttpServer, HttpClient
from core.net import NetServer, NetClient
from core.sock_js import SockJSServer
from core.handlers import TimerHandler, NullDoneHandler, AsyncHandler, NullAsyncHandler
from core.javautils import map_to_java, map_from_java

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

def create_http_server(**kwargs):
    """ Return a HttpServer """
    return HttpServer(org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createHttpServer(), **kwargs)

def create_http_client(**kwargs):
    """ Return a HttpClient """
    return HttpClient(**kwargs)

def create_net_server(**kwargs):
    """ Return a NetServer """
    return NetServer(org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createNetServer(), **kwargs)

def create_net_client(**kwargs):
    """ Return a NetClient """
    return NetClient(**kwargs)

def create_sockjs_server(http_server):
    """ Return a SockJSServer """
    return SockJSServer(http_server)

def create_datagram_socket(ipv4=None):
    """ Return a datagram socket """
    if ipv4 is None:
        return DatagramSocket(org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createDatagramSocket(None))
    elif ipv4:
        return DatagramSocket(org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createDatagramSocket(org.vertx.java.core.datagram.InternetProtocolFamily.Ipv4))
    else:
        return DatagramSocket(org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createDatagramSocket(org.vertx.java.core.datagram.InternetProtocolFamily.Ipv6))

def file_system():
    """ Return the filesystem """
    return FileSystem()

def logger():
    """ Get the logger for the verticle """
    return org.vertx.java.platform.impl.JythonVerticleFactory.container.logger()

def deploy_verticle(main, config=None, instances=1, handler=None):
    """Deploy a verticle. The actual deploy happens asynchronously

    Keyword arguments:
    @param main: the main of the verticle to deploy
    @param config: dict configuration for the verticle
    @param instances: number of instances to deploy
    @param handler: a handler that will be called when deploy has completed

    """
    if config != None:
        config = org.vertx.java.core.json.JsonObject(map_to_java(config))

    if handler != None:
        handler = AsyncHandler(handler)
    org.vertx.java.platform.impl.JythonVerticleFactory.container.deployVerticle(main, config, instances, handler)

def deploy_worker_verticle(main, config=None, instances=1, multi_threaded=False, handler=None):
    """Deploy a worker verticle. The actual deploy happens asynchronously

    Keyword arguments:
    @param main: the main of the verticle to deploy
    @param config: dict configuration for the verticle
    @param instances: the number of instances to deploy
    @param handler: an handler that will be called when deploy has completed
    @param multithreaded: enables multithreaded worker
    """
    if config != None:
        config = org.vertx.java.core.json.JsonObject(map_to_java(config))
    org.vertx.java.platform.impl.JythonVerticleFactory.container.deployWorkerVerticle(main, config, instances, multi_threaded, AsyncHandler(handler))

def deploy_module(module_name, config=None, instances=1, handler=None):
    """Deploy a module. The actual deploy happens asynchronously

    Keyword arguments:
    @param module_name: The name of the module to deploy
    @param config: dict configuration for the module
    @param instances: Number of instances to deploy
    @param handler: an handler that will be called when deploy has completed
    """
    if config != None:
        config = org.vertx.java.core.json.JsonObject(map_to_java(config))
    org.vertx.java.platform.impl.JythonVerticleFactory.container.deployModule(module_name, config, instances, AsyncHandler(handler))

def undeploy_verticle(id, handler=None):
    """Undeploy a verticle

    Keyword arguments:
    @param id: the unique id of the deployment
    @param handler: an handler that will be called when undeploy has completed
    """
    org.vertx.java.platform.impl.JythonVerticleFactory.container.undeployVerticle(id, NullAsyncHandler(handler))

def undeploy_module(id, handler=None):
    """Undeploy a module

    Keyword arguments:
    @param id: the unique id of the module
    @param handler: an handler that will be called when undeploy has completed
    """
    org.vertx.java.platform.impl.JythonVerticleFactory.container.undeployModule(id, NullAsyncHandler(handler))

def config():
    """Get config for the verticle
    @return: dict config for the verticle
    """
    return map_from_java(org.vertx.java.platform.impl.JythonVerticleFactory.container.config().toMap())

def env():
    """Get environment variables for the verticle
    @return: dict containing environment variables
    """
    return map_from_java(java.lang.System.getenv())

def set_timer(delay, handler):
    """Sets a one-shot timer that will fire after a certain delay.

    Keyword arguments:
    @param delay: the delay, in milliseconds
    @param handler: an handler that will be called when the timer fires
    @return: the unique id of the timer
    """
    return java_vertx().setTimer(delay, TimerHandler(handler))

def set_periodic(delay, handler):
    """Sets a periodic timer.

    Keyword arguments:
    @param delay: the period of the timer, in milliseconds
    @param handler: an handler that will be called each time the timer fires
    @return: the unique id of the timer
    """
    return java_vertx().setPeriodic(delay, TimerHandler(handler))

def cancel_timer(id):
    """Cancels a timer.

    Keyword arguments:
    @param id: the id of the timer, as returned from set_timer or set_periodic
    @return: true if the timer was cancelled, false if it wasn't found.
    """
    return java_vertx().cancelTimer(id)

def run_on_context(handler):
    """Put the handler on the event queue for this loop so it will be run asynchronously
    ASAP after this event has been processed

    Keyword arguments:
    @param handler: an handler representing the code that will be run ASAP
    """
    java_vertx().runOnContext(NullDoneHandler(handler))

def current_context():
    return Context(java_vertx().currentContext())

def exit():
    """ Cause the container to exit """
    org.vertx.java.platform.impl.JythonVerticleFactory.container.exit()

def create_dns_client(*args):
    """Create a new dns client
    @param kwargs: tuples which hold (address, port)
    """
    return DnsClient(*args)

def java_vertx():
    return org.vertx.java.platform.impl.JythonVerticleFactory.vertx

class Context():
    """ An HTTP and websockets server """
    def __init__(self, j_context):
        self.j_context = j_context

    def run_on_context(self, handler):
        self.j_context.runOnContext(NullDoneHandler(handler))


