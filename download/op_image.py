#/usr/bin/env python
# -*- coding: utf-8 -*-

from iota import *
import zlib
import cv2
import numpy as np
import math
import os
from PIL import Image
import piexif

def img_encode(img):
    #png圧縮だとクソ重い
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 5]
    return cv2.imencode(".jpg", cv2.imread(img), encode_param)[1].tostring()

def img_decode(img):
    return cv2.imdecode(np.fromstring(img, dtype = "uint8"), 1)
    #return cv2.imdecode(img, 1)

def enc_image_to_str(img):
    return ",".join(map(lambda x: str(x), [e for inner in img for e in inner]))

def enc_image_from_str(string):
    oned_list = list(map(lambda x: int(x), string.split(",")))
    emp_list = np.empty((0,1), int)
    emp_list = np.array(list(map(lambda x: [x], oned_list[:])))
    return emp_list

def to_tryte_from_picture(args):
    enc_image = img_encode(args.file)
    tryte = TryteString.from_bytes(zlib.compress(enc_image))
    return tryte

def from_tryte_to_picture(tryte, tag, trace_info, count, data_dir):
    try:
        from_trytes = zlib.decompress(TryteString.as_bytes(tryte))
        dec_img = img_decode(from_trytes)
        tag += str(count)
        im_RGB = dec_img[:, :, ::-1].copy()
        PIL_data = Image.fromarray(im_RGB)
        zeroth_ifd = {
            piexif.ImageIFD.Artist: trace_info.replace("\n"," "),
            piexif.ImageIFD.Software: "iota-pic"
            }
        #exif_ifd = {
        #    piexif.ExifIFD.DateTimeOriginal: "2099:09:23 10:10:10"
        #}
        #exif = piexif.dump({"0th": zeroth_ifd, "Exif": exif_ifd})
        exif = piexif.dump({"0th": zeroth_ifd})
        PIL_data.save("{}.jpg".format(data_dir + tag), exif = exif)
        #dec_img = np.asarray(PIL_data)
        #cv2.imwrite("{}.jpg".format(tag), dec_img)
        return True
    except:
        print(tag)
        return False
