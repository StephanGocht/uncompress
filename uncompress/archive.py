from collections import namedtuple
import zipfile
import tarfile

import gzip
import lzma
import bz2

import io
from pathlib import Path

class register_archive:
    def __init__(self, ending):
        self.ending = ending

    def __call__(self, f):
        registered_archives[self.ending] = f
        return f

FileInfo = namedtuple('FileInfo', "name is_file")

class Archive():
    registered_archives = list()

    @staticmethod
    def register_archive(a):
        Archive.registered_archives.append(a)

    @staticmethod
    def open(archive):
        a = None
        for archive_cls in Archive.registered_archives:
            try:
                a = archive_cls(archive)
            except UnsupportedArchive as e:
                # reset if file object, do nothing otherwise
                try:
                    archive.seek(0)
                except AttributeError:
                    pass
            else:
                break

        if a is None:
            raise UnsupportedArchive();

        return a

    def list_files(self):
        return [x.name for x in self.infolist() if x.is_file]

    def list(self):
        return [x.name for x in self.infolist()]

    def __init__(self, file):
        raise NotImplementedError()

    def infolist():
        raise NotImplementedError()

    def read(file_name):
        raise NotImplementedError()

    def close():
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

class UnsupportedArchive(RuntimeError):
    pass

@Archive.register_archive
class ZipWrapper(Archive):
    def __init__(self, file):
        try:
            self.zip = zipfile.ZipFile(file)
        except zipfile.BadZipFile as e:
            raise UnsupportedArchive(e)

    def infolist(self):
        return  [FileInfo(x.filename, not x.is_dir()) for x in self.zip.infolist()]

    def read(self, file_name):
        bytes_ = self.zip.read(file_name)
        return io.BufferedReader(io.BytesIO(bytes_))

    def close(self):
        self.zip.close()

@Archive.register_archive
class TarWrapper(Archive):
    def __init__(self, file):
        try:
            try:
                self.tar = tarfile.open(fileobj = file)
            except AttributeError as e:
                self.tar = tarfile.TarFile(file)
        except tarfile.ReadError as e:
            raise UnsupportedArchive(e)

    def infolist(self):
        return [FileInfo(x.name, x.isfile()) for x in self.tar.getmembers()]

    def read(self, file_name):
        return self.tar.extractfile(file_name)

    def close(self):
        self.tar.close()

class ArchiveOfCompressedFiles(Archive):
    registered_compressions = list()
    registered_endings = set()

    @staticmethod
    def register_compression(endings):
        def register(f):
            ArchiveOfCompressedFiles.registered_compressions.append(f)
            return f

        for x in endings:
            ArchiveOfCompressedFiles.registered_endings.add(x)

        return register

    @staticmethod
    def uncompress(file):
        for compression in ArchiveOfCompressedFiles.registered_compressions:
            try:
                result = compression(file)
                # errors if wrong compression is used are only thrown on
                # read so we try to read a bit
                try:
                    result.peek(1)
                except AttributeError:
                    result.read(1)
                    result.seek(0)
                return result
            except:
                file.seek(0)

        return file

    @staticmethod
    def pure_name(name):
        endings = ArchiveOfCompressedFiles.registered_endings
        path = Path(name)
        while path.suffix[1:] in endings:
            path = path.with_suffix("")

        return str(path)

    def __init__(self, archive):
        self.archive = Archive.open(archive)

    def infolist(self):
        return self.archive.infolist()

    def read(self, file_name):
        return self.uncompress(self.archive.read(file_name))

    def close(self):
        self.archive.close()

ArchiveOfCompressedFiles.register_compression(["bz2"])(bz2.open)
ArchiveOfCompressedFiles.register_compression(["xz"])(lzma.open)
ArchiveOfCompressedFiles.register_compression(["gz"])(gzip.open)