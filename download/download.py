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

    def getSnapshot(self):
        command = {
            "command": "Snapshot.getState"
        }

        stringified = json.dumps(command)

        headers = {
            "content-type" : "application/json",
            "X-IOTA-API-Version" : "1"
        }
        request = urllib.request.Request(url = self.host_ip, data = stringified.encode("utf-8"), headers = headers)
        returnData = urllib.request.urlopen(request).read()
        addresses = json.loads(returnData)
        return addresses

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

def parse_argument():
    p = ArgumentParser()
    p.add_argument("host_ip", type = str)
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

    addresses = txn.getSnapshot()
    address_list = list(addresses["ixi"]["state"].keys())
    if "9" * 81 in address_list:
        address_list.remove("9" * 81)

    #数が多すぎるとbad requestが帰ってくる
    #ここの10とかの数字ベタ書きで決めてるの最高にアホ
    print("loading tryte...")
    for i in range(math.ceil(len(address_list) / 10)):
        transaction += txn.getTrytes(address_list[0 + i * 10 : 10 + i * 10])

    #transactionのbundle_hashをかぶらないようにリストにいれる
    print("searching bundle...")
    for tx in transaction:
        if tx.bundle_hash not in bundle and tx.bundle_hash != "9" * 81 and not  tx.bundle_hash in ignore_bundle:
            bundle.append(str(tx.bundle_hash))

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
