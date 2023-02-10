import os
import hashlib
from pathlib import Path
from itertools import groupby
from rich import print

# TODO: look on memory usage, and use gc if needed


def list_directory_files(directory):
    """https://stackoverflow.com/questions/9816816/get-absolute-paths-of-all-files-in-a-directory"""
    for (dirpath, _, filenames) in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))
            
            
def group_pairs_old(pairs):
    """group files by hashes
    pairs = [('hash1', 'file1.txt'), ('hash2', 'file2.txt'), ('hash1', 'file5.txt'), ('hash2', 'file4.txt'), ('hash2', 'file3.txt'), ('hash3', 'file6.txt')]
    """
    matched = [
        (key, [item[1] for item in items])
        for key, items in groupby(sorted(pairs, key=lambda ele: ele[0]), key=lambda ele: ele[0])
    ]
    return matched


def group_files(handles):
    """group files handles by hashes
    handles = [('hash1', 'file1.txt'), ('hash2', 'file2.txt'), ('hash1', 'file5.txt'), ('hash2', 'file4.txt'), ('hash2', 'file3.txt'), ('hash3', 'file6.txt')]
    """
    matched = [
        (key, list(items))
        for key, items in groupby(sorted(handles, key=lambda ele: ele[0]), key=lambda ele: ele[0])
    ]
    return matched
    

def file_md5(filename):
    """calculate file md5 hash"""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_files_handles(directory='.', extensions=('',)):
    """search duplicates (fixed)"""
    # calc hashes and make pairs (hash - filename)
    files_paths = list_directory_files(directory)
    files = []
    for filepath in files_paths:
        try:
            if not Path(filepath).suffix.endswith(extensions):
                continue
            # pair = (file_md5(filepath), filepath)
            file_handle = FileHash(filepath)
            files.append(file_handle)
        except OSError:
            # file not exists
            # think of passing logger here and log info
            pass
    return files


def search(files):
    """files - files handles
    
    DO I NEED RECURSION EVERYWHERE HERE?
    """
    duplicates = []

    # match pairs with hashes
    matched = group_files(files)

    # filter duplicates only
    semi_duplicates = [(key, values) for key, values in matched if len(values) > 1]

    for (key, handles) in semi_duplicates:
        # end of the line
        if handles[0].end:
            return [(key, handles)]

        print(handles)
        input()
        # calc next block
        handles = [handle.next_block() for handle in handles]
        # split items into ended with file read or not
        handles_next = [handle for handle in handles if not handle.end]
        handles_end = [handle for handle in handles if handle.end]
        dupli_next = search(handles_next)
        dupli_end = search(handles_end)
        duplicates.extend(dupli_next)
        duplicates.extend(dupli_end)
    return duplicates
    
    
class FileHash:
    """calculates sha256 hash of next n bytes of data from file"""
    block_size = 1024  # 1kB
    # TODO: use tuple fields instead of dict

    def __init__(self, filename):
        self.filename = filename
        self.file_handle = open(filename, 'rb')
        self.chunks = self.generate_chunks()
        self.digest = hashlib.sha256()
        self.hexdigest = self.digest.hexdigest()
        self.end = False

    def __getitem__(self, item):
        return (self.hexdigest, self.filename)[item]

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
        return self.hexdigest
        
        
if __name__ == "__main__":
    print('search_duplicates module')
    directory = r'directory'
    files = create_files_handles(directory=directory, extensions=('.pdf',))
    out = search(files)
    print(out)
