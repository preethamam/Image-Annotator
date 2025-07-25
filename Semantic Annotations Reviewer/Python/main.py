"""
%//%************************************************************************%
%//%*                         ImageLabeler		     				       *%
%//%*           A simple and light weight Python Kivy based software       *%
%//%*           tool to label the multiclass images contained in a         *%
%//%*           folder to respective class folders. This tool is best      *%
%//%*           suited for image labeling/annotation for                   *%
%//%*           classification problem.                                    *%
%//%*                                                                      *%
%//%*           Authors: Preetham Manjunatha, Ph.D.                        *%
%//%*                    Zhiye Lu                     		               *%
%//%*           Github link: https://github.com/preethamam                 *%
%//%*           Submission Date: 01/26/2022                                *%
%//%************************************************************************%
%//%*           Viterbi School of Engineering,                             *%
%//%*           Sonny Astani Dept. of Civil Engineering,                   *%
%//%*           Department of Computer Science                             *%
%//%*           Ming Hsieh Department of Electrical and                    *%
%//%*           Computer Engineering                                       *%
%//%*           University of Southern california,                         *%
%//%*           Los Angeles, California.                                   *%
%//%************************************************************************%

Requirements
---------------------
Tested on Windows 10
Python >= 2.7
Kivy >= 1.0.6
"""

import json
import ntpath
import os
import shutil
from glob import glob
from os.path import basename, dirname, join
from random import randint
from tkinter import Tk, filedialog

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

kivy.require("1.10.1")


