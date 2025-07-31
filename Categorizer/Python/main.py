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
# ── std libs ────────────────────────────────────────────────────────────────
import os, sys, json, ntpath, shutil
from collections import deque
from glob import glob
from os.path import basename, exists, join
from tkinter import Tk, filedialog

# ── 3rd‑party libs ───────────────────────────────────────────────────────────
import re
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ListProperty, StringProperty
from kivy.uix.scatter import Scatter
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

# ─────────────────────────────────────────────────────────────────────────────
# Load configuration (asks user for the JSON file at startup)
# ─────────────────────────────────────────────────────────────────────────────
def load_config():
    root = Tk()
    root.withdraw()

    try:                                                    # set nice icon (optional)
        if os.name == "nt":                                 # Windows
            icon_path = "app.ico"
            root.iconbitmap(icon_path)
            root.tk.call("wm", "iconbitmap", root._w, "-default", icon_path)
        elif sys.platform == "darwin":                      # macOS
            from PIL import Image, ImageTk                  # noqa: import‑only‑when‑needed
            icon = Image.open("icon.png")
            root.iconphoto(True, ImageTk.PhotoImage(icon))
    except Exception as e:
        print(f"[warn] could not set dialog icon: {e}")

    cfg_path = filedialog.askopenfilename(
        title="Select JSON file",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    if not cfg_path:
        print("No config file selected – exiting.")
        sys.exit(1)

    try:
        with open(cfg_path, "r") as fh:
            cfg = json.load(fh)
        return cfg["sourceImageFolder"], cfg["key_dict"]
    except Exception as e:
        print(f"[err] bad config file: {e}")
        sys.exit(1)


# ─── configuration on disk ───────────────────────────────────────────────────
sourceImageFolder, key_dict = load_config()

# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════
def move_file(src, dst):
    """Move with automatic destination‑directory creation."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print("move:", src, "→", dst)
    shutil.move(src, dst)


def normal_key(name: str) -> str:
    """
    Convert keypad digits / Enter to plain equivalents using *symbolic* names
    so ordinary letters never get remapped.
    """
    lname = name.lower()
    # keypad digits come as 'numpad7', 'kp3', …
    if lname.startswith(("numpad", "kp")) and lname[-1].isdigit():
        return lname[-1]
    # translate keypad Enter
    if lname in ("numpadenter", "kpenter"):
        return "enter"
    return lname
        
# ═════════════════════════════════════════════════════════════════════════════
# GUI widgets
# ═════════════════════════════════════════════════════════════════════════════
class Picture(Scatter):
    source = StringProperty(None)  # bound in kv file

    def on_size(self, *_):
        pass  # placeholder kept to preserve original variable name


class PicturesFrame(Widget):
    imageList = ListProperty()  # kept for potential kv binding

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # build sorted image list once
        self.image_list = self._lex_files()

        if not self.image_list:
            print("[err] no images found in sourceImageFolder")
            sys.exit(1)

        # pointers / counters
        self.idx = 0                      # index in image_list
        self.total_images = len(self.image_list)
        self.processed_images = 1         # 1‑based UX counter

        # undo / redo stacks
        self.history = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)

        # thumbnail dimensions
        self.left_image_size = [900, 900]
        self.right_image_size = [350, 350]

        # first draw
        self._update_views()
        self.update_counter_display()    
        
        
    def _lex_files(self):
        """Natural‑sort the files (…1, …2, …10) – case‑insensitive."""
        files = [p for p in glob(join(sourceImageFolder, "*")) if os.path.isfile(p)]

        def natkey(path):
            name = os.path.basename(path)
            # split into digit and non‑digit chunks, turn digits into ints
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

        files.sort(key=natkey)
        return files
        
    # ── pane refresh ────────────────────────────────────────────────────────
    def _src(self, idx: int) -> str:
        return join(sourceImageFolder, self.image_list[idx])

    def _update_views(self):
        """Populate the three panes from self.idx and refresh labels / sizes."""
        cur, nxt, prv = self.idx, self.idx + 1, self.idx - 1

        self.picture_1.source = self._src(cur) if cur < self.total_images else ""
        self.picture_2.source = self._src(nxt) if nxt < self.total_images else ""
        self.picture_past.source = self._src(prv) if prv >= 0 else ""

        # labels
        self.picture_1.labelText.text = "Current image"
        self.picture_2.labelText.text = "Next image"
        self.picture_past.labelText.text = "Previous image"

        # restore sizes and positions
        for pic in (self.picture_1, self.picture_2, self.picture_past):
            self.update_image_size(pic)

    # ── misc GUI helpers ────────────────────────────────────────────────────
    def update_image_size(self, picture_widget):
        if picture_widget == self.picture_1:
            picture_widget.pic.size = self.left_image_size
            picture_widget.center = self.picture_1_center
        elif picture_widget is self.picture_2:
            picture_widget.pic.size = self.right_image_size
            picture_widget.center = self.picture_2_center
        elif picture_widget is self.picture_past:
            picture_widget.pic.size = self.right_image_size
            picture_widget.center = self.picture_past_center

    def update_counter_display(self):
        self.counter_label.text = f"{self.processed_images}/{self.total_images}"

    # ── keyboard plumbing ───────────────────────────────────────────────────
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key_name = normal_key(keycode[1])
        
        # ── ignore lock keys in the modifier list ──────────────────────────────
        lock_keys = {"numlock", "capslock", "scrolllock"}
        effective_mods = [m for m in modifiers if m not in lock_keys]
    
        print(f"Key pressed: {key_name}, modifiers: {modifiers}")

        # undo / redo
        if key_name == "z" and {"ctrl", "meta"} & set(effective_mods):
            self.undo_action(); return True
        if key_name == "y" and {"ctrl", "meta"} & set(effective_mods):
            self.redo_action(); return True

        # ignore other real modifiers (shift, alt, ctrl, meta …)
        if effective_mods:
            return True

        # move labelled
        if key_name in key_dict:
            self.move_and_next(key_name)
            return True
        # skip (Enter)
        if key_name == "enter":
            self.display_next_image()
            return True

        return True  # swallow everything

    # ── core actions ────────────────────────────────────────────────────────
    def move_and_next(self, key_char: str):
        src_path = self.picture_1.source
        if not src_path or not exists(src_path):
            # happens if user keeps pressing after list exhausted
            print("[info] no current image to move")
            return

        dst_path = join(key_dict[key_char], basename(src_path))

        # history
        self.history.append(("move", src_path, dst_path))
        self.redo_stack.clear()

        try:
            move_file(src_path, dst_path)
        except FileNotFoundError:
            print("[warn] file already moved – skipping")
            return

        # advance index
        if self.idx + 1 < self.total_images:
            self.idx += 1
            self.processed_images += 1
            self._update_views()
            self.update_counter_display()
        else:
            # that was the last one → clear panes
            self.picture_past.source = src_path
            self.picture_1.source = ""
            self.picture_2.source = ""
            self.update_image_size(self.picture_1)
            self.update_counter_display()
            print("[info] all images processed")

    def display_next_image(self):
        if self.idx + 1 >= self.total_images:
            print("[info] reached last image – nothing to show")
            return
        self.idx += 1
        self.processed_images += 1
        self._update_views()
        self.update_counter_display()

    def undo_action(self):
        if not self.history:
            print("[info] nothing to undo")
            return

        action = self.history.pop()
        self.redo_stack.append(action)

        if action[0] == "move":
            src_path, dst_path = action[1], action[2]
            try:
                move_file(dst_path, src_path)
            except Exception as e:
                print(f"[err] undo failed: {e}")
                return

            if self.idx > 0:
                self.idx -= 1
                self.processed_images -= 1
            self._update_views()
            self.update_counter_display()

    def redo_action(self):
        if not self.redo_stack:
            print("[info] nothing to redo")
            return

        action = self.redo_stack.pop()
        self.history.append(action)

        if action[0] == "move":
            src_path, dst_path = action[1], action[2]
            try:
                move_file(src_path, dst_path)
            except Exception as e:
                print(f"[err] redo failed: {e}")
                return

            if self.idx + 1 < self.total_images:
                self.idx += 1
                self.processed_images += 1
                self._update_views()
            else:  # ★ we just redid the very last image ★
                self.picture_past.source = src_path   # 5 ➜ Previous pane
                self.picture_1.source = ""            # clear Current
                self.picture_2.source = ""            # clear Next
                self.update_image_size(self.picture_1)

            self.update_counter_display()


# ═════════════════════════════════════════════════════════════════════════════
# Kivy app bootstrap
# ═════════════════════════════════════════════════════════════════════════════
class PicturesApp(App):
    def build(self):
        Window.clearcolor = (0.094, 0.094, 0.094, 1)
        return PicturesFrame()


if __name__ == "__main__":
    PicturesApp().run()