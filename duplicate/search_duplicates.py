import os
import gc
import re
import hashlib
from pathlib import Path
from itertools import groupby, filterfalse


def list_directory_files(directory):
    """https://stackoverflow.com/questions/9816816/get-absolute-paths-of-all-files-in-a-directory"""
    for (dirpath, _, filenames) in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def split_extensions(text):
    """split text to files extensions"""
    extensions = [
        item.strip(" .") for item in re.split(",|;| ", text) if item.strip()
    ]
    extensions = tuple(sorted(set(extensions)))
    return extensions


def group_by_hash(handles):
    """group files handles by hashes"""
    matched = [
        (key, list(items))
        for key, items in groupby(sorted(handles, key=lambda ele: ele.hexdigest), key=lambda ele: ele.hexdigest)
    ]
    return matched


def group_by_size(handles):
    """group files handles by size"""
    matched = [
        list(items)
        for key, items in groupby(sorted(handles, key=lambda ele: ele.size), key=lambda ele: ele.size)
    ]
    return matched


def create_files_handles(directory='.', extensions=None):
    """create file handlers for hash calc"""
    if extensions is None or extensions == ():
        extensions = ('',)
    files_paths = list_directory_files(directory)
    files = []
    for filepath in files_paths:
        try:
            if not Path(filepath).suffix.endswith(extensions):
                continue
            file_handle = FileHash(filepath)
            files.append(file_handle)
        except OSError:
            pass
            # file not exists
            # think of passing logger here and log info
            # when we rapidly use search, this error will occur
            # it may be cause of keeping previous handle to file
            # use of gc.collect() at the end of search() fix that
    return files


def objects_dupli(files):
    """find duplicates in list of files handles
    
    it works recursively
    """
    duplicates = []

    # match pairs with hashes
    matched = group_by_hash(files)

    # filter duplicates only
    semi_duplicates = [(key, values) for key, values in matched if len(values) > 1]

    for (key, handles) in semi_duplicates:
        # end of the line
        if handles[0].end:
            return [(key, handles)]

        # calc next block & split files depend on end of file status
        handles = [handle.next_block() for handle in handles]
        handles_next = filterfalse(lambda handle: not handle.end, handles)
        handles_end = filterfalse(lambda handle: handle.end, handles)
        dupli_next = objects_dupli(handles_next)
        dupli_end = objects_dupli(handles_end)
        duplicates.extend(dupli_next)
        duplicates.extend(dupli_end)
    return duplicates


def search(directory, extensions=None):
    """search for duplicate files
    
    params:
        directory - directory to search in
        extensions - files extensions to search through
    """
    files = create_files_handles(directory=directory, extensions=extensions)
    grouped = group_by_size(files)
    total = []
    for group in grouped:
        if len(group) == 1:
            continue
        block_size = max(1024, group[0].size//100)
        [handle.set_block_size(block_size) for handle in group]
        part = objects_dupli(group)
        total.extend(part)
    gc.collect()
    return total


class FileHash:
    """calculates sha256 hash of next n bytes of data from file"""
    __slots__ = ('block_size', 'filename', 'size', 'file_handle', 'chunks', 'digest', 'hexdigest', 'end')

    def __init__(self, filename):
        self.block_size = 1024  # 1kB
        self.filename = filename
        self.size = os.stat(filename).st_size
        self.file_handle = open(filename, 'rb')
        self.chunks = self.generate_chunks()
        self.digest = hashlib.sha256()
        self.hexdigest = self.digest.hexdigest()
        self.end = False

    def __getitem__(self, item):
        return (self.hexdigest, self.filename)[item]

    def set_block_size(self, size):
        """set block size"""
        self.block_size = size

    def generate_chunks(self):
        """generate file data chunks for further processing"""
        while True:
            data = self.file_handle.read(self.block_size)
            if not data:
                break
            yield data
            
    def next_block(self):
        """update digest with next block"""
        try:
            next_bytes = next(self.chunks)
        except StopIteration:
            self.end = True
            return self
        self.digest.update(next_bytes)
        self.hexdigest = self.digest.hexdigest()
        return self

    def __repr__(self):
        return '<{}>:<{}>'.format(Path(self.filename).name, self.hexdigest)

    def __str__(self):
        return '<{}>:<{}>'.format(Path(self.filename).name, self.hexdigest)

    # TODO: do we need that?
    # def __delete__(self):
    #     self.file_handle.close()


if __name__ == "__main__":
    os.chdir(str(Path(__file__).parent))
    directory = r'..\example_files_tree\random_blocks'
    duplicates = search(directory)
    print(duplicates)
