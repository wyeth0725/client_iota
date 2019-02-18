# -*- coding: utf-8 -*-

from PIL import Image
import piexif

src = Image.open("./data/lion3.jpg")
zeroth_ifd = {
    piexif.ImageIFD.Artist: "koga",
    piexif.ImageIFD.Software: "iota-pic"
    }
#exif_ifd = {
#    piexif.ExifIFD.DateTimeOriginal: "2099:09:23 10:10:10"
#}
#exif = piexif.dump({"0th": zeroth_ifd, "Exif": exif_ifd})
exif = piexif.dump({"0th": zeroth_ifd})
src.save("test.jpg", exif = exif)
#dec_img = np.asarray(PIL_data)
#cv2.imwrite("{}.jpg".format(tag), dec_img)
