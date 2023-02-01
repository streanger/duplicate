import os
import random
from pathlib import Path
from string import ascii_uppercase


def script_path():
    """set current path, to script path"""
    current_path = str(Path(__file__).parent)
    os.chdir(current_path)
    return current_path
    
    
def write_bin(filename, data):
    """write to binary file"""
    with open(filename, 'wb') as f:
        f.write(data)
    return True
    
    
def generate_data():
    """with random number of fixed size blocks"""
    
    length = random.randrange(1, len(ascii_uppercase))
    block_size = 1024
    data = b''
    for x in range(length):
        char = ascii_uppercase[x]
        subblock = bytes(char, 'utf-8')*block_size
        data += subblock
    return data
    
    
if __name__ == "__main__":
    script_path()
    for x in range(20):
        name = ''.join(random.choices(ascii_uppercase, k=10)) + '.bin'
        data = generate_data()
        write_bin(name, data)
        