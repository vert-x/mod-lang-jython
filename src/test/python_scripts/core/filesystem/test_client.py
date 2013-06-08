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

from test_utils import TestUtils
from core.buffer import Buffer

import vertx

tu = TestUtils()
fs = vertx.file_system()

FILEDIR = "python-test-output"

tu.check_thread()

def setup(setup_func):
    def mkdir_handler(err, result):
        setup_func()
    def exists_handler(err, exists):
        if exists:
            def delete_handler(err, result):
                fs.mkdir(FILEDIR, handler=mkdir_handler)
            fs.delete_recursive(FILEDIR, delete_handler)
        else:
            fs.mkdir(FILEDIR, handler=mkdir_handler)
    fs.exists(FILEDIR, exists_handler)

class FileSystemTest(object):

    def test_copy(self):
        filename = FILEDIR + "/test-file.txt"
        tofile = FILEDIR + "/to-file.txt"
        def create_file_handler(err, res):
            tu.check_thread()
            def copy_handler(err, res):
                tu.check_thread()
                tu.azzert(err == None)
                tu.test_complete()
            fs.copy(filename, tofile, copy_handler)
        fs.create_file(filename, handler=create_file_handler)
  

    def test_stats(self):
        filename = FILEDIR + "/test-file.txt"
        def create_file_handler(err, stats):
            tu.check_thread()
            def props_handler(err, stats):
                tu.check_thread()
                tu.azzert(err == None)
#                print "creation time %s"% stats.creation_time
#                print "last access time %s"% stats.last_access_time
#                print "last modification time %s"% stats.last_modified_time
#                print "directory? %s"% stats.directory
#                print "regular file? %s"% stats.regular_file
#                print "symbolic link? %s"% stats.symbolic_link
#                print "other? %s"% stats.other
#                print "size %s"% stats.size
                tu.azzert(stats.regular_file)
                tu.test_complete()
            fs.props(filename, props_handler)
        fs.create_file(filename, handler=create_file_handler)

    def test_async_file(self):
        def open_handler(err, file):
            tu.check_thread()
            tu.azzert(err == None)
            num_chunks = 100;
            chunk_size = 1000;
            tot_buff = Buffer.create()
            self.written = 0
            for i in range(0, num_chunks):
                buff = TestUtils.gen_buffer(chunk_size)
                tot_buff.append_buffer(buff)
                def write_handler(err, res):
                    tu.check_thread()
                    self.written += 1
                    if self.written == num_chunks:
                      # all written
                      tot_read = Buffer.create()
                      self.read = 0
                      for j in range(0, num_chunks):
                        pos = j * chunk_size
                        def read_handler(err, buff):
                            tu.check_thread
                            tu.azzert(err == None)
                            self.read += 1
                            if self.read == num_chunks:
                                # all read
                                tu.azzert(TestUtils.buffers_equal(tot_buff, tot_read))
                                def close_handler(err, res):
                                    tu.check_thread()
                                    tu.test_complete()
                                file.close(close_handler)
                        file.read_at_pos(tot_read, pos, pos, chunk_size, read_handler)
                file.write_at_pos(buff, i * chunk_size, write_handler)
        fs.open(FILEDIR + "/somefile.txt", handler=open_handler)
                

    def test_async_file_streams(self):
        filename = FILEDIR + "/somefile.txt"
        def open_handler(err, file):
            tu.check_thread()
            tu.azzert(err == None)
            num_chunks = 100;
            chunk_size = 1000;
            tot_buff = Buffer.create()
            for i in range(0, num_chunks):
                buff = TestUtils.gen_buffer(chunk_size)
                tot_buff.append_buffer(buff)
                file.write(buff)
            def close_handler(err, file):
                def open_handler2(err, file):
                    tu.check_thread()
                    tu.azzert(err == None)
                    read_stream = file
                    tot_read = Buffer.create()
                    def data_handler(data):
                        tot_read.append_buffer(data)  
                    read_stream.data_handler(data_handler)
                    def end_handler():
                        tu.azzert(TestUtils.buffers_equal(tot_buff, tot_read))
                        tu.check_thread
                        def close_handler2(err, result):
                            tu.check_thread()
                            tu.test_complete()
                        file.close(close_handler2)
                    read_stream.end_handler(end_handler)
                fs.open(filename, handler=open_handler2)
            
            file.close(close_handler)
        fs.open(filename, handler=open_handler)

def vertx_stop():
    tu.check_thread()
    fs.delete_recursive_sync(FILEDIR)
    tu.unregister_all()
    tu.app_stopped()


tu.register_all(FileSystemTest())
setup(tu.app_ready)
