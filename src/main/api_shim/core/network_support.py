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

__author__ = 'Norman Maurer'
__email__ = 'nmaurer@redhat.com'

class NetworkSupport(object):
    """Mixin module that provides all the common network params that can be set."""

    def set_send_buffer_size(self, bytes):
        """Set the TCP send buffer size.

        Keyword arguments:
        @param bytes: The size in bytes.

        return a reference to self so invocations can be chained
        """
        self.java_obj.setSendBufferSize(bytes)
        return self

    def get_send_buffer_size(self):
        return self.java_obj.getSendBufferSize()

    send_buffer_size = property(get_send_buffer_size, set_send_buffer_size)

    def set_receive_buffer_size(self, bytes):
        """Set the TCP receive buffer size.

        Keyword arguments:
        @param bytes: The size in bytes.

        return a reference to self so invocations can be chained
        """
        self.java_obj.setReceiveBufferSize(bytes)
        return self

    def get_receive_buffer_size(self):
        return self.java_obj.getReceiveBufferSize()

    receive_buffer_size = property(get_receive_buffer_size, set_receive_buffer_size)

    def set_reuse_address(self, val):
        """Set the TCP reuse address setting.

        Keyword arguments:
        @param val: If true, then TCP reuse address will be enabled.
        @return: a reference to self so invocations can be chained
        """
        self.java_obj.setReuseAddress(val)
        return self

    def get_reuse_address(self):
        return self.java_obj.isReuseAddress()

    reuse_address = property(get_reuse_address, set_reuse_address)

    def set_traffic_class(self, val):
        """Set the TCP traffic class setting.

        Keyword arguments:
        @param val: The TCP traffic class setting.

        return a reference to self so invocations can be chained
        """
        self.java_obj.setTrafficClass(val)
        return self

    def get_traffic_class(self):
        return self.java_obj.getTrafficClass()

    traffic_class = property(get_traffic_class, set_traffic_class)


