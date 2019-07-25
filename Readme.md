uncompress
===

uncompress is a simple tool that is designed to easily unpack the
content of a single (compressed) file in an (compressed) archive.

Supported archives: zip, tar, tar.gz, tar.bz2, tar.xz

Supported file compression: gz, xz, bz2

For example consider the following archive.

    example.tar
        |- largeFile.txt.gz
        |- someFolder
            |- smallFile.txt

To print the uncompressed content of `largeFile.txt` to std out you
can run

    unarchive example.tar largeFile.txt.gz


Installation
----

To install the tool run

    git clone https://github.com/StephanGocht/uncompress.git
    cd uncompress
    pip3 install .

alternatively you can run the tool without installation using

    git clone https://github.com/StephanGocht/uncompress.git
    cd uncompress
    python3 uncompress


Help
---

Run

    unarchive -h

for more help.

Interface
---

Here is a minimal working example.

```python
    from uncompress import Archive
    import io

    fileName = input()
    with Archive(fileName) as a:
        firstFile = a.list_files[0]
        print(firstFile)

        # obtain binary stream
        f = a.read(firstFile)
        tf = io.TextIOWrapper(f)
        for line in tf.readlines():
            print(line,end="")
```
