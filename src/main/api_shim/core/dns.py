# Copyright 2013 the original author or authors.
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

from core.handlers import AsyncHandler
from java import net
from jarray import zeros

class DnsClient():

    def __init__(self, *args):
        addresses = zeros(len(args), net.InetSocketAddress)
        for item in args:
            self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createDnsClient(net.InetSocketAddress(item[0], item[1]))
            #addresses.append(net.InetSocketAddress(item[0], item[1]))

        # TODO: Why does this not work ????
        #self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createDnsClient(addresses)

    def lookup(self, name, handler):
        self.java_obj.lookup(name, AsyncHandler(handler, self.address_converter))
        return self

    def lookup_4(self, name, handler):
        self.java_obj.lookup4(name, AsyncHandler(handler, self.address_converter))
        return self

    def lookup_6(self, name, handler):
        self.java_obj.lookup6(name, AsyncHandler(handler, self.address_converter))
        return self

    def resolve_a(self, name, handler):
        self.java_obj.resolveA(name, AsyncHandler(handler, self.address_array_converter))
        return self

    def resolve_aaaa(self, name, handler):
        self.java_obj.resolveAAAA(name, AsyncHandler(handler, self.address_array_converter))
        return self

    def resolve_cname(self, name, handler):
        self.java_obj.resolveCNAME(name, AsyncHandler(handler))
        return self

    def resolve_txt(self, name, handler):
        self.java_obj.resolveTXT(name, AsyncHandler(handler))
        return self

    def resolve_mx(self, name, handler):
        def converter(array):
            def record_converter(record):
                return MxRecord(record)

            return map(record_converter, array)

        self.java_obj.resolveMX(name, AsyncHandler(handler, converter))
        return self

    def resolve_ptr(self, name, handler):
        self.java_obj.resolvePTR(name, AsyncHandler(handler))
        return self

    def resolve_ns(self, name, handler):
        self.java_obj.resolveNS(name, AsyncHandler(handler))
        return self

    def resolve_srv(self, name, handler):
        def converter(array):
            def record_converter(record):
                return SrvRecord(record)

            return map(record_converter, array)

        self.java_obj.resolveSRV(name, AsyncHandler(handler, converter))
        return self

    def reverse_lookup(self, name, handler):
        self.java_obj.reverseLookup(name, AsyncHandler(handler, self.host_converter))
        return self

    def address_converter(self, addr):
        return addr.getHostAddress()

    def host_converter(self, addr):
        return addr.getHostName()

    def address_array_converter(self, array):
        return map(self.address_converter, array)

class MxRecord():
    def __init__(self, obj):
        self.java_obj = obj;

    @property
    def priority(self):
        """
        """
        return self.java_obj.priority()

    @property
    def name(self):
        """
        """
        return self.java_obj.name()

class SrvRecord():
    def __init__(self, obj):
        self.java_obj = obj;

    @property
    def priority(self):
        """
        """
        return self.java_obj.priority()

    @property
    def name(self):
        """
        """
        return self.java_obj.name()

    @property
    def weight(self):
        """
        """
        return self.java_obj.weight()

    @property
    def port(self):
        """
        """
        return self.java_obj.port()

    @property
    def protocol(self):
        """
        """
        return self.java_obj.protocol()


    @property
    def service(self):
        """
        """
        return self.java_obj.service()

    @property
    def target(self):
        """
        """
        return self.java_obj.target()