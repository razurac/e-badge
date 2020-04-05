#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd4in2b
import time
from PIL import Image,ImageDraw,ImageFont,ImageOps
from distutils.util import strtobool
import traceback
import sys
import argparse
import npyscreen

####
#Parser
####

parser = argparse.ArgumentParser(description='Displays pictures on e-Paper')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", help="Input File for monochrome")
group.add_argument("-p", "--prepared", action='store_true', help="Load prepared files")
group.add_argument("--tui", action='store_true', help="Load TUI environment")
parser.add_argument("-fb", "--file_black", help="Load black File")
parser.add_argument("-fr", "--file_red", help="Load black File")
parser.add_argument("-t", "--threshold", required=False, type=int, default=125, help="Sets threshold for conversion")
parser.add_argument("-b", "--bicolor", required=False, action='store_true', help="Enables Bicolor")
parser.add_argument("-to", "--trsh_of", required=False, type=int, default=10, help="Changes threshold offset for bicolor conversion")
parser.add_argument("-i", "--invert", required=False, action='store_true', help="Flips color")
parser.add_argument("-r", "--rotate", required=False, type=int, default=0, help="Rotates picture")
args = vars(parser.parse_args())

if args["prepared"] and (args["file_black"] is None or args["file_black"] is None):
    parser.error("-p requires -fb and -fr")


####
# Basic image functionality
####
# Converter for single images
def convert_image(src_file=args["file"], threshold=args["threshold"], bicolor=args["bicolor"], trsh_of=args["trsh_of"]):
    image_file = Image.open(src_file)
    size = (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT)
    if args["rotate"] != 0:
        image_file = image_file.rotate(args["rotate"])
    image_file = ImageOps.fit(image_file, size, Image.ANTIALIAS, centering=(0.0, 0.5))
    image_file = image_file.convert('L')
    image_b = image_file.point(lambda p: p > threshold and 255)

    if bicolor:
        print("Bicolor is on")
        image_r = image_file.point(lambda p: p > threshold + trsh_of and 255)
        image_r = ImageOps.invert(image_r)
        return image_b, image_r

    return image_b

# Loader for pre converted images
def load_prepared_image(file_b=args["file_black"], file_r=args["file_red"]):
    image_b = Image.open(file_b)
    image_r = Image.open(file_r)
    return image_b, image_r


# Pushes actual image
def push_image(pic, flip=args["invert"]):
    blackimage = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)
    redimage = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)

    if isinstance(pic, tuple):
        blackimage = pic[0]
        redimage = pic[1]
    else:
        blackimage = pic

    if flip:
        blackimage, redimage = redimage, blackimage

    try:
        epd = epd4in2b.EPD()
        epd.init()
        epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))
        epd.sleep()
    except:
        print('traceback.format_exc():\n%s',traceback.format_exc())
        epd = epd4in2b.EPD()
        epd.sleep()
        exit()

#####
# The TUI
#####
def tui():

    class ChooseForm(npyscreen.ActionForm):
        def create(self):
            self.choice = self.add(npyscreen.TitleSelectOne, name='Choose Method', max_height=2, values=['Convert', 'Load'])

        def on_ok(self):
            if 0 in self.choice.value:
                self.parentApp.setNextForm('CONVERT')
            else:
                self.parentApp.setNextForm(None)

        def on_cancel(self):
            self.parentApp.setNextForm(None)

    class ConvertForm(npyscreen.ActionForm):
        def create(self):
            self.file = self.add(npyscreen.TitleFilenameCombo, name='Input File')

        def on_ok(self):
            npyscreen.blank_terminal()
            picture = convert_image(src_file=self.file.value)
            push_image(picture)
            self.parentApp.setNextForm(None)

        def on_cancel(self):
            self.parentApp.setNextForm(None)

    class TUI(npyscreen.NPSAppManaged):
        def onStart(self):
            self.addForm('MAIN', ChooseForm, name='Choice')
            self.addForm('CONVERT', ConvertForm, name='Convert Mode')

    TUI().run()

def main():
    if args["prepared"]:
        picture = load_prepared_image()
        push_image(picture)
        sys.exit()
    elif args["file"]:
        picture = convert_image()
        push_image(picture)
        sys.exit()
    elif args["tui"]:
        print("Loading TUI")
        tui()
        sys.exit()
    else:
        print("You shouldn't be able to get to this error.\n"
              "If you did, then something might be wrong with argument Parsing")
        sys.exit(1)



if __name__ == "__main__":
    main()
