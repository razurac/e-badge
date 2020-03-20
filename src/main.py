#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd4in2b
import time
from PIL import Image,ImageDraw,ImageFont,ImageOps
from distutils.util import strtobool
import traceback
import sys
import argparse

parser = argparse.ArgumentParser(description='Displays pictures on e-Paper')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", help="Input File for monochrome")
group.add_argument("-p", "--prepared", action='store_true', help="Load prepared files")
parser.add_argument("-fb", "--file_black", help="Load black File")
parser.add_argument("-fr", "--file_red", help="Load black File")
parser.add_argument("-t", "--threshold", required=False, type=int, default=125, help="Sets threshold for conversion")
parser.add_argument("-b", "--bicolor", required=False, action='store_true', help="Enables Bicolor")
parser.add_argument("-to", "--trsh_of", required=False, type=int, default=10, help="Changes threshold offset for bicolor conversion")
parser.add_argument("-fl", "--flip", required=False, action='store_true', help="Flips color")
args = vars(parser.parse_args())

#if args["prepared"] and (args["file_black"] is None or args["file_black"]):
#    parser.error("-p requires -fb and -fr")



def convert_image(src_file=args["file"], threshold=args["threshold"], bicolor=args["bicolor"], trsh_of=args["trsh_of"]):
    image_file = Image.open(src_file)
    size = (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT)
    image_file = ImageOps.fit(image_file, size, Image.ANTIALIAS, centering=(0.0, 0.5))
    image_file = image_file.convert('L')
    image_b = image_file.point(lambda p: p > threshold and 255)

    if bicolor:
        print("Bicolor is on")
        image_r = image_file.point(lambda p: p > threshold + trsh_of and 255)
        image_r = ImageOps.invert(image_r)
        return image_b, image_r

    return image_b


def load_prepared_image(file_b=args["file_black"], file_r=args["file_red"]):
    image_b = Image.open(file_b)
    image_r = Image.open(file_r)
    return image_b, image_r



def push_image(pic, flip=args["flip"]):
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


def main():
    if args["prepared"]:
        picture = load_prepared_image()
    else:
        picture = convert_image()

    push_image(picture)


if __name__ == "__main__":
    main()
