import os
import hashlib
from pathlib import Path
from itertools import groupby


def list_directory_files(directory):
    """https://stackoverflow.com/questions/9816816/get-absolute-paths-of-all-files-in-a-directory"""
    for (dirpath, _, filenames) in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))
            
            
def group_pairs(pairs):
    """group files by hashes
    pairs = [('hash1', 'file1.txt'), ('hash2', 'file2.txt'), ('hash1', 'file5.txt'), ('hash2', 'file4.txt'), ('hash2', 'file3.txt'), ('hash3', 'file6.txt')]
    """
    matched = [(key, [item[1] for item in items]) for key, items in groupby(sorted(pairs, key=lambda ele: ele[0]), key=lambda ele: ele[0])]
    return matched
    
    
def file_md5(filename):
    """calculate file md5 hash"""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
    
def search(directory='.', extensions=('',)):
    """search duplicates (fixed)"""
    # calc hashes and make pairs (hash - filename)
    files = list_directory_files(directory)
    pairs = []
    for filepath in files:
        try:
            if not Path(filepath).suffix.endswith(extensions):
                continue
            pair = (file_md5(filepath), filepath)
            pairs.append(pair)
        except OSError:
            # file not exists
            # think of passing logger here and log info
            pass
            
    # match pairs with hashes
    matched = group_pairs(pairs)
    
    # filter duplicates only
    duplicates = [(key, values) for key, values in matched if len(values) > 1]
    return duplicates
    
    
if __name__ == "__main__":
    print('search_duplicates module')
    