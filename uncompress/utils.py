import argparse
import uncompress
import io

from argparse import ArgumentTypeError as err
import os

# PathType implementation from
# https://mail.python.org/pipermail/stdlib-sig/2015-July/000991.html
# with minor change (added type any)


class PathType(object):
    def __init__(self, exists=True, type='file', dash_ok=True):
        '''exists:
                True: a path that does exist
                False: a path that does not exist, in a valid parent directory
                None: don't care
           type: file, dir, symlink, None, or a function returning True for valid paths
                None: don't care
           dash_ok: whether to allow "-" as stdin/stdout'''

        assert exists in (True, False, None)
        assert type in ('file','dir','symlink','any',None) or hasattr(type,'__call__')

        self._exists = exists
        self._type = type
        self._dash_ok = dash_ok

    def __call__(self, string):
        if string=='-':
            # the special argument "-" means sys.std{in,out}
            if self._type == 'dir':
                raise err('standard input/output (-) not allowed as directory path')
            elif self._type == 'symlink':
                raise err('standard input/output (-) not allowed as symlink path')
            elif not self._dash_ok:
                raise err('standard input/output (-) not allowed')
        else:
            e = os.path.exists(string)
            if self._exists==True:
                if not e:
                    raise err("path does not exist: '%s'" % string)

                if self._type is None or self._type == 'any':
                    pass
                elif self._type=='file':
                    if not os.path.isfile(string):
                        raise err("path is not a file: '%s'" % string)
                elif self._type=='symlink':
                    if not os.path.symlink(string):
                        raise err("path is not a symlink: '%s'" % string)
                elif self._type=='dir':
                    if not os.path.isdir(string):
                        raise err("path is not a directory: '%s'" % string)
                elif not self._type(string):
                    raise err("path not valid: '%s'" % string)
            else:
                if self._exists==False and e:
                    raise err("path exists: '%s'" % string)

                p = os.path.dirname(os.path.normpath(string)) or '.'
                if not os.path.isdir(p):
                    raise err("parent path is not a directory: '%s'" % p)
                elif not os.path.exists(p):
                    raise err("parent directory does not exist: '%s'" % p)

        return string

def run(archive, file = None, dst = None, list = "files", pureName = True):
    with uncompress.Archive(archive) as a:
        if file is not None:
            if dst == "-":
                f = io.TextIOWrapper(a.read(file))
                for line in f.readlines():
                    print(line,end="")
            else:
                if dst is None and pureName:
                    dst = a.pure_name(file)
                a.extract(file, dst)

        elif list == "files":
            for name in a.list_files():
                print(name)
        else:
            for name in a.list():
                print(name)

def runUI(*args, **kwargs):
    try:
        run(*args, **kwargs)
    except BrokenPipeError:
        # user doesn't want to read more, we don't care
        return 1

    except uncompress.UnsupportedArchive:
        print("Could not open archive, not an archive or unsupported format.")
        return 1

    return 0

def run_cmd_main():
    p = argparse.ArgumentParser(
        description = """Command line tool for uncompressing an
        archive of compressed files.""")
    p.add_argument("archvie", help="Archive to uncompress.", type=PathType(exists=True, type="any"))
    p.add_argument("file", help="File to extract from archive.", type=str, nargs='?')
    p.add_argument("dst",  help="Destination to extract to. '-' for std out, ommit to extract into same path.", type=str, nargs='?')

    p.add_argument("-e", "--exactName", help="Use exact name for extraction, e.g. foo.txt.gz will be extracted to foo.txt.gz instead of foo.txt.",
    default=False, action="store_true")

    args = p.parse_args()
    return runUI(args.archvie, args.file, args.dst, pureName = not args.exactName)