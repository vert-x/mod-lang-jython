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
import org.vertx.testtools.TestDnsServer
from test_utils import TestUtils

tu = TestUtils()
tu.check_thread()
logger = vertx.logger()
server = None

# This is just a basic test. Most testing occurs in the Java tests
class DnsClientTest(object):

    def prepare_dns(self, server):
        server.start()
        server = server
        return vertx.create_dns_client(('127.0.0.1', server.getTransports()[0].getAcceptor().getLocalAddress().getPort()))

    def test_resolve_a(self):
        ip = '10.0.0.1'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(ip == result[0])
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveA(ip))
        client.resolve_a('vertx.io', handler)

    def test_resolve_aaaa(self):
        ip = '::1'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert('0:0:0:0:0:0:0:1' == result[0])
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveAAAA(ip))
        client.resolve_aaaa('vertx.io', handler)

    def test_resolve_mx(self):
        prio = 10
        name = 'mail.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(prio == result[0].priority)
            tu.azzert(name == result[0].name)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveMX(prio, name))
        client.resolve_mx('vertx.io', handler)

    def test_resolve_txt(self):
        txt = 'Vert.x rocks'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(txt == result[0])
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveTXT(txt))
        client.resolve_txt('vertx.io', handler)

    def test_resolve_ns(self):
        ns = 'ns.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(ns == result[0])
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveNS(ns))
        client.resolve_ns('vertx.io', handler)

    def test_resolve_cname(self):
        cname = 'cname.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(cname == result[0])
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveCNAME(cname))
        client.resolve_cname('vertx.io', handler)

    def test_resolve_ptr(self):
        ptr = 'ptr.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ptr == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolvePTR(ptr))
        client.resolve_ptr('10.0.0.1.in-addr.arpa', handler)

    def test_resolve_srv(self):
        priority = 10
        weight = 1
        port = 80
        target = 'vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(len(result) == 1)
            tu.azzert(priority == result[0].priority)
            tu.azzert(weight == result[0].weight)
            tu.azzert(port == result[0].port)
            tu.azzert(target == result[0].target)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testResolveSRV(priority, weight, port, target))
        client.resolve_srv('vertx.io', handler)

    def test_lookup_6(self):
        ip = '0:0:0:0:0:0:0:1'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ip == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testLookup6())
        client.lookup('vertx.io', handler)

    def test_lookup_4(self):
        ip = '10.0.0.1'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ip == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testLookup4(ip))
        client.lookup('vertx.io', handler)

    def test_lookup(self):
        ip = '10.0.0.1'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ip == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testLookup4(ip))
        client.lookup('vertx.io', handler)

    def test_lookup_non_existing(self):
        def handler(err, result):
            tu.azzert(result is None)
            tu.azzert(3 == err.code().code())
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testLookupNonExisting())
        client.lookup('notexists.vertx.io', handler)

    def test_reverse_lookup_ipv4(self):
        ptr = 'ptr.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ptr == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testReverseLookup(ptr))
        client.reverse_lookup('10.0.0.1', handler)

    def test_reverse_lookup_ipv6(self):
        ptr = 'ptr.vertx.io'
        def handler(err, result):
            tu.azzert(err is None)
            tu.azzert(ptr == result)
            tu.test_complete()

        client = self.prepare_dns(org.vertx.testtools.TestDnsServer.testReverseLookup(ptr))
        client.reverse_lookup('::1', handler)

def vertx_stop():
    if server is not None:
        server.stop()
    tu.check_thread()
    tu.unregister_all()
    tu.app_stopped()


tu.register_all(DnsClientTest())
tu.app_ready()
