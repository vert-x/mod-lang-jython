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

import java.net.NetworkInterface
import java.net.InetAddress
import vertx
from test_utils import TestUtils

tu = TestUtils()

tu.check_thread()

peer1 = vertx.create_datagram_socket()
peer2 = vertx.create_datagram_socket()

class DatagramTest(object):

    def test_send_receive(self):
        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        def peer2_listen_handler(err, serv):
            tu.check_thread()
            tu.azzert(err is None)
            tu.azzert(serv == peer2)
            buffer = TestUtils.gen_buffer(128)

            @peer2.data_handler
            def data_handler(data):
                tu.check_thread()
                tu.azzert(TestUtils.buffers_equal(buffer, data.data))
                tu.test_complete()


            def send_handler(err, result):
                tu.check_thread()
                tu.azzert(err is None)
                tu.azzert(result == peer1)

            peer1.send('127.0.0.1', 1234, buffer, send_handler)

        peer2.listen(1234, '127.0.0.1', peer2_listen_handler)

    def test_listen_host_port(self):
        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        def peer2_listen_handler(err, serv):
            tu.check_thread()
            tu.azzert(err is None)
            tu.azzert(serv == peer2)
            tu.test_complete()

        peer2.listen(1234, '127.0.0.1', peer2_listen_handler)

    def test_listen_port(self):
        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        def peer2_listen_handler(err, serv):
            tu.check_thread()
            tu.azzert(err is None)
            tu.azzert(serv == peer2)
            tu.test_complete()

        peer2.listen(1234, handler=peer2_listen_handler)

    def test_listen_port_multiple_times(self):
        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        def peer2_listen_handler(err, serv):
            tu.check_thread()
            tu.azzert(err is None)
            tu.azzert(serv == peer2)

            def listen_handler(err, serv):
                tu.check_thread()
                tu.azzert(err is not None)
                tu.azzert(serv is None)
                tu.test_complete()
            peer2.listen(1234, handler=listen_handler)

        peer2.listen(1234, handler=peer2_listen_handler)

    def test_echo(self):
        @peer1.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        buffer = TestUtils.gen_buffer(128)

        def peer2_listen_handler(err, sock):
            @peer2.data_handler
            def data_handler(data):
                tu.check_thread()
                tu.azzert(TestUtils.buffers_equal(buffer, data.data))

                def send_handler(err, sock):
                    tu.check_thread()
                    tu.azzert(err is None)
                    tu.azzert(sock == peer2)

                peer2.send('127.0.0.1', 1235, data.data, send_handler)


            def peer1_listen_handler(err, sock):
                @peer1.data_handler
                def data_handler(data):
                    tu.check_thread()
                    tu.azzert(TestUtils.buffers_equal(buffer, data.data))
                    tu.test_complete()

                def send_handler(err, sock):
                    tu.check_thread()
                    tu.azzert(err is None)
                    tu.azzert(sock ==  peer1)

                peer1.send('127.0.0.1', 1234, buffer, send_handler)
            peer1.listen(1235, '127.0.0.1', peer1_listen_handler)

        peer2.listen(1234, '127.0.0.1', peer2_listen_handler)

    def test_send_after_close_fails(self):
        @peer1.close
        def close_handler():
            tu.check_thread()

            def send_handler(err, sock):
                tu.check_thread()
                tu.azzert(err is not None)
                tu.azzert(sock is None)

                @peer2.close
                def close_handler():
                    tu.check_thread()

                    def send_handler(err, sock):
                        tu.check_thread()
                        tu.azzert(err is not None)
                        tu.azzert(sock is None)
                        tu.test_complete()

                    peer2.send_str('127.0.0.1', 1234, 'test', handler=send_handler)
            peer1.send_str('127.0.0.1', 1234, 'test', handler=send_handler)

    def test_broadcast(self):
        @peer2.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        @peer1.exception_handler
        def exception_handler(err):
            tu.azzert(False)

        peer1.broadcast = True
        peer2.broadcast = True

        def listen_handler(err, sock):
            tu.azzert(err is None)
            tu.azzert(sock == peer2)
            buffer = TestUtils.gen_buffer(128)

            @peer2.data_handler
            def data_handler(data):
                tu.check_thread()
                tu.azzert(TestUtils.buffers_equal(buffer, data.data))
                tu.test_complete()

            def send_handler(err, sock):
                tu.check_thread()
                tu.azzert(err is None)
                tu.azzert(sock == peer1)

            peer1.send('255.255.255.255', 1234, buffer, send_handler)

        peer2.listen(1234, handler=listen_handler)

    def test_configure(self):
        tu.azzert(peer1.broadcast == False)
        peer1.broadcast = True
        tu.azzert(peer1.broadcast)

        tu.azzert(peer1.multicast_loopback_mode)
        peer1.multicast_loopback_mode = False
        tu.azzert(peer1.multicast_loopback_mode == False)

        #tu.azzert(peer1.multicast_network_interface is None)
        #iface = java.net.NetworkInterface.getByInetAddress(java.net.InetAddress.getLoopbackAddress())
        #peer1.set_multicast_network_interface(iface.getName())
        #print peer1.multicast_network_interface
        #print iface.getName()
        #tu.azzert(peer1.multicast_network_interface == iface.getName())

        tu.azzert(peer1.reuse_address == False)
        peer1.reuse_address = True
        tu.azzert(peer1.reuse_address)

        tu.azzert(peer1.multicast_time_to_live != 2)
        peer1.multicast_time_to_live = 2
        tu.azzert(peer1.multicast_time_to_live == 2)

        tu.test_complete()

def vertx_stop():
    tu.unregister_all()
    if peer1 is not None:
        def close_handler():
            if peer2 is not None:
                def close_handler():
                    tu.app_stopped()
                peer2.close(close_handler)
            else:
                tu.app_stopped()

        peer1.close(close_handler)

    elif peer2 is not None:
        def close_handler():
            tu.app_stopped()
        peer2.close(close_handler)
    else:
        tu.app_stopped()

    

tu.register_all(DatagramTest())
tu.app_ready()
