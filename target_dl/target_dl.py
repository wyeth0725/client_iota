#/usr/bin/env python
# -*- coding: utf-8 -*-

from iota import *
import urllib
import json
from argparse import ArgumentParser
import math
import sys
import os
from op_image import from_tryte_to_picture

class getTransaction:
    def __init__(self, args):
        self.host_ip = args.host_ip

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

def parse_argument():
    p = ArgumentParser()
    p.add_argument("host_ip", type = str)
    p.add_argument("snapshot", type = str)
    #p.add_argument("seed", type = str)
    #p.add_argument("--file", type = str)
    args = p.parse_args()
    try:
        if type(args.host_ip) is not str: raise ValueError("host_ip is must be string.")
        #if type(args.seed) is not str: raise ValueError("seed is must be string.")
        #if type(args.file) is not str: raise ValueError("filename is must be string.")
    except Exception as ex:
        print(ex, file = sys.stderr)
        sys.exit()
    return args

def main():

    #流れとしては全部のアドレス→ハッシュからtrytesでbundleのリスト作ってbundleを全部ゲットする

    args = parse_argument()
    bundle = []
    hashes = []
    transaction = []
    image = []
    ignore_bundle = ['OXFDFUFHGWFZKDHKRPQDDSWZCXNVFJT9WVYNULRNLQZJKGZLHWL9CDFQXMAIDWHPCTKKUWFKQZYKBTVHC','YZZLNUFYRFOVLGBXZCWDJVEAHI9BLVNPTLPFYHUAHKSXDAH9GFJXREXOMZBX9BLADZGTFUISWWULKBZLC']
    data = {}
    txn = getTransaction(args)

    with open(args.snapshot) as f:
        bundle = f.readlines()
    bundle = list(map(lambda x: x.replace("\n","") , bundle))
    print(bundle)
    print("get image...")
    for bd in bundle:
        image.append(txn.findTransactions(bd))
    print(list(map(lambda x: len(x), image)))
    bundle = []

    count = 0
    data_dir = "./data/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for img in image:
        trace_info = "origin : \nediter : "
        trytes = [_ for _ in range(len(img))]
        tryte = TryteString.from_string("")
        for fragment in img:
            if fragment.signature_message_fragment[0:6].as_string().isdecimal():
                index = int(fragment.signature_message_fragment[0:8].as_string()[0:3])
                if index >= 0:
                    trytes[index] = fragment.signature_message_fragment[8:]
            elif fragment.signature_message_fragment[0:6].as_string() == "-01":
                trace_info = fragment.signature_message_fragment.as_string()[4:].replace("./","")

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

            if from_tryte_to_picture(TryteString(tryte), tag.replace(" ","_"), trace_info, count, data_dir):
                count += 1
                bundle.append(str(img[0].bundle_hash))

    with open("picture.txt","w") as f:
        f.writelines(map(lambda x: x + "\n", bundle))


if __name__ == "__main__":
    main()
