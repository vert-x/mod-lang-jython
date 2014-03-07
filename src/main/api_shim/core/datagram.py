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

"""
This module adds the datagram support to the python vert.x platform
"""
__author__ = 'Norman Maurer'
__email__ = 'nmaurer@redhat.com'


import org.vertx.java.core.Handler

from core.streams import ReadSupport, DrainSupport, ExceptionSupport
from core.handlers import AsyncHandler, CloseHandler
from core.buffer import Buffer
from core.network_support import NetworkSupport

class DatagramSocket(ReadSupport, DrainSupport, ExceptionSupport,  NetworkSupport, object):

    """A Datagram socket which can be used to send data to remote Datagram servers and receive DatagramPackets .

    Usually you use a Datragram Client to send UDP over the wire. UDP is connection-less which means you are not connected
    to the remote peer in a persistent way. Because of this you have to supply the address and port of the remote peer
    when sending data.

    You can send data to ipv4 or ipv6 addresses, which also include multicast addresses.
    """
    def __init__(self, server, **kwargs):
        self.local_addr = None
        self.java_obj = server
        for item in kwargs.keys():
            setattr(self, item, kwargs[item])

    def send(self, host, port, packet,  handler=None):
        """Write the given buffer to the remote datagram server. The handler will be notified once the
        write completes.

        @param packet:      the buffer to write
        @param host:        the host address of the remote peer
        @param port:        the host port of the remote peer
        @param handler:     the function to notify once the write completes.
        @return self:       itself for method chaining
        """
        def converter(server):
            return self
        self.java_obj.send(packet._to_java_buffer(), host, port, AsyncHandler(handler, converter))
        return self



    def send_str(self, host, port, str, enc = 'UTF-8',  handler=None):
        """Write the given buffer to the remote datagram server. The handler will be notified once the
        write completes.

        @param str:         the string to write
        @param enc:         the charset to use to encode the string to bytes
        @param host:        the host address of the remote peer
        @param port:        the host port of the remote peer
        @param handler:     the function to notify once the write completes.
        @return self:       itself for method chaining
        """
        def converter(server):
            return self
        self.java_obj.send(str, enc, host, port, AsyncHandler(handler, converter))
        return self

    def is_broadcast(self):
        """Get the {@link java.net.StandardSocketOptions#SO_BROADCAST} option."""
        return self.java_obj.isBroadcast()

    def set_broadcast(self, val):
        """Set the {@link java.net.StandardSocketOptions#SO_BROADCAST} option."""
        self.java_obj.setBroadcast(val)
        return self

    broadcast = property(is_broadcast, set_broadcast)

    def is_multicast_loopback_mode(self):
        """Get the {@link java.net.StandardSocketOptions#IP_MULTICAST_LOOP} option.

        @return loopbackmode: True if and only if the loopback mode has been disabled
        """
        return self.java_obj.isMulticastLoopbackMode()

    def set_multicast_loopback_mode(self, val):
        """Set the {@link java.net.StandardSocketOptions#IP_MULTICAST_LOOP} option."""
        self.java_obj.setMulticastLoopbackMode(val)
        return self

    multicast_loopback_mode = property(is_multicast_loopback_mode, set_multicast_loopback_mode)

    def get_multicast_time_to_live(self):
        """Get the {@link java.net.StandardSocketOptions#IP_MULTICAST_TTL} option."""
        return self.java_obj.getMulticastTimeToLive()


    def set_multicast_time_to_live(self, val):
        """Set the {@link java.net.StandardSocketOptions#IP_MULTICAST_TTL} option."""
        self.java_obj.setMulticastTimeToLive(val)
        return self

    multicast_time_to_live = property(get_multicast_time_to_live, set_multicast_time_to_live)

    def get_multicast_network_interface(self):
        """Get the {@link java.net.StandardSocketOptions#IP_MULTICAST_IF} option."""
        self.java_obj.getMulticastNetworkInterface()

    def set_multicast_network_interface(self, val):
        """Set the {@link java.net.StandardSocketOptions#IP_MULTICAST_IF} option."""
        self.java_obj.setMulticastNetworkInterface(val)

    multicast_network_interface = property(get_multicast_network_interface, set_multicast_network_interface)

    def close(self, handler=None):
        """Close the socket asynchronous and notifies the handler once done.

        @param handler: the function to notify once the operation completes
        """
        self.java_obj.close(CloseHandler(handler))

    @property
    def local_address(self):
        """Returns the local address as tuple in form of ('ipaddress', port)"""
        if self.local_addr is None:
            self.local_addr =  self.java_obj.local_address().getAddress().getHostAddress() , self.java_obj.local_address().getPort()
        return self.local_address

    def listen_multicast_group(self, multicast_address, source = None, network_interface = None,  handler = None):
        """Joins a multicast group and so start listen for packets send to it. The handler is notified once the operation completes.

        @param   multicast_address:     the address of the multicast group to join
        @param   source:                the address of the source for which we will listen for mulicast packets
        @param   network_interface:     the network interface on which to listen for packets.
        @param   handler:               then handler to notify once the operation completes
        @return  self:                  returns itself for method-chaining
        """
        def converter(server):
            return self
        if network_interface is not None and source is not None:
            self.java_obj.listenMulticastGroup(multicast_address, network_interface, source, AsyncHandler(handler, converter))
        else:
            self.java_obj.listenMulticastGroup(multicast_address, AsyncHandler(handler, converter))

        return self


    def unlisten_multicast_group(self, multicast_address, source = None, network_interface = None, handler = None):
        """Leaves a multicast group and so stop listen for packets send to it on the given network interface.
        The handler is notified once the operation completes.

        @param   multicast_address:     the address of the multicast group to leave
        @param   source:                the address of the source for which we will stop listen for mulicast packets
        @param   network_interface:     the network interface on which to stop listen for packets.
        @param   handler:               then handler to notify once the operation completes
        @return  self:                  returns itself for method-chaining
        """
        def converter(server):
            return self
        if network_interface is not None and source is not None:
            self.java_obj.unlistenMulticastGroup(multicast_address, network_interface, source, AsyncHandler(handler, converter))
        else:
            self.java_obj.unlistenMulticastGroup(multicast_address, AsyncHandler(handler, converter))

        return self

    def block_multicast_group(self, multicast_address, source_to_block, network_interface = None, handler = None):
        """Block the given source_to_block address for the given multicast_address on the given network_interface.
        The handler is notified once the operation completes.

        @param   multicast_address:     the address for which you want to block the source_to_block
        @param   source_to_block:       the source address which should be blocked. You will not receive an multicast packets
                                        for it anymore.
        @param   network_interface:     the network interface on which the block should be done
        @param   handler:           then handler to notify once the operation completes
        @return  self:              returns itself for method-chaining
        """
        def converter(server):
            return self
        if network_interface is not None:
            self.java_obj.blockMulticastGroup(multicast_address, network_interface, source_to_block, AsyncHandler(handler, converter))
        else:
            self.java_obj.blockMulticastGroup(multicast_address, source_to_block, AsyncHandler(handler, converter))
        return self

    def listen(self, port, address = '0.0.0.0', handler = None):
        """Listen for incoming [DatagramPacket]s on the given address and port.

        @param      port:                the port on which to listen for incoming packets
        @param      address:             the address on which to listen for incoming [DatagramPacket]s
        @param      handler:             the function to notify once the opeation completes.
        @return     self:                itself for method chaining
        """
        def converter(server):
            return self
        self.java_obj.listen(address, port, AsyncHandler(handler, converter))
        return self



    # Set a data handler. As data is read, the handler will be called with the data.
    # @param [Block] hndlr. The data handler
    def data_handler(self, handler):
        """Set a data handler. As data is read, the handler will with the packet that
        was received

        @param handler: the function to notify once the packet was received
        """
        self.java_obj.dataHandler(DatagramPacketHandler(handler))
        return self



class DatagramPacket(object):
    """A received Datagram packet (UDP) which contains the data and information about the sender of the data itself."""
    def __init__(self, packet):
        self.packet = packet
        self.sender_addr = None
        self.buffer = None

    @property
    def sender(self):
        """Returns the address of the sender as tuple in form of ('ipaddress', port)"""
        if self.sender_addr is None:
            self.sender_addr =  self.java_obj.sender().getAddress().getHostAddress() , self.java_obj.sender().getPort()
        return self.sender_addr

    @property
    def data(self):
        """Returns the data as buffer that was received."""
        if self.buffer is None:
            self.buffer = Buffer(self.packet.data())
        return self.buffer

class DatagramPacketHandler(org.vertx.java.core.Handler):
    def __init__(self, handler):
        self.handler = handler

    def handle(self, packet):
        self.handler(DatagramPacket(packet))
