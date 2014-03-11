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
from java.net import InetSocketAddress
from java.util import ArrayList

__author__ = "Norman Maurer"
__email__ = "nmaurer@redhat.com"
class DnsClient():
    """Provides a way to asynchronous lookup informations from DNS-Servers."""
    def __init__(self, *args):
        addresses = ArrayList(len(args))
        for item in args:
            addresses.add(InetSocketAddress(item[0], item[1]))

        self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.createDnsClient(addresses)

    def lookup(self, name, handler):
        """Try to lookup the A (ipv4) or AAAA (ipv6) record for the given name. The first found will be used.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.lookup(name, AsyncHandler(handler, self.__address_converter))
        return self

    def lookup_4(self, name, handler):
        """Try to lookup the A (ipv4) record for the given name.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.lookup4(name, AsyncHandler(handler, self.__address_converter))
        return self

    def lookup_6(self, name, handler):
        """Try to lookup the AAAA (ipv6) record for the given name.

            Keyword arguments:
            @param name:    The name to resolve
            @param handler: The handler to notify once the response was received or a failure was detected
            @return:        Itself for method-chaining.
        """
        self.java_obj.lookup6(name, AsyncHandler(handler, self.__address_converter))
        return self

    def resolve_a(self, name, handler):
        """Try to resolve all A records for the given name. The handler will get notified with an array hold them.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolveA(name, AsyncHandler(handler, self.__address_array_converter))
        return self

    def resolve_aaaa(self, name, handler):
        """Try to resolve all AAAA records for the given name. The handler will get notified with an array hold them.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolveAAAA(name, AsyncHandler(handler, self.__address_array_converter))
        return self

    def resolve_cname(self, name, handler):
        """Try to resolve all CNAME records for the given name. The handler will get notified with an array hold them.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolveCNAME(name, AsyncHandler(handler))
        return self

    def resolve_txt(self, name, handler):
        """Try to resolve all TXT records for the given name. The handler will get notified with an array hold them.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolveTXT(name, AsyncHandler(handler))
        return self

    def resolve_mx(self, name, handler):
        """Try to resolve all MX records for the given name. The handler will get notified with an array hold them.
        The MxRecord's are sorted based on their priority

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        def converter(array):
            def record_converter(record):
                return MxRecord(record)

            return map(record_converter, array)

        self.java_obj.resolveMX(name, AsyncHandler(handler, converter))
        return self

    def resolve_ptr(self, name, handler):
        """Try to resolve the PTR record for the given name.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolvePTR(name, AsyncHandler(handler))
        return self

    def resolve_ns(self, name, handler):
        """Try to resolve all NS records for the given name. The handler will get notified with an array hold them.

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.resolveNS(name, AsyncHandler(handler))
        return self

    def resolve_srv(self, name, handler):
        """Try to resolve all SRV records for the given name. The handler will get notified with an array hold them.
        The SrvRecord's are sorted based on their priority

        Keyword arguments:
        @param name:    The name to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        def converter(array):
            def record_converter(record):
                return SrvRecord(record)

            return map(record_converter, array)

        self.java_obj.resolveSRV(name, AsyncHandler(handler, converter))
        return self

    def reverse_lookup(self, ip, handler):
        """ Try to do a reverse lookup of an ipaddress. This is basically the same as doing trying to resolve a PTR record
        but allows you to just pass in the ipaddress and not a valid ptr query string.

        Keyword arguments:
        @param ip:      The ip to resolve
        @param handler: The handler to notify once the response was received or a failure was detected
        @return:        Itself for method-chaining.
        """
        self.java_obj.reverseLookup(ip, AsyncHandler(handler, self.__host_converter))
        return self

    def __address_converter(self, addr):
        return addr.getHostAddress()

    def __host_converter(self, addr):
        return addr.getHostName()

    def __address_array_converter(self, array):
        return map(self.__address_converter, array)

class MxRecord():
    """ Represent a Mail-Exchange-Record (MX) which was resolved for a domain.
    """
    def __init__(self, obj):
        self.java_obj = obj

    @property
    def priority(self):
        """ The priority of the MX record.
        """
        return self.java_obj.priority()

    @property
    def name(self):
        """ The name of the MX record
        """
        return self.java_obj.name()

class SrvRecord():
    """ Represent a Service-Record (SRV) which was resolved for a domain.
    """
    def __init__(self, obj):
        self.java_obj = obj

    @property
    def priority(self):
        """ Returns the priority for this service record.
        """
        return self.java_obj.priority()

    @property
    def name(self):
        """ Returns the name for the server being queried.
        """
        return self.java_obj.name()

    @property
    def weight(self):
        """ Returns the weight of this service record.
        """
        return self.java_obj.weight()

    @property
    def port(self):
        """ Returns the port the service is running on.
        """
        return self.java_obj.port()

    @property
    def protocol(self):
        """ Returns the protocol for the service being queried (i.e. "_tcp").
        """
        return self.java_obj.protocol()


    @property
    def service(self):
        """ Returns the service's name (i.e. "_http").
        """
        return self.java_obj.service()

    @property
    def target(self):
        """ Returns the name of the host for the service.
        """
        return self.java_obj.target()