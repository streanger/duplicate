import os
from pathlib import Path
from search_duplicates import FileHash


def script_path():
    """set current path, to script path"""
    current_path = str(Path(__file__).parent)
    os.chdir(current_path)
    return current_path
    
    
if __name__ == "__main__":
    script_path()
    filename = 'DIDPRWUDWC.bin'
    digest = FileHash(filename)
    for x in range(20):
        status = digest.next_block()
        if not status:
            break
        print(digest)
        