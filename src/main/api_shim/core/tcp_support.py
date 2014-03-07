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

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

import core.network_support

class TCPSupport(core.network_support.NetworkSupport, object):
  """Mixin class that provides all the common TCP params that can be set."""

  def set_tcp_no_delay(self, val):
      """Enable TCP_NO_DELAY

      Keyword arguments:
      @param val: if true TCP_NO_DELAY will be enabled

      return a reference to self so invocations can be chained
      """
      self.java_obj.setTCPNoDelay(val)
      return self

  def get_tcp_no_delay(self):
      return self.java_obj.getTCPNoDelay();

  tcp_no_delay = property(get_tcp_no_delay, set_tcp_no_delay)

  def set_tcp_keep_alive(self, val):
    """Set the TCP keep alive setting.

    Keyword arguments:
    @param val: If true, then TCP keep alive will be enabled.
    
    return a reference to self so invocations can be chained
    """
    self.java_obj.setTCPKeepAlive(val)
    return self

  def get_tcp_keep_alive(self):
    return self.java_obj.getTCPKeepAlive()

  tcp_keep_alive = property(get_tcp_keep_alive, set_tcp_keep_alive)

  def set_so_linger(self, val):
    """Set the TCP so linger setting.

    Keyword arguments:
    @param val: If true, then TCP so linger will be enabled.
    
    return a reference to self so invocations can be chained
    """
    self.java_obj.setSoLinger(val)
    return self

  def get_so_linger(self):
    return self.java_obj.getSoLinger()

  so_linger = property(get_so_linger, set_so_linger)

  def set_use_pooled_buffers(self, val):
    """Set if vert.x should use pooled buffers for performance reasons.
    Doing so will give the best throughput but may need a bit higher memory footprint.

    Keyword arguments:
    @param val: if true pooled buffers will be used.

    return a reference to self so invocations can be chained
    """
    self.java_obj.setUsePooledBuffers(val)
    return self

  def get_use_pooled_buffers(self):
    return self.java_obj.getUsePooledBuffers()

  use_pooled_buffers = property(get_use_pooled_buffers, set_use_pooled_buffers)

class ServerTCPSupport(TCPSupport, object):

  def set_accept_backlog(self, val):
    """Set the accept backlog

    Keyword arguments:
    @param val: set the accept backlog to the value

    return a reference to self so invocations can be chained
    """
    self.java_obj.setAcceptBacklog(val)
    return self

  def get_accept_backlog(self):
    return self.java_obj.getAcceptBacklog()

  accept_backlog = property(get_accept_backlog, set_accept_backlog)
