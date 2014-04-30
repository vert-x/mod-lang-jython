# Copyright 2011 the original author or authors.
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

import datetime
import core.streams
import org.vertx.java.core.AsyncResultHandler
import org.vertx.java.platform.impl.JythonVerticleFactory

from core.buffer import Buffer
from core.handlers import AsyncHandler

__author__ = "Scott Horn"
__email__ = "scott@hornmicro.com"
__credits__ = "Based entirely on work by Tim Fox http://tfox.org"

class FileProps(object):
    """Represents the properties of a file on the file system"""

    def __init__(self, java_obj):
        self.java_obj = java_obj

    @property
    def creation_time(self):
        """Return [Time] The creation time of the file."""
        return datetime.datetime.fromtimestamp(self.java_obj.creationTime().getTime() / 1000)

    @property
    def last_access_time(self):
        """Return [Time] The last access time of the file."""
        return datetime.datetime.fromtimestamp(self.java_obj.lastAccessTime().getTime() / 1000)        

    @property
    def last_modified_time(self):
        """Return The last modified time of the file."""
        return datetime.datetime.fromtimestamp(self.java_obj.lastModifiedTime().getTime() / 1000)        
    
    @property 
    def directory(self):
        """Return is the file a directory"""
        return self.java_obj.isDirectory()

    @property
    def other(self):
        """Return Is the file some other file type?"""
        return self.java_obj.isOther()

    @property
    def regular_file(self):
        """Returns   Is it a regular file?"""
        return self.java_obj.isRegularFile()

    @property
    def symbolic_link(self): 
        """Returns is it a symbolic link?"""
        return self.java_obj.isSymbolicLink()

    @property
    def size(self):
        """Returns the size of the file, in bytes."""
        return self.java_obj.size()

class FSProps(object):
    """Represents the properties of a file system"""
  
    def __init__(self, java_obj):
        self.java_obj = java_obj

    @property
    def total_space(self):
        """Returns  the total space on the file system, in bytes."""
        return self.java_obj.totalSpace()

    @property
    def unallocated_space(self): 
        """Returns unallocated space on the file system, in bytes."""
        return self.java_obj.unallocatedSpace()

    @property
    def usable_space(self): 
        """Returns usable space on the file system, in bytes."""
        return self.java_obj.usableSpace()

class AsyncFile(core.streams.ReadStream, core.streams.WriteStream):
    """Represents a file on the file-system which can be read from, or written to asynchronously.
    The file is also a read stream and a write stream. This allows the data to be pumped to and from
    other streams, e.g. an HttpClientRequest instance, using the Pump class
    """
    def __init__(self, java_obj):
        self.java_obj = java_obj

    def close(self, handler=None):
        if (handler is None):
            self.java_obj.close()
        else:
            self.java_obj.close(AsyncHandler(handler))


    def write_at_pos(self, buf, position, handler):
        """Write a Buffer to the file, asynchronously.
        When multiple writes are invoked on the same file
        there are no guarantees as to order in which those writes actually occur.

        Keyword arguments:
        @param buffer: the buffer to write
        @param position: the position in the file where to write the buffer. Position is measured in bytes and
        starts with zero at the beginning of the file.
        """

        self.java_obj.write(buf._to_java_buffer(), position, AsyncHandler(handler))
        return self

    def read_at_pos(self, buf, offset, position, length, handler):
        """Reads some data from a file into a buffer, asynchronously.
        When multiple reads are invoked on the same file
        there are no guarantees as to order in which those reads actually occur.

        Keyword arguments  
        @param buffer: the buffer into which the data which is read is written.
        @param offset: the position in the buffer where to start writing the data.
        @param position: the position in the file where to read the data.
        @param length: the number of bytes to read.
        """
        def converter(buf):
            return Buffer(buf)
        self.java_obj.read(buf._to_java_buffer(), offset, position, length, AsyncHandler(handler, converter))
        return self

    def flush(self, handler=None):
        """Flush any writes made to this file to underlying persistent storage, asynchronously.
        If the file was opened with flush set to true then calling this method will have no effect.
        Keyword arguments:

        @param handler: the handler which is called on completion.
        """
        if handler is None:
            Future(self.java_obj.flush())
        else:
            Future(self.java_obj.flush(AsyncHandler(handler)))
        return self


