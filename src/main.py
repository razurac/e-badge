#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd4in2b
from PIL import Image, ImageDraw, ImageFont, ImageOps
import traceback
import sys
import argparse
import npyscreen

####
# Parser
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
parser.add_argument("-s", "--swap", required=False, action='store_true', help="Swaps Black and red")
parser.add_argument("-i", "--invert", required=False, action='store_true', help="Inverts color")
parser.add_argument("-r", "--rotate", required=False, type=int, default=0, help="Rotates picture")
args = vars(parser.parse_args())

if args["prepared"] and (args["file_black"] is None or args["file_black"] is None):
    parser.error("-p requires -fb and -fr")


####
# Basic image functionality
####
# Converter for single images
def convert_image(src_file=args["file"], threshold=args["threshold"], bicolor=args["bicolor"], trsh_of=args["trsh_of"], rotation=args["rotate"], invert=args["invert"]):
    image_file = Image.open(src_file)
    size = (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT)
    if rotation != 0:
        image_file = image_file.rotate(rotation)
    image_file = ImageOps.fit(image_file, size, Image.HAMMING, centering=(0.0, 0.5))
    image_file = image_file.convert('L')
    image_b = image_file.point(lambda p: p > threshold and 255)
    if invert and not bicolor:
        image_b = ImageOps.invert(image_b)

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
def push_image(pic, swap=args["swap"]):
    # blackimage = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)  # Might be obsolete
    redimage = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)

    if isinstance(pic, tuple):
        blackimage = pic[0]
        redimage = pic[1]
    else:
        blackimage = pic

    blackimage = blackimage.convert('L')
    redimage = redimage.convert('L')

    if swap:
        blackimage, redimage = redimage, blackimage

    try:
        epd = epd4in2b.EPD()
        epd.init()
        epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))
        epd.sleep()
    except:
        print('traceback.format_exc():\n%s', traceback.format_exc())
        epd = epd4in2b.EPD()
        epd.sleep()
        exit()


#####
# The TUI
#####
def tui():

    class ChooseForm(npyscreen.ActionForm):
        def create(self):
            self.choice = self.add(npyscreen.TitleSelectOne,
                                   name='Choose Method',
                                   values=['Convert', 'Load', 'Clear'])

        def on_ok(self):
            if 0 in self.choice.value:
                self.parentApp.setNextForm('CONVERT')
            elif 1 in self.choice.value:
                self.parentApp.setNextForm('LOAD')
            elif 2 in self.choice.value:
                npyscreen.blank_terminal()
                epd = epd4in2b.EPD()
                epd.init()
                epd.Clear(0xFF)
                epd.sleep()
                self.parentApp.setNextForm('MAIN')

        def on_cancel(self):
            notify_result = npyscreen.notify_ok_cancel('Are you sure you want to exit?', title='Exit')
            if notify_result:
                self.parentApp.setNextForm(None)

    class ConvertForm(npyscreen.ActionForm):
        def create(self):
            self.file = self.add(npyscreen.TitleFilenameCombo, name='Input File')
            self.threshold = self.add(npyscreen.TitleSlider,
                                      out_of=256,
                                      step=1,
                                      label=True,
                                      value=args["threshold"],
                                      name='Threshold')
            self.threshold_of = self.add(npyscreen.TitleSlider,
                                         out_of=256,
                                         step=1,
                                         label=True,
                                         value=args["trsh_of"],
                                         name='Threshold Offset')
            self.rotation = self.add(npyscreen.TitleSlider,
                                     out_of=270,
                                     step=90,
                                     label=True,
                                     value=args["rotate"],
                                     name='Rotation')
            self.bicolor = self.add(npyscreen.CheckBox, name='Bicolor')
            self.swap = self.add(npyscreen.CheckBox, name='Swap B/R')
            self.invert = self.add(npyscreen.CheckBox, name="Invert color")


        def on_ok(self):
            npyscreen.blank_terminal()
            picture = convert_image(src_file=self.file.value,
                                    threshold=int(self.threshold.value),
                                    bicolor=self.bicolor.value,
                                    trsh_of=int(self.threshold_of.value),
                                    rotation=int(self.rotation.value),
                                    invert=self.invert.value)
            push_image(picture, swap=self.swap.value)
            self.parentApp.setNextForm('MAIN')

        def on_cancel(self):
            self.parentApp.setNextForm('MAIN')

    class LoadForm(npyscreen.ActionForm):
        def create(self):
            self.fileb = self.add(npyscreen.TitleFilenameCombo, name='Input Black File')
            self.filer = self.add(npyscreen.TitleFilenameCombo, name='Input Red File')
            self.swap = self.add(npyscreen.CheckBox, name='Swap B/R')

        def on_ok(self):
            npyscreen.blank_terminal()
            picture = load_prepared_image(file_b=self.fileb.value, file_r=self.filer.value)
            push_image(picture, swap=self.swap.value)
            self.parentApp.setNextForm('MAIN')

        def on_cancel(self):
            self.parentApp.setNextForm('MAIN')

    class TUI(npyscreen.NPSAppManaged):
        def onStart(self):
            self.addForm('MAIN', ChooseForm, name='Choice')
            self.addForm('CONVERT', ConvertForm, name='Convert Mode')
            self.addForm('LOAD', LoadForm, name='Load Mode')

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
