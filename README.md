# Image annotator and semantic annotations reviewer

## Image categorization/labeler tool
A simple and light weight Python Kivy based software tool to label the multiclass images contained in a folder to class folders. This tool is best suited for image labeling/annotation for classification problem.

![overview](assets/overview.png)


## Semantic annotations reviewer tool
A simple and light weight GUI application to review the semantic segmentation masks or object bounding boxes in comparison to the original image. This is a `2x2` grid layout GUI window which shows the annotated, original, next and previous images in the left top, bottom, right top and bottom grids.

![overview](assets/overview_semantic.png)

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
The Folder containing large pool of images is pointed in the `config.json` file line below: 
`"sourceImageFolder": "H:\\Project MegaCRACK-RoboCRACK\\Real World Data\\USC PhD\\Classification\\Dataset 3 - Cracks-K (644 x 483) (Concrete and pavement)\\NoCrack",`

For semantic image reviewer, change the `config.json` file, especially, `"sourceImageFolder": "C:\\Users\\Preetham\\Downloads\\Anno"`, `"originalImageFolder": "C:\\Users\\Preetham\\Downloads\\Cracks"` lines. Lastly, include valid `"key_dict"` values.
    
Once the original folder has the right path, the next step is to create the folder with the dictionary names (keyboard keys) shown below.

Class folder names and their respective keyboard shortcuts template:
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

Image annotator JSON file change required (config.json):
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

Semantic annotations reviewer JSON file change required (config.json):
```json
{
    "sourceImageFolder": "C:\\Users\\Preetham\\Downloads\\Anno",
    "originalImageFolder": "C:\\Users\\Preetham\\Downloads\\Cracks",
    "key_dict": {
        "a": "C:\\Users\\Preetham\\Downloads\\Good",
        "s": "C:\\Users\\Preetham\\Downloads\\Bad"
    }
}
```

After the dictionary folders are created, the files will be copied to the destination folder as per the keyboard shortcuts below
Keyboard shortcuts:
`'w', 'a', 's', 'd', 'f', 'g', 'u', 'q', 'e', 'z'`

To `Undo` an action, simply use `Ctrl + Z` or `Command ⌘ + Z` and `Redo` by using the keyboard shortcut `Ctrl + Y` or `Command ⌘ + Y`.

## Installer
In the [Installer](<Classification Examples/Installer>) folder, double-click the `Image Annotator.exe` or `Semantic Reviewer.exe` follow the instructions for the installation. After the successful installation, `Image Annotator` or `Semantic Reviewer` Windows application can be started using the Start Menu or Desktop icon. The same [Annotator Installer](<Classification Examples/Installer>) or [Semantic Reviewer Installer](<Semantic Annotations Reviewer/Installer>) folder has a `config.json` JSON file. Before starting the `Image Annotator` Windows application, change the path of the source image folder in `sourceImageFolder`, original images folder in `originalImageFolder`,  `key_dict` keys and folder paths values in the `config.json` JSON file in the respective folder. After changing the relevant paths and keys, double click the `Image Annotator` or `Semantic Reviewer` Windows application icon. This should start the `Image Annotator` or `Semantic Reviewer` app.

Image annotator JSON file change required (config.json):
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

Semantic annotations reviewer JSON file change required (config.json):
```json
{
    "sourceImageFolder": "C:\\Users\\Preetham\\Downloads\\Anno",
    "originalImageFolder": "C:\\Users\\Preetham\\Downloads\\Cracks",
    "key_dict": {
        "a": "C:\\Users\\Preetham\\Downloads\\Good",
        "s": "C:\\Users\\Preetham\\Downloads\\Bad"
    }
}
```

After the dictionary folders are created, the files will be copied to the destination folder as per the keyboard shortcuts below
Keyboard shortcuts:
`'w', 'a', 's', 'd', 'f', 'g', 'u', 'q', 'e', 'z'`

To `Undo` an action, simply use `Ctrl + Z` or `Command ⌘ + Z` and `Redo` by using the keyboard shortcut `Ctrl + Y` or `Command ⌘ + Y`.

----
# Authors
1. Dr. Preetham Manjunatha, Ph.D in Civil Engineering, M.S in Computer Science, M.S in Electrical Engineering and M.S in Civil Engineering, University of Southern California.

2. Zhiye 'Ryan' Lu ([ryanluwork](https://github.com/ryanluwork)), M.S in Computer Science, University of Southern California.
