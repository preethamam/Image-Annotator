'''
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
'''

import datetime
import ntpath
import shutil
from collections import deque
from glob import glob
from os.path import basename, dirname, join
from random import randint

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget

kivy.require('1.10.1')


curdir = dirname(__file__)
print (curdir)
sourceImageFolder = r'C:\Users\Preetham\Downloads\Dummy\Clean me'

key_dict = {    
    'b': r'C:\Users\Preetham\Downloads\Dummy\Branched',
    'f': r'C:\Users\Preetham\Downloads\Dummy\Few Strands',
    'n': r'C:\Users\Preetham\Downloads\Dummy\No Crack',
    's': r'C:\Users\Preetham\Downloads\Dummy\Surface Cracks',
    'q': r'C:\Users\Preetham\Downloads\Dummy\Bad Images'
}


def move_file(source_path, target_path):
    print("move: ", source_path, target_path)
    shutil.move(source_path, target_path)

class Picture(Scatter):
    source = StringProperty(None)

    def on_size(self, instance, value):
        print("size changed", self.pos, self.center, self.size, instance, value)
        # self.center = self.center_hint
        pass

class PicturesFrame(Widget):
    imageList = ListProperty()

    def __init__(self, **kwargs):
        super(PicturesFrame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # Initialize counters for total and processed images
        self.total_images = len(glob(join(sourceImageFolder, '*')))
        self.processed_images = 1  # Start from 1
        
        # For undo/redo functionality
        self.history = deque(maxlen=50)  # Store last 50 actions
        self.redo_stack = deque(maxlen=50)  # Store redo actions
        
        # Set initial image sizes
        self.left_image_size = [900, 900]
        self.right_image_size = [350, 350]
        
        self.restart()

    def restart(self):
        # Reset image sources
        self.picture_past.source = ''
        self.picture_1.source = ''
        self.picture_2.source = ''

        self.src = ""
        self.dst = ""
        
        # Reset image positions and sizes
        self.picture_1.center = self.picture_1_center
        self.picture_2.center = self.picture_2_center
        self.picture_past.center = self.picture_past_center
        
        self.picture_1.pic.size = self.left_image_size
        self.picture_2.pic.size = self.right_image_size
        self.picture_past.pic.size = self.right_image_size
        
        # Setup image iterator and display first images
        self.nextNameIter = self.next_image_name_generator()
        
        try:
            # Initialize with first image in main view
            self.picture_1.source = self.source_image_name_to_path(next(self.nextNameIter), sourceImageFolder)
            # Initialize with second image in next preview
            self.picture_2.source = self.source_image_name_to_path(next(self.nextNameIter), sourceImageFolder)
        except StopIteration:
            print("Not enough images")
        
        # Update counter display
        self.update_counter_display()

    def display_next_image(self, dstFolderName=''):
        try:
            # Move current main image to past position
            self.picture_past.source = self.picture_1.source
            
            # Move next preview image to main position
            self.picture_1.source = self.picture_2.source
            
            # Load new image into next preview
            next_image = next(self.nextNameIter)
            self.picture_2.source = self.source_image_name_to_path(next_image, sourceImageFolder)
            
            # Make sure sizes are correct (to fix the initial issue)
            self.picture_1.pic.size = self.left_image_size
            self.picture_2.pic.size = self.right_image_size
            self.picture_past.pic.size = self.right_image_size
            
            # Make sure positions are correct
            self.picture_1.center = self.picture_1_center
            self.picture_2.center = self.picture_2_center
            self.picture_past.center = self.picture_past_center
            
        except StopIteration as e:
            print("no more images")

    def update_image_size(self, picture_widget):
        """Update image size based on which picture widget it is"""
        if picture_widget == self.picture_1:
            picture_widget.pic.size = self.left_image_size
        elif picture_widget in (self.picture_2, self.picture_past):
            picture_widget.pic.size = self.right_image_size
        
        # Ensure it's properly centered
        if picture_widget == self.picture_1:
            picture_widget.center = self.picture_1_center
        elif picture_widget == self.picture_2:
            picture_widget.center = self.picture_2_center
        elif picture_widget == self.picture_past:
            picture_widget.center = self.picture_past_center
                            
    def update_counter_display(self):
        # Update the counter text
        self.counter_label.text = f"{self.processed_images}/{self.total_images}"

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(f"Key pressed: {keycode[1]}, modifiers: {modifiers}")
        
        # Handle undo (Ctrl+Z or Command+Z)
        if keycode[1] == 'z' and ('ctrl' in modifiers or 'meta' in modifiers):
            self.undo_action()
            return True
            
        # Handle redo (Ctrl+Y or Command+Y)
        if keycode[1] == 'y' and ('ctrl' in modifiers or 'meta' in modifiers):
            self.redo_action()
            return True
            
        # Original key handling (if no modifiers)
        if not modifiers:  # Changed from modifiers == []
            if keycode[1] in key_dict:
                self.key_pressed(keycode[1])
            if keycode[1] == 'enter':            
                self.key_pressed(keycode[1])
                
        return True

    def next_image_name_generator(self):
        print("reading: ", join(sourceImageFolder, '*'))
        for fileName in glob(join(sourceImageFolder, '*')):
            yield ntpath.basename(fileName)

    def source_image_name_to_path(self, image_name, folder_name):
        return join(folder_name, image_name)

    def key_pressed(self, key):            
        if key[0] in key_dict:
            src_path = self.picture_1.source
            dst_path = join(key_dict[key[0]], basename(src_path))

            self.src = src_path
            self.dst = dst_path
            
            # Add to history for undo
            self.history.append(('move', src_path, dst_path))
            # Clear redo stack when a new action is performed
            self.redo_stack.clear()
            
            # Move the file
            move_file(src_path, dst_path)
            
            # Display next image
            self.display_next_image(key_dict[key[0]])
            
            # Increment processed counter and update display
            self.processed_images += 1
            self.update_counter_display()

        # Next image without classification
        if key == 'enter':
            print('Going to next image.')
            self.display_next_image()
    
    def undo_action(self):
        if not self.history:
            print("Nothing to undo")
            return
            
        action = self.history.pop()
        self.redo_stack.append(action)
        
        if action[0] == 'move':
            src_path, dst_path = action[1], action[2]
            # The src and dst are reversed for undo
            print(f"Undoing: moving {dst_path} back to {src_path}")
            try:
                move_file(dst_path, src_path)
                self.processed_images -= 1
                self.update_counter_display()
                # Reset the view to show the correct images
                self.restart()
            except Exception as e:
                print(f"Error during undo: {e}")
    
    def redo_action(self):
        if not self.redo_stack:
            print("Nothing to redo")
            return
            
        action = self.redo_stack.pop()
        self.history.append(action)
        
        if action[0] == 'move':
            src_path, dst_path = action[1], action[2]
            print(f"Redoing: moving {src_path} to {dst_path}")
            try:
                move_file(src_path, dst_path)
                self.processed_images += 1
                self.update_counter_display()
                # Reset the view to show the correct images
                self.restart()
            except Exception as e:
                print(f"Error during redo: {e}")
                
class PicturesApp(App):
    def build(self):
        frame = PicturesFrame()
        return frame


if __name__ == '__main__':
    PicturesApp().run()