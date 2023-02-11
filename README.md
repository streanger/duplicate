# duplicate

files duplicate viewer

## install

```
pip install git+https://github.com/streanger/duplicate.git
```

## usage

```bash
# from cli
duplicate  # with no args will run gui
duplicate <directory>  # will run cli search
duplicate . ".jpg, .png"  # search in current directory, filter by .jpg, .png

# as module
python -m duplicate
```

```python
# gui
import duplicate
duplicate.gui()

# console search
from rich import print
from duplicate import search
directory = 'path/to/directory/with/duplicates
results = search(directory)
print(results)
```

## screenshots

![image](screenshots/duplicate01.png)

## changelog
- v. 0.1.2
    - fix for `OSError` using `gc.collect()` due to locked file handles after many search
    - __slots__ in `FileHash` class
    - version info in gui and cli

- v. 0.1.1
    - initial filter and matching by files size
    - files handle, which allows for reading files in chunks, what improves speed a lot
    - entrypoint cli and gui support
    
- v. 0.1.0
    - gui
    - matching hashes of full file content

## ideas

- faster search (+)

- faster window moving while many rows exists

- green progressbar for search

- sync between search and gui

- resizable filedialog (if possible)

- after method in tkinter if needed

- reset scrollbar for maximized windows should be fixed

- more information on the bottom info label

- better threads handling; maybe use of queue

- utils module for class staticmethods

- pylint & black todo

- screenshot(s) to upload (+)
