#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import cv2
import math
import sys
from iota import *
import urllib
import json
import zlib
import numpy as np
import os

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

def from_tryte_to_picture(tryte):
    try:
        from_trytes = zlib.decompress(TryteString.as_bytes(tryte))
        dec_img = img_decode(from_trytes)
        return dec_img
    except:
        return False

class getTransaction:
    def __init__(self, ip):
        self.host_ip = ip

    def getTrytes(self, hashes):
        txn = []
        command = {
            "command" : "getTrytes",
            "hashes" : hashes
        }

        stringified = json.dumps(command)

        headers = {
            "content-type" : "application/json",
            "X-IOTA-API-Version" : "1"
        }

        request = urllib.request.Request(url = self.host_ip, data = stringified.encode("utf-8"), headers = headers)
        returnData = urllib.request.urlopen(request).read()
        jsonData = json.loads(returnData)
        for dat in jsonData["trytes"]:
            txn.append(Transaction.from_tryte_string(dat.encode("utf-8")))
        return txn

    def findTransactions(self, bundle_hash):
        command = {
            'command': 'findTransactions',
            'bundles': [bundle_hash]
        }

        stringified = json.dumps(command)

        headers = {
            'content-type': 'application/json',
            'X-IOTA-API-Version': '1'
        }

        request = urllib.request.Request(url=self.host_ip, data=stringified.encode("utf-8"), headers=headers)
        returnData = urllib.request.urlopen(request).read()
        hashes = json.loads(returnData)
        return self.getTransactions(hashes["hashes"])

    def getTransactions(self, hashes):
        txn = []
        command = {
            "command" : "getTrytes",
            "hashes" : hashes
        }

        stringified = json.dumps(command)

        headers = {
            "content-type" : "application/json",
            "X-IOTA-API-Version" : "1"
        }

        request = urllib.request.Request(url = self.host_ip, data = stringified.encode("utf-8"), headers = headers)
        returnData = urllib.request.urlopen(request).read()

        jsonData = json.loads(returnData)
        for dat in jsonData["trytes"]:
            txn.append( Transaction.from_tryte_string(dat.encode("utf-8")))
        return txn

def ct(path, ip):
    bundle = []
    hashes = []
    transaction = []
    image = []
    ignore_bundle = [ 'OXFDFUFHGWFZKDHKRPQDDSWZCXNVFJT9WVYNULRNLQZJKGZLHWL9CDFQXMAIDWHPCTKKUWFKQZYKBTVHC','YZZLNUFYRFOVLGBXZCWDJVEAHI9BLVNPTLPFYHUAHKSXDAH9GFJXREXOMZBX9BLADZGTFUISWWULKBZLC']
    dic = {}

    with open(path) as f:
        hash = f.readlines()
    bundle = map(lambda x: x.replace("\n",""), hash)

    txn = getTransaction(ip)

    for bd in bundle:
        image.append(txn.findTransactions(bd))
    for img in image:
        skip = False
        trytes = [_ for _ in range(len(img))]
        tryte = TryteString.from_string("")
        for fragment in img:
            if fragment.signature_message_fragment[0:6].as_string().isdecimal():
                index = int(fragment.signature_message_fragment[0:8].as_string()[0:3])
                if index >= 0:
                    trytes[index] = fragment.signature_message_fragment[8:]
            elif fragment.signature_message_fragment[0:6].as_string() == "-01":
                skip = True
        else:
            if not all([type(x) == int for x in trytes]):
                tag = fragment.tag.as_string()
                bundle_hash = str(fragment.bundle_hash)
        if not all([type(x) == int for x in trytes]):
            for val in trytes:
                if type(val) is not int:
                    tryte += val

            tryte = str(tryte)
            if len(tryte) % 2 == 1:
                tryte = tryte[:-1]
            if not skip:
                data = from_tryte_to_picture(TryteString(tryte))

                if type(data) is not bool:
                    dic.update({str(img[0].bundle_hash) + "@" + tag : data})

        #ここyeildに変えたほうがいいかもしれん
    return dic
