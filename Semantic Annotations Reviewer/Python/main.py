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

ImageLabeler – 2×2 image reviewer / annotator
---------------------------------------------
Kivy‑based tool to shuttle images from a source folder to class folders
with full undo / redo.  Patched July 2025 to:

1. Load files in **lexicographic order**.
2. Rebuild the internal “next” iterator whenever state changes so the
   pipeline is always consistent (fixes the “1→17, undo, 1→17” bug).
3. Use a JSON config file to specify source and destination folders.
4. Use a Tkinter file dialog to select the config file.
5. Use a `key_dict` to map keys to destination folders.

Requirements
---------------------
Tested on Windows 10
Python >= 2.7
Kivy >= 1.0.6
---------------------
"""

import json
import os
import re
import shutil
import sys
from glob import glob
from os.path import basename, dirname, join
from random import randint  # kept for parity; not used here
from tkinter import Tk, filedialog

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

kivy.require("1.10.1")


# ─────────────────────────────── configuration ──────────────────────────────
def load_config():
    """Prompt for a JSON config and return (source, original, key_dict)."""
    root = Tk()
    root.withdraw()

    # Try to set a window icon – best‑effort
    try:
        if os.name == "nt":
            icon_path = "app.ico"
            root.iconbitmap(icon_path)
            root.tk.call("wm", "iconbitmap", root._w, "-default", icon_path)
        elif sys.platform == "darwin":
            from PIL import Image as PILImage
            from PIL import ImageTk

            icon_img = PILImage.open("icon.png")
            root.iconphoto(True, ImageTk.PhotoImage(icon_img))
    except Exception as e:  # noqa: BLE001
        print(f"[warn] Could not set icon: {e}")

    cfg_path = filedialog.askopenfilename(
        title="Select JSON file",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )
    if not cfg_path:
        print("No config file selected – exiting.")
        sys.exit(1)

    try:
        with open(cfg_path, "r", encoding="utf‑8") as fh:
            cfg = json.load(fh)
        return cfg["sourceImageFolder"], cfg["originalImageFolder"], cfg["key_dict"]
    except Exception as e:  # noqa: BLE001
        print(f"[err] Failed to load config: {e}")
        sys.exit(1)


sourceImageFolder, originalImageFolder, key_dict = load_config()

# ─────────────────────────────── helpers ─────────────────────────────────────
def move_file(src: str, dst: str):
    """Move `src` to `dst`, creating parent dirs if needed."""
    print("move:", src, "→", dst)
    os.makedirs(dirname(dst), exist_ok=True)
    shutil.move(src, dst)


# ─────────────────────────────── UI widgets ──────────────────────────────────
class ImageCell(FloatLayout):
    """One quadrant: image + lower caption + (opt.) counter label."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # main image
        self.image = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.85, 0.85),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.image.color = (0.961, 0.961, 0.961, 1)
        self.add_widget(self.image)

        # caption
        self.label = Label(
            text="",
            size_hint=(1, None),
            height=30,
            pos_hint={"x": 0, "y": 0},
            color=(0, 0, 0, 1),
            bold=True,
            font_size="14sp",
            valign="middle",
            halign="center",
        )
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

        # counter (only used for bottom‑left)
        self.counter_label = Label(
            text="",
            size_hint=(None, None),
            size=(60, 30),
            pos_hint={"x": 0, "y": 0},
            color=(0, 0, 0, 1),
            bold=True,
            font_size="12sp",
        )
        self.add_widget(self.counter_label)

    # Convenience setters
    def set_image(self, src: str):
        self.image.source = src

    def set_label(self, txt: str):
        self.label.text = txt


