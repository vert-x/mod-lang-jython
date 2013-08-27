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


from core.handlers import AsyncHandler

class DnsClient():

    def __init__(self, **kwargs):
        addresses = java.net.InetSocketAddress[len(kwargs)];

        self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.createHttpServer()
        for item in kwargs.keys():
            t = kwargs[item]
            addresses[i] = java.net.InetSocketAddress(t[0], t[1])

    def lookup(self, name, handler):
        self.java_obj.lookup(name, AsyncHandler(handler))
        return self

    def lookup_4(self, name, handler):
        self.java_obj.lookup4(name, AsyncHandler(handler))
        return self

    def lookup_6(self, name, handler):
        self.java_obj.lookup6(name, AsyncHandler(handler))
        return self

    def resolve_a(self, name, handler):
        self.java_obj.resolveA(name, AsyncHandler(handler))
        return self

    def resolve_aaaa(self, name, handler):
        self.java_obj.resolveAAAA(name, AsyncHandler(handler))
        return self

    def resolve_cname(self, name, handler):
        self.java_obj.resolveCNAME(name, AsyncHandler(handler))
        return self

    def resolve_mx(self, name, handler):
        self.java_obj.resolveMX(name, AsyncHandler(handler))
        return self

    def resolve_ptr(self, name, handler):
        self.java_obj.resolvePTR(name, AsyncHandler(handler))
        return self

    def resolve_ns(self, name, handler):
        self.java_obj.resolveNS(name, AsyncHandler(handler))
        return self

    def resolve_srv(self, name, handler):
        self.java_obj.resolveSRV(name, AsyncHandler(handler))
        return self

    def reverse_lookup(self, name, handler):
        self.java_obj.reverseLookup(name, AsyncHandler(handler))
        return self
