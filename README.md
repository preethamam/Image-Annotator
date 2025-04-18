# ImageLabeler
A simple and light weight Python Kivy based software tool to label the multiclass images contained in a folder to class folders. This tool is best suited for image labeling/annotation for classification problem.

-----

# Requirements 
Tested on Windows 10 <br>
Python >= 2.7 <br>
Kivy >= 1.0.6

Tested on Ubuntu 16.04 <br>
Python >= 3.9.7 <br>
Kivy >= 2.0.0

Tested on macOS 12.2 <br>
Python >= 3.9.7 <br>
Kivy >= 2.0.0

-----

# Installation procedure

Step 1: Install Python. It is important to have the right version of Python. To check the correct version of Python, we have the command
`python -- version`
It is important to have the right version of python as detailed in the link below:
https://kivy.org/doc/stable/gettingstarted/installation.html#install-pip

Step 2: Install kivy using the pip library. 
Command: `pip install kivy`

Step 3: Execute the main.py file on the corresponding terminal. Ensure that the folder is pointing to the right path in the terminal before execution

-----

# Usage

The purpose of this repository is to use the GUI of pyhton based Kivy to transfer images to a particular folder from an original folder

## Python + Kivy source code
The Folder containing large pool of images is present in the path detailed by main.py file line below: 
`sourceImageFolder = 'foldername'`

Once the original folder has the right path, the next step is to create the folder with the dictionary names shown below.

Class folder names and their respective keyboard shortcuts (change required):
```
key_dict = {
    'w': 'Folder 1',
    'a': 'Folder 2',
    's': 'Folder 3',
    'd': 'Folder 4',
    'f': 'Folder 5',
    'g': 'Folder 6',
    'u': 'Folder 7',
            .
            .
            .
    
    'q': 'Folder n',
    'e': 'Folder n+1',
    'z': 'Folder n+2',
}
```

After the dictionary folders are created, the files will be copied to the destination folder as per the keyboard shortcuts below
Keyboard shortcuts:
`'w', 'a', 's', 'd', 'f', 'g', 'u', 'q', 'e', 'z'`

To `Undo` an action, simply use `Ctrl+Z` and `Redo` by using the keyboard shortcut `Ctrl+Y`.

## Executable
Unzip the `Executable.zip` file. In the Executable folder, find the `config.json` file and change the path of the source image folder in `sourceImageFolder` and `key_dict` keys and folder paths values. After changing the relevant paths and keys, double click the executable `Image Categorize.exe`.

```json
{
    "sourceImageFolder": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\NoCrack",
    "key_dict": {
        "b": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Branched",
        "f": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Few Strands",
        "c": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Nocrack Concrete",
        "p": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Nocrack Pavement",
        "s": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Surface Cracks",
        "q": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\Bad Images"
    }
}
```

----
# Authors
1. Dr. Preetham Manjunatha, Ph.D in Civil Engineering, M.S in Computer Science, M.S in Electrical Engineering and M.S in Civil Engineering, University of Southern California.

2. Zhiye 'Ryan' Lu ([ryanluwork](https://github.com/ryanluwork)), M.S in Computer Science, University of Southern California.