# ─────────────────────────────── main frame ─────────────────────────────────
class PicturesFrame(GridLayout):
    """2×2 grid handling all keyboard logic."""

    imageList = ListProperty()  # kept for compatibility

    # --------------- iterator helpers ----------------------------------
    def _lex_files(self):
        """Natural‑sort the files (…1, …2, …10) – case‑insensitive."""
        files = [p for p in glob(join(sourceImageFolder, "*")) if os.path.isfile(p)]

        def natkey(path):
            name = os.path.basename(path)
            # split into digit and non‑digit chunks, turn digits into ints
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

        files.sort(key=natkey)
        return files

    def _build_iter_after(self, basename_or_none):
        """
        Rebuild the iterator `self.nextNameIter` so that it yields filenames
        **after** `basename_or_none` in lexicographic order.
        """
        files = self._lex_files()

        basenames = [os.path.basename(f) for f in files]
        if basename_or_none in basenames:
            start_idx = basenames.index(basename_or_none) + 1
        else:
            start_idx = 0

        self.nextNameIter = iter(basenames[start_idx:])
        self._basenames_lex = basenames

    def _sync_original(self):
        """Refresh the Original cell so it mirrors the Annotated one."""
        src = self.annotated_cell.image.source
        if not src:
            self.original_cell.set_image("")
            self.original_cell.set_label("Original image")
            return

        bn = basename(src)
        candidate = self.source_image_name_to_path(bn, originalImageFolder)
        if not os.path.isfile(candidate):
            png = self.source_image_name_to_path(os.path.splitext(bn)[0] + ".png",
                                                originalImageFolder)
            candidate = png if os.path.isfile(png) else ""

        self.original_cell.set_image(candidate)
        if candidate:
            self.original_cell.set_label(f"Original - {bn}")
        else:
            self.original_cell.set_label("Original image (not found)")
            
    # --------------------------------------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.spacing = 2
        self.padding = 2

        # four quadrants
        self.annotated_cell = ImageCell()
        self.next_cell = ImageCell()
        self.original_cell = ImageCell()
        self.previous_cell = ImageCell()

        for cell in (
            self.annotated_cell,
            self.next_cell,
            self.original_cell,
            self.previous_cell,
        ):
            self.add_widget(cell)

        # Total images
        self.total_images_fixed = len(self._lex_files())
        
        # keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # history: (src, dst, index_before_move, prev_img, annotated_img, next_img)
        self.history = []
        self.history_index = -1

        # initialise
        self.restart()

    # --------------------- lifecycle helpers ---------------------------
    def restart(self, restore_index=None):
        """Reset the UI, optionally restoring to a specific counter value."""
        print("Restarting…")
        for cell, cap in [
            (self.annotated_cell, "Annotated image"),
            (self.next_cell, "Next image"),
            (self.original_cell, "Original image"),
            (self.previous_cell, "Previous image - start"),
        ]:
            cell.set_image("")
            cell.set_label(cap)

        self.src = self.dst = ""
        self.current_index = 1 if restore_index is None else restore_index

        # fresh iterator
        self._build_iter_after(None)

        # prime first two tiles
        try:
            self.display_next_image(skip_increment=True)
            self.display_next_image(skip_increment=True)
        except StopIteration:
            print("[info] No images found in source folder.")

    # --------------------- keyboard handling ---------------------------
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # ctrl/cmd + Z / Y
        if ("ctrl" in modifiers or "cmd" in modifiers) and keycode[1] == "z":
            self.undo()
            return
        if ("ctrl" in modifiers or "cmd" in modifiers) and keycode[1] == "y":
            self.redo()
            return

        if modifiers and modifiers != ["numlock"]:
            return  # ignore with other modifiers

        key_name = keycode[1]
        if text and len(text) == 1 and text.lower() in key_dict:
            self.key_pressed(text.lower())
        elif key_name == "z":
            self.key_pressed("z")
        elif key_name == "enter":
            self.key_pressed("enter")

    # -------------------- display pipeline -----------------------------
    def source_image_name_to_path(self, image_name, folder_name):
        return join(folder_name, image_name)

    def display_next_image(
        self,
        dstFolderName: str = "",
        skip_increment: bool = False,
        skip_previous_update: bool = False,
    ):
        """
        Shift the 2×2 pipeline forward by one image.

        skip_increment          – don’t bump the counter (used at startup)
        skip_previous_update    – don’t copy Annotated→Previous (used after move)
        """
        try:
            # advance the counter (but never beyond the fixed total)
            if (
                not skip_increment
                and self.annotated_cell.image.source
                and self.current_index < self.total_images_fixed
            ):
                self.current_index += 1

            # move pipeline: Previous ← Annotated
            if not skip_previous_update:
                self.previous_cell.set_image(self.annotated_cell.image.source)
                self.previous_cell.set_label(
                    f"Previous - {basename(self.previous_cell.image.source)}"
                    if self.previous_cell.image.source
                    else "Previous image"
                )

            # Annotated ← Next
            self.annotated_cell.set_image(self.next_cell.image.source)
            self.annotated_cell.set_label(
                f"Annotated - {basename(self.annotated_cell.image.source)}"
                if self.annotated_cell.image.source
                else "Annotated image"
            )

            # rebuild iterator starting *after* the new Annotated image
            annot_bn = (
                basename(self.annotated_cell.image.source)
                if self.annotated_cell.image.source
                else None
            )
            self._build_iter_after(annot_bn)

            # pull the new Next image
            next_image_name = next(self.nextNameIter)
            self.next_cell.set_image(
                self.source_image_name_to_path(next_image_name, sourceImageFolder)
            )
            self.next_cell.set_label(f"Next - {next_image_name}")

            # keep Original tile in sync
            self._sync_original()

            # update counter display
            self.original_cell.counter_label.text = (
                f"{self.current_index}/{self.total_images_fixed}"
            )

        except StopIteration:
            # no more images: tidy up the view
            if not skip_previous_update:
                self.previous_cell.set_image(self.annotated_cell.image.source)
                self.previous_cell.set_label(
                    f"Previous - {basename(self.previous_cell.image.source)}"
                    if self.previous_cell.image.source
                    else "Previous image"
                )

            self.annotated_cell.set_image(self.next_cell.image.source)
            self.annotated_cell.set_label(
                f"Annotated - {basename(self.annotated_cell.image.source)}"
                if self.annotated_cell.image.source
                else "Annotated image - end"
            )

            self.next_cell.set_image("")
            self.next_cell.set_label("Next image - end")

            # sync Original tile at end
            self._sync_original()

            # counter stays at the last value reached
            self.original_cell.counter_label.text = (
                f"{self.current_index}/{self.total_images_fixed}"
            )

            print("[info] No more images.")
            
    # ------------------------ main command handler ---------------------
    def key_pressed(self, key):
        if key == "z":  # undo shortcut alias
            self.undo()
            return
        if key == "enter":
            self.display_next_image()
            return
        if key not in key_dict:
            return

        dst_dir = key_dict[key]
        if not dst_dir:
            print(f"[warn] No destination folder mapped to key '{key}'.")
            return

        src_path = self.annotated_cell.image.source
        if not src_path or not os.path.isfile(src_path):
            print("[warn] No valid annotated image to move.")
            return

        dst_path = join(dst_dir, basename(src_path))

        # push current state into history BEFORE the move
        self.history = self.history[: self.history_index + 1]
        self.history.append(
            (
                src_path,
                dst_path,
                self.current_index,
                self.previous_cell.image.source,
                self.annotated_cell.image.source,
                self.next_cell.image.source,
            )
        )
        self.history_index += 1

        move_file(src_path, dst_path)

        # previous quadrant shows moved file
        self.previous_cell.set_image(dst_path)
        self.previous_cell.set_label(f"Previous - {basename(dst_path)} (moved)")

        # ── REBUILD iterator because source folder content changed ──
        annot_bn = (
            basename(self.annotated_cell.image.source)
            if self.annotated_cell.image.source
            else None
        )
        self._build_iter_after(annot_bn)

        # advance
        self.display_next_image(skip_previous_update=True)

    # --------------------- undo / redo ---------------------------------
    def undo(self):
        """Undo the last move, restoring quadrants and iterator."""
        if self.history_index < 0:
            print("[info] Nothing to undo.")
            return

        (
            src,
            dst,
            idx_before,
            prev_img,
            annot_img,
            next_img,
        ) = self.history[self.history_index]
        print(f"Undo: moving {basename(dst)} → {dirname(src)}")
        move_file(dst, src)

        # restore quadrant images exactly as they were
        self.previous_cell.set_image(prev_img or "")
        self.previous_cell.set_label(
            f"Previous - {basename(prev_img)}"
            if prev_img
            else "Previous image - start"
        )

        self.annotated_cell.set_image(annot_img)
        self.annotated_cell.set_label(f"Annotated - {basename(annot_img)}")

        self.next_cell.set_image(next_img or "")
        self.next_cell.set_label(
            f"Next - {basename(next_img)}" if next_img else "Next image"
        )

        # restore counter and history pointer
        self.current_index = idx_before
        self.history_index -= 1

        # rebuild iterator so Next resumes correctly
        annot_bn = basename(annot_img) if annot_img else None
        self._build_iter_after(annot_bn)

        # sync Original tile with the restored Annotated image
        self._sync_original()

        # refresh counter display
        self.original_cell.counter_label.text = (
            f"{self.current_index}/{self.total_images_fixed}"
        )
        
    def redo(self):
        if self.history_index >= len(self.history) - 1:
            print("[info] Nothing to redo.")
            return

        self.history_index += 1
        src, dst, idx_at_move, prev_img, annot_img, next_img = self.history[
            self.history_index
        ]
        print(f"Redo: moving {basename(src)} → {dirname(dst)}")
        move_file(src, dst)

        # show moved file in previous
        self.previous_cell.set_image(dst)
        self.previous_cell.set_label(f"Previous - {basename(dst)} (moved)")

        # iterator must skip over everything up to the new annotated
        annot_bn = basename(annot_img) if annot_img else None
        self._build_iter_after(annot_bn)

        self.current_index = (idx_at_move + 1 if idx_at_move < self.total_images_fixed else idx_at_move)
        try:
            self.display_next_image(skip_increment=True, skip_previous_update=True)
        except StopIteration:
            self.annotated_cell.set_image("")
            self.annotated_cell.set_label("Annotated image - end")
            self.next_cell.set_image("")
            self.next_cell.set_label("Next image - end")
            self.original_cell.set_image("")
            self.original_cell.set_label("Original image")

        self.original_cell.counter_label.text = f"{self.current_index}/{self.total_images_fixed}"


# ─────────────────────────────── Kivy app ───────────────────────────────────
class PicturesApp(App):
    def build(self):
        Window.size = (1200, 800)
        Window.clearcolor = (0.961, 0.961, 0.961, 1)
        return PicturesFrame()


if __name__ == "__main__":
    PicturesApp().run()