# Load configuration from JSON file
# This function will open a file dialog to select the JSON file
# and return the source image folder and key dictionary
# The JSON file should contain the following structure:
# {
#     "sourceImageFolder": "path/to/source/folder",
#     "key_dict": {
#         "key1": "path/to/destination/folder1",
#         "key2": "path/to/destination/folder2",
#         ...
#     }
# }
# Load configuration
def load_config():
    # Create a Tkinter root window but hide it
    root = Tk()
    root.withdraw()
    
    # Set custom icon based on operating system
    try:
        if os.name == 'nt':  # Windows
            icon_path = "app.ico"  # Replace with your Windows icon path
            root.iconbitmap(icon_path)
            root.tk.call('wm', 'iconbitmap', root._w, '-default', icon_path)
        elif sys.platform == 'darwin':  # macOS
            # macOS handles icons differently with tkinter
            # You can set the application icon, but it won't affect individual dialogs
            # in the same way as on Windows
            from PIL import Image, ImageTk
            icon = Image.open("icon.png")  # Use PNG for macOS
            icon_image = ImageTk.PhotoImage(icon)
            root.iconphoto(True, icon_image)
    except Exception as e:
        print(f"Could not set icon: {e}")
    
    # Open file dialog to select the JSON file
    config_path = filedialog.askopenfilename(
        title="Select JSON file",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    
    # If a file was selected
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config["sourceImageFolder"], config["originalImageFolder"], config["key_dict"]
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Please check your JSON file format")
            return "", {}
    else:
        print("No config file selected.")
        return "", {}

# Load paths from config
sourceImageFolder, originalImageFolder, key_dict = load_config()


def reverse():
    pass


def move_to_queue(folder_name):
    pass


def move_file(source_path, target_path):
    print("move: ", source_path, target_path)
    shutil.move(source_path, target_path)


class ImageCell(FloatLayout):
    """A cell containing an image and a label"""
    def __init__(self, **kwargs):
        super(ImageCell, self).__init__(**kwargs)
        
        # Create image widget that fills most of the space
        self.image = Image(
            allow_stretch=True, 
            keep_ratio=True,
            size_hint=(0.85, 0.85),  # Make image 85% of cell size
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Center the image properly
        )
        self.add_widget(self.image)
        
        # Create label at the bottom
        self.label = Label(
            text='',
            size_hint=(1, None),
            height=30,  # Taller label
            pos_hint={'x': 0, 'y': 0},  # Position at bottom
            color=(0, 0, 0, 1),
            bold=True,
            font_size='14sp',
            valign='middle',
            halign='center'
        )
        self.label.bind(size=self.label.setter('text_size'))  # Enable text wrapping
        self.add_widget(self.label)
    
    def set_image(self, source):
        self.image.source = source
    
    def set_label(self, text):
        self.label.text = text


class PicturesFrame(GridLayout):
    imageList = ListProperty()

    def __init__(self, **kwargs):
        super(PicturesFrame, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.spacing = 2
        self.padding = 2
        
        # Create the four cells
        self.annotated_cell = ImageCell()
        self.next_cell = ImageCell()
        self.original_cell = ImageCell()
        self.previous_cell = ImageCell()
        
        # Add cells to grid
        self.add_widget(self.annotated_cell)
        self.add_widget(self.next_cell)
        self.add_widget(self.original_cell)
        self.add_widget(self.previous_cell)
        
        # Set up keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # Initialize
        self.restart()

    def restart(self):
        print("Restarting...")
        self.annotated_cell.set_image("")
        self.annotated_cell.set_label("Annotated image")
        
        self.next_cell.set_image("")
        self.next_cell.set_label("Next image")
        
        self.original_cell.set_image("")
        self.original_cell.set_label("Original image")
        
        self.previous_cell.set_image("")
        self.previous_cell.set_label("Previous image - start")

        self.src = ""
        self.dst = ""
        self.nextNameIter = self.next_image_name_generator()
        
        # Load first two images to populate the display
        try:
            self.display_next_image()
            self.display_next_image()
        except StopIteration:
            print("No images found in source folder")

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Skip if modifier keys are pressed (except num lock which we ignore)
        if modifiers and modifiers != ['numlock']:
            return
        
        # Debug output
        print(f"Key pressed - keycode: {keycode}, text: '{text}', modifiers: {modifiers}")
        
        # keycode[1] is the key name
        key_name = keycode[1]
        
        # For letter keys, use the text parameter if available
        # This ensures it works regardless of Num Lock state
        if text and len(text) == 1:
            # Check if it's a letter we care about
            if text.lower() in key_dict:
                self.key_pressed(text.lower())
                return
        
        # Handle special keys by name
        if key_name == "z":
            self.key_pressed("z")
        elif key_name == "enter":
            self.key_pressed("enter")

    def next_image_name_generator(self):
        for fileName in glob(join(sourceImageFolder, "*")):
            yield ntpath.basename(fileName)

    def source_image_name_to_path(self, image_name, folder_name):
        return join(folder_name, image_name)

    def display_next_image(self, dstFolderName=""):
        try:
            # Move images through the pipeline
            self.previous_cell.set_image(self.annotated_cell.image.source)
            if self.previous_cell.image.source:
                self.previous_cell.set_label(f"Previous - {basename(self.previous_cell.image.source)}")
            else:
                self.previous_cell.set_label("Previous image")
            
            self.annotated_cell.set_image(self.next_cell.image.source)
            if self.annotated_cell.image.source:
                self.annotated_cell.set_label(f"Annotated - {basename(self.annotated_cell.image.source)}")
            else:
                self.annotated_cell.set_label("Annotated image")
            
            # Get next image
            next_image_name = next(self.nextNameIter)
            self.next_cell.set_image(self.source_image_name_to_path(next_image_name, sourceImageFolder))
            self.next_cell.set_label(f"Next - {basename(self.next_cell.image.source)}")
            
            # Update original image
            if basename(self.annotated_cell.image.source):
                original_path = self.source_image_name_to_path(
                    basename(self.annotated_cell.image.source), originalImageFolder
                )
                if os.path.isfile(original_path):
                    self.original_cell.set_image(original_path)
                else:
                    file_name = os.path.splitext(basename(self.annotated_cell.image.source))[0]
                    png_path = self.source_image_name_to_path(
                        file_name + ".png", originalImageFolder
                    )
                    if os.path.isfile(png_path):
                        self.original_cell.set_image(png_path)
                    else:
                        self.original_cell.set_image("")
                
                if self.original_cell.image.source:
                    self.original_cell.set_label(f"Original - {basename(self.annotated_cell.image.source)}")
                else:
                    self.original_cell.set_label("Original image (not found)")

        except StopIteration as e:
            # Handle case when no more images
            if self.next_cell.image.source:
                original_path = self.source_image_name_to_path(
                    basename(self.next_cell.image.source), originalImageFolder
                )
                if os.path.isfile(original_path):
                    self.original_cell.set_image(original_path)
                else:
                    file_name = os.path.splitext(basename(self.next_cell.image.source))[0]
                    png_path = self.source_image_name_to_path(
                        file_name + ".png", originalImageFolder
                    )
                    if os.path.isfile(png_path):
                        self.original_cell.set_image(png_path)
                    else:
                        self.original_cell.set_image("")
                
                if self.original_cell.image.source:
                    self.original_cell.set_label(f"Original - {basename(self.next_cell.image.source)}")
                else:
                    self.original_cell.set_label("Original image (not found)")
            
            print("no more images")

    def key_pressed(self, key):
        print(f"Key pressed: {key}")
        
        if key == "z":
            print("Undo (reverse)")
            if self.dst == "":
                print("Nothing to undo")
                return
            move_file(self.dst, self.src)
            self.restart()

        if key in key_dict:
            if not key_dict[key]:  # Check if destination folder is set
                print(f"No destination folder set for key '{key}'")
                return
                
            src_path = self.annotated_cell.image.source
            print(f"Current annotated image: {src_path}")
            
            if not src_path or not os.path.isfile(src_path):  # Check if there's an image to move
                print("No valid image to move")
                return
                
            dst_path = join(key_dict[key], basename(src_path))
            print(f"Moving from: {src_path}")
            print(f"Moving to: {dst_path}")

            self.src = src_path
            self.dst = dst_path

            # Move the file first, then update display
            move_file(src_path, dst_path)
            self.display_next_image(key_dict[key])

        # Next image
        if key == "enter":
            print("Going to next image.")
            self.display_next_image()


class PicturesApp(App):
    def build(self):
        # Set window size if desired
        Window.size = (1200, 800)  # You can adjust this to your preference
        
        # Set window background color to white
        Window.clearcolor = (1, 1, 1, 1)
        
        frame = PicturesFrame()
        return frame


if __name__ == "__main__":
    PicturesApp().run()