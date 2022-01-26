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
import kivy

from glob import glob
from random import randint
from os.path import join, dirname, basename
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
import ntpath
import shutil
import datetime

kivy.require('1.0.6')


curdir = dirname(__file__)
print (curdir)
sourceImageFolder = 'Working_On'

key_dict = {
    'w': 'Blur',
    'a': 'Thin',
    's': 'Thick',
    'd': 'Branched',
    'f': 'NoCrack',
    'g': 'Alligator',
    'u': 'Unsure',
}



def reverse():
    pass


def move_to_queue(folder_name):
    pass


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
        self.restart()

    def restart(self):
        self.picture_past.source = ''
        self.picture_1.source = ''
        self.picture_2.source = ''

        self.src = ""
        self.dst = ""
        self.nextNameIter = self.next_image_name_generator()
        self.display_next_image()
        self.display_next_image()
        self.pastLabel.text = 'start'

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # do not log command+q
        if modifiers != []:
            return
        if keycode[1] in key_dict or keycode[1] == 'z':
            self.key_pressed(keycode[1])

    def next_image_name_generator(self):
        print("reading: ", join(sourceImageFolder, '*'))
        for fileName in glob(join(sourceImageFolder, '*')):
            # print(fileName)
            yield ntpath.basename(fileName)

    def source_image_name_to_path(self, image_name, folder_name):
        return join(folder_name, image_name)

    default_pic_size = [640,480]
    def display_next_image(self, dstFolderName = ''):
        try:
            print(sourceImageFolder)
            self.picture_past.source = self.picture_1.source
            # self.picture_past.pic.size = [400,300]
            self.picture_past.pic.size = self.default_pic_size
            self.picture_past.center = self.picture_past_center
            self.picture_past.labelText.text = dstFolderName + ' - ' + basename(self.picture_1.source)
            self.picture_past.labelText.top = 390

            self.pastLabel.text = dstFolderName
            # print (self.picture_past.labelText.text)
            self.picture_1.source = self.picture_2.source
            self.picture_1.center = self.picture_1_center
            self.picture_1.labelText.text = basename(self.picture_1.source)
            self.picture_1.pic.size = self.default_pic_size
            self.picture_1.pic.scale = 2
            self.picture_2.source = self.source_image_name_to_path(next(self.nextNameIter), sourceImageFolder)
            self.picture_2.center = self.picture_2_center
            self.picture_2.labelText.text = basename(self.picture_2.source)
            self.picture_2.pic.size = self.default_pic_size
        except StopIteration as e:
            print("no more images")

    def key_pressed(self, key):
        if key[0] == 'z':
            print('reverse')
            if self.dst == '':
                return
            move_file(self.dst, self.src)
            self.restart()
        if key[0] in key_dict:
            src_path = self.picture_1.source
            dst_path = join(key_dict[key[0]], basename(src_path))

            self.src = src_path
            self.dst = dst_path

            self.display_next_image(key_dict[key[0]])
            move_file(src_path, dst_path)



class PicturesApp(App):
    def build(self):
        frame = PicturesFrame()
        return frame


if __name__ == '__main__':
    PicturesApp().run()