class FileSystem(object):
    """Represents the file-system and contains a broad set of operations for manipulating files.
    An asynchronous and a synchronous version of each operation is provided.
    The asynchronous versions take a handler as a final argument which is
    called when the operation completes or an error occurs. The handler is called
    with two arguments; the first an exception, this will be None if the operation has
    succeeded. The second is the result - this will be None if the operation failed or
    there was no result to return.
    The synchronous versions return the results, or throw exceptions directly."""

    def __init__(self):
        self.java_obj = org.vertx.java.platform.impl.JythonVerticleFactory.vertx.fileSystem()


    def copy(self, frm, to, handler):
        """Copy a file, asynchronously. The copy will fail if from does not exist, or if to already exists.

        Keyword arguments:
        @param frm: path of file to copy
        @param to: path of file to copy to
        @param handler: the handler which is called on completion."""
        self.java_obj.copy(frm, to, AsyncHandler(handler))
        return self

    def copy_sync(self, frm, to):
        """Synchronous version of FileSystem.copy"""
        self.java_obj.copySync(frm, to)
        return self

    def copy_recursive(self, frm, to, handler):
        """Copy a file recursively, asynchronously. The copy will fail if from does not exist, or if to already exists and is not empty.
        If the source is a directory all contents of the directory will be copied recursively, i.e. the entire directory
        tree is copied.

        Keyword arguments:
        @param frm: path of file to copy
        @param to: path of file to copy to
        @param handler: the function to call when complete
        """
        self.java_obj.copy(frm, to, True, AsyncHandler(handler))
        return self

    def copy_recursive_sync(self, frm, to):
        """Synchronous version of FileSystem.copy_recursive"""
        self.copySync(frm, to, True)
        return self

    def move(self, frm, to, handler):
        """Move a file, asynchronously. The move will fail if from does not exist, or if to already exists.

        Keyword arguments:
        @param frm: Path of file to move
        @param to: Path of file to move to
        @param handler: the function to call when complete
        """
        self.java_obj.move(frm, to, AsyncHandler(handler))
        return self

    def move_sync(self, frm, to):
        """Synchronous version of FileSystem.move"""
        self.java_obj.moveSync(frm, to)
        return self

    def truncate(self, path, len, handler):
        """Truncate a file, asynchronously. The move will fail if path does not exist.

        Keyword arguments:
        @param path: Path of file to truncate
        @param len: Length to truncate file to. Will fail if len < 0. If len > file size then will do nothing.
        @param handler: the function to call when complete
        """
        self.java_obj.truncate(path, len, AsyncHandler(handler))
        return self

    def truncate_sync(self, path, len):
        """Synchronous version of FileSystem.truncate"""
        self.java_obj.truncateSync(path, len)
        return self

    def chown(self, path, user, group, handler=None):
        """Change the ownership on a file, asynchronously.

        Keyword arguments:
        @param path: path of file to change ownership
        @param user: the user to which to change
        @param group: the group to which to change
        @param handler: the function to call when complete
        """
        self.java_obj.chown(path, user, group, AsyncHandler(handler))
        return self

    def chown_sync(self, path, user, group):
        """Synchronous version of FileSystem.chown"""
        self.java_obj.chownSync(path, user, group)
        return self

    def chmod(self, path, perms, dir_perms=None, handler=None):
        """Change the permissions on a file, asynchronously. If the file is directory then all contents will also have their permissions changed recursively.

        Keyword arguments:
        @param path: path of file to change permissions
        @param perms: a permission string of the form rwxr-x--- as specified in http://download.oracle.com/javase/7/docs/api/java/nio/file/attribute/PosixFilePermissions.html. This is
        used to set the permissions for any regular files (not directories).
        @param dir_perms: a permission string of the form rwxr-x---. Used to set permissions for regular files.
        @param handler: the function to call when complete
        """
        self.java_obj.chmod(path, perms, dir_perms, AsyncHandler(handler))
        return self

    def chmod_sync(self, path, perms, dir_perms=None):
        """Synchronous version of FileSystem.chmod"""
        self.java_obj.chmodSync(path, perms, dir_perms)
        return self

    def props(self, path, handler):
        """Get file properties for a file, asynchronously.

        Keyword arguments:
        @param path: path to file
        @param handler: the function to call when complete
        """
        def converter(obj):
            return FileProps(obj)

        self.java_obj.props(path, AsyncHandler(handler, converter))
        return self

    def props_sync(self, path):
        """Synchronous version of FileSystem.props"""
        java_obj = self.java_obj.propsSync(path)
        return FileProps(java_obj)

    def lprops(self, path, handler):
        """Obtain properties for the link represented by {@code path}, asynchronously.
        The link will not be followed..

        Keyword arguments:
        @param path: path to file
        @param handler: the function to call when complete
        """
        def converter(obj):
            return FileProps(obj)

        self.java_obj.lprops(path, AsyncHandler(handler, converter))
        return self

    def lprops_sync(self, path):
        """Synchronous version of FileSystem.lprops"""
        java_obj = self.java_obj.lpropsSync(path)
        return FileProps(java_obj)


    def link(self, link, existing, handler):
        """Create a hard link, asynchronously..

        Keyword arguments:
        @param link: path of the link to create.
        @param existing: path of where the link points to.
        @param handler: the function to call when complete
        """
        self.java_obj.link(link, existing, AsyncHandler(handler))
        return self

    def link_sync(self, link, existing):
        """Synchronous version of FileSystem.link"""
        self.java_obj.linkSync(link, existing)
        return self

    def symlink(self, link, existing, handler):
        """Create a symbolic link, asynchronously.

        Keyword arguments:
        @param link: Path of the link to create.
        @param existing: Path of where the link points to.
        @param handler: the function to call when complete
        """
        self.java_obj.symlink(link, existing, AsyncHandler(handler))
        return self

    def symlink_sync(self, link, existing):
        """Synchronous version of FileSystem.symlink"""
        self.java_obj.symlinkSync(link, existing)
        return self

    def unlink(self, link, handler):
        """Unlink a hard link.

        Keyword arguments:
        @param link: path of the link to unlink.
        """
        self.java_obj.unlink(link, AsyncHandler(handler))
        return self

    def unlinkSync(self, link):
        """Synchronous version of FileSystem.unlink"""
        self.java_obj.unlinkSync(link)
        return self

    def read_symlink(self, link, handler):
        """Read a symbolic link, asynchronously. I.e. tells you where the symbolic link points.

        Keyword arguments:
        @param link: path of the link to read.
        @param handler: the function to call when complete
        """
        self.java_obj.readSymlink(link, AsyncHandler(handler))
        return self

    def read_symlink_sync(self, link):
        """Synchronous version of FileSystem.read_symlink"""
        self.java_obj.readSymlinkSync(link)
        return self

    def delete(self, path, handler):
        """Delete a file on the file system, asynchronously.
        The delete will fail if the file does not exist, or is a directory and is not empty.

        Keyword arguments:
        @param path: path of the file to delete.
        @param handler: the function to call when complete
        """
        self.java_obj.delete(path, AsyncHandler(handler))
        return self

    def delete_sync(self, path):
        """Synchronous version of FileSystem.delete"""
        self.java_obj.deleteSync(path)
        return self

    def delete_recursive(self, path, handler):
        """Delete a file on the file system recursively, asynchronously.
        The delete will fail if the file does not exist. If the file is a directory the entire directory contents
        will be deleted recursively.

        Keyword arguments:
        @param path: path of the file to delete.
        @param handler: the function to call when complete
        """
        self.java_obj.delete(path, True, AsyncHandler(handler))
        return self

    def delete_recursive_sync(self, path):
        """Synchronous version of FileSystem.delete_recursive"""
        self.java_obj.deleteSync(path, True)
        return self

    def mkdir(self, path, perms=None, handler=None):
        """Create a directory, asynchronously.
        The create will fail if the directory already exists, or if it contains parent directories which do not already
        exist.

        Keyword arguments:
        @param path: path of the directory to create.
        @param perms: a permission string of the form rwxr-x--- to give directory.
        @param handler: the function to call when complete
        """
        self.java_obj.mkdir(path, perms, AsyncHandler(handler))
        return self

    def mkdir_sync(self, path, perms=None):
        """Synchronous version of FileSystem.mkdir"""
        self.java_obj.mkdirSync(path, perms)
        return self

    def mkdir_with_parents(self, path, perms=None, handler=None):
        """Create a directory, and create all it's parent directories if they do not already exist, asynchronously.
        The create will fail if the directory already exists.

        Keyword arguments:
        @param path: path of the directory to create.
        @param perms: a permission string of the form rwxr-x--- to give the created directory(ies).
        """
        self.java_obj.mkdir(path, perms, True, AsyncHandler(handler))
        return self

    def mkdir_with_parents_sync(self, path, perms=None):
        """Synchronous version of FileSystem.mkdir_with_parents"""
        self.java_obj.mkdirSync(path, perms, True)
        return self

    def read_dir(self, path, filter=None, handler=None):
        """Read a directory, i.e. list it's contents, asynchronously.
        The read will fail if the directory does not exist.

        Keyword arguments:
        @param path: path of the directory to read.
        @param filter: a regular expression to filter out the contents of the directory. If the filter is not nil
        then only files which match the filter will be returned.
        @param handler: the function to call when complete
        """
        self.java_obj.readDir(path, filter, AsyncHandler(handler))
        return self

    def read_dir_sync(self, path, filter=None):
        """Synchronous version of FileSystem.read_dir"""
        self.java_obj.readDirSync(path, filter)
        return self

    def read_file_as_buffer(self, path, handler):
        """Read the contents of an entire file as a Buffer, asynchronously.

        Keyword arguments:
        @param path: path of the file to read.
        @param handler: the function to call when complete
        """
        def converter(buffer):
            return Buffer(buffer)
        self.java_obj.readFile(path, AsyncHandler(handler, converter))
        return self

    def read_file_as_buffer_sync(self, path):
        """Synchronous version of FileSystem.read_file_as_buffer"""
        self.java_obj.readFileSync(path)
        return self

    def write_buffer_to_file(self, path, buffer, handler):
        """Write a  as the entire contents of a file, asynchronously.

        Keyword arguments:
        @param path: path of the file to write.
        @param buffer: the Buffer to write
        @param handler: the function to call when complete
        """
        self.java_obj.writeFile(path, buffer, AsyncHandler(handler))
        return self

    def write_buffer_to_file_sync(self, path, buf):
        """Synchronous version of FileSystem.write_buffer_to_file"""
        self.java_obj.writeFileSync(path, buf)
        return self

    def open(self, path, perms=None, read=True, write=True, create_new=True, flush=False, handler=None):
        """Open a file on the file system, asynchronously.

        Keyword arguments:
        @param path: path of the file to open.
        @param perms: if the file does not exist and create_new is true, then the file will be created with these permissions.
        @param read: open the file for reading?
        @param write: open the file for writing?
        @param create_new: Create the file if it doesn't already exist?
        @param flush: whenever any data is written to the file, flush all changes to permanent storage immediately?
        @param handler: the function to call when complete
        """
        def converter(f):
            return AsyncFile(f)
        self.java_obj.open(path, perms, read, write, create_new, flush, AsyncHandler(handler, converter))
        return self

    def open_sync(self, path, perms=None, read=True, write=True, create_new=True, flush=False):
        """Synchronous version of FileSystem.open"""
        java_obj = self.java_obj.open(path, perms, read, write, create_new, flush)
        return AsyncFile(java_obj)

    def create_file(self, path, perms=None, handler=None):
        """Create a new empty file, asynchronously.

        Keyword arguments:
        @param path: path of the file to create.
        @param perms: the file will be created with these permissions.
        @param handler: the function to call when complete
        """
        self.java_obj.createFile(path, perms, AsyncHandler(handler))
        return self

    def create_file_sync(self, path, perms=None):
        """Synchronous version of FileSystem.create_file"""
        self.java_obj.createFileSync(path, perms)
        return self

    def exists(self, path, handler):
        """Check if  a file exists, asynchronously.

        Keyword arguments:
        @param path: Path of the file to check.
        @param handler: the function to call when complete
        """
        self.java_obj.exists(path, AsyncHandler(handler))
        return self

    def exists_sync(self, path):
        """Synchronous version of FileSystem.exists"""
        return self.java_obj.existsSync(path)

    def fs_props(self, path, handler):
        """Get properties for the file system, asynchronously.

        Keyword arguments:
        @param path: Path in the file system.
        @param handler: the function to call when complete
        """
        def converter(props):
            return FSProps(props)
        self.java_obj.fsProps(path, AsyncHandler(handler, converter))
        return self

    def fs_props_sync(self, path):
        """Synchronous version of FileSystem.fs_props"""
        j_fsprops = self.java_obj.fsPropsSync(path)
        return FSProps(j_fsprops)
