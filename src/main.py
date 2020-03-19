#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd4in2b
import time
from PIL import Image,ImageDraw,ImageFont,ImageOps
from distutils.util import strtobool
import traceback
import sys



def convert_image(src_file, threshold = 125, bicolor = False, trsh_of = 40, flip = False):
    image_file = Image.open(src_file)
    size = (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT)
    image_file = ImageOps.fit(image_file, size, Image.ANTIALIAS, centering=(0.0, 0.5))
    image_file = image_file.convert('L')
    image_b = image_file.point(lambda p: p > threshold and 255)

    if bicolor:
        print("Bicolor is on")
        image_r = image_file.point(lambda p: p > threshold + trsh_of and 255)
        image_r = ImageOps.invert(image_r)
        if flip:
            return image_r, image_b
        return image_b, image_r

    return image_b





def push_image(pic, flip = False):
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


picture = convert_image(sys.argv[1], int(sys.argv[2]), bool(strtobool(sys.argv[3])))

push_image(picture)
