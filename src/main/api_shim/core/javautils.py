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
#

"""
This module defines several functions to ease interfacing with Java code.  

Initially based on resources in the following article http://www.ibm.com/developerworks/java/tutorials/j-jython2/index.html
"""

import sys
from types import TupleType, ListType, DictType
from java.util import (
    Map,
    HashMap,
    Set,
    Collection,
    ArrayList,
    Vector
)
from java.lang import (
    Long,
    Double,
    Integer
)
from core.buffer import Buffer
import org.vertx.java.core.json.JsonObject
import org.vertx.java.core.json.JsonArray
import org.vertx.java.core.buffer.Buffer

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

def map_array_from_java(array):
    """Converts a JsonArray to a list."""
    result = []
    iter = array.iterator()
    while iter.hasNext():
        result.append(map_from_vertx(iter.next()))
    return result

def map_map_from_java(map):
    """Convert a Map to a Dictionary."""
    result = {}
    iter = map.keySet().iterator()
    while iter.hasNext():
        key = iter.next()
        result[map_from_java(key)] = map_from_java(map.get(key))
    return result

def map_object_from_java(obj):
    """Converts a JsonObject to a dictionary."""
    return map_map_from_java(obj.toMap())

def map_buffer_from_java(obj):
    """Converts a Buffer to a Python Buffer."""
    return Buffer(obj)

def map_set_from_java(set_):
    """Convert a Set to a set."""
    result = set()
    iter = set_.iterator()
    while iter.hasNext():
        result.add(map_from_java(iter.next()))
    return result

def map_collection_from_java(coll):
    """Convert a Collection to a List."""
    result = []
    iter = coll.iterator()
    while iter.hasNext():
        result.append(map_from_java(iter.next()))
    return result

def map_from_java(value):
    """Convert a Java type to a Jython type."""
    if value is None:
        return value
    if isinstance(value, Map):
        return map_map_from_java(value)
    elif isinstance(value, Set):
        return map_set_from_java(value)
    elif isinstance(value, Collection):
        return map_collection_from_java(value)
    return value

def map_from_vertx(value):
    """Converts a Vert.x type to a Jython type."""
    if value is None:
        return value
    if isinstance(value, Map):
        return map_map_from_java(value)
    elif isinstance(value, Set):
        return map_set_from_java(value)
    elif isinstance(value, Collection):
        return map_collection_from_java(value)
    elif isinstance(value, org.vertx.java.core.json.JsonObject):
        return map_object_from_java(value)
    elif isinstance(value, org.vertx.java.core.json.JsonArray):
        return map_array_from_java(value)
    elif isinstance(value, org.vertx.java.core.buffer.Buffer):
        return map_buffer_from_java(value)
    return value

def map_seq_to_java(seq):
    """Convert a seqence to a Java ArrayList."""
    result = ArrayList(len(seq))
    for e in seq:
        result.add(map_to_java(e));
    return result

def map_list_to_java(list):
    """Convert a List to a Java ArrayList."""
    result = ArrayList(len(list))
    for e in list:
        result.add(map_to_java(e));
    return result

def map_list_to_java_vector(list):
    """Convert a List to a Java Vector."""
    result = Vector(len(list))
    for e in list:
        result.add(map_to_java(e));
    return result

def map_dict_to_java(dict):
    """Convert a Dictionary to a Java HashMap."""
    result = HashMap()
    for key, value in dict.items():
        result.put(map_to_java(key), map_to_java(value))
    return result

def map_to_java(value):
    """Convert a Jython type to a Java type."""
    if value is None:
        return value
    t = type(value)
    if t in (TupleType, ListType):
        return map_seq_to_java(value)
    elif t == DictType:
        return map_dict_to_java(value)
    return value

def map_to_vertx(value):
    """Converts a Jython type to a Vert.x type."""
    if value is None:
        return value
    if isinstance(value, (list, tuple)):
        return org.vertx.java.core.json.JsonArray(map_seq_to_java(value))
    elif isinstance(value, dict):
        return org.vertx.java.core.json.JsonObject(map_dict_to_java(value))
    elif isinstance(value, Buffer):
        return value._to_java_buffer()
    elif isinstance(value, long):
        return Long(value)
    elif isinstance(value, float):
        return Double(value)
    elif isinstance(value, int):
        return Integer(value)
    return map_to_java(value)

def inetsocketaddress_to_tuple(object):
    return object.getAddress().getHostAddress() , object.getPort()
