import argparse
import uncompress
import io

def run(archive, file = None, list = "files"):
    with uncompress.ArchiveOfCompressedFiles(archive) as a:
        if file is not None:
            f = io.TextIOWrapper(a.read(file))
            for line in f.readlines():
                print(line,end="")
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
    p.add_argument("archvie", help="Archive to uncompress.", type=argparse.FileType('rb'))
    p.add_argument("file", help="File to extract from archive.", type=str, nargs='?')

    args = p.parse_args()
    return runUI(args.archvie, args.file)