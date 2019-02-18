#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from iota import Transaction

class tx_lib:
    def __init__(self, ip):
        self.host_ip = ip

    def getTrytes(self, hashes):
        txn = []
        if type(hashes) == dict:
            command = {
                "command" : "getTrytes",
                "hashes" : hashes["hashes"]
            }
        elif type(hashes) == str:
            command = {
                "command" : "getTrytes",
                "hashes" : [hashes]
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
        return self.findTransactions(txn[0])

    def findTransactions(self, txn):
        command = {
            'command': 'findTransactions',
            'bundles': [str(txn.bundle_hash)]
        }

        stringified = json.dumps(command)

        headers = {
            'content-type': 'application/json',
            'X-IOTA-API-Version': '1'
        }

        request = urllib.request.Request(url=self.host_ip, data=stringified.encode("utf-8"), headers=headers)
        returnData = urllib.request.urlopen(request).read()
        image_hash = json.loads(returnData)

        return txn.bundle_hash, self.getTransactions(image_hash)

    def getTransactions(self, hashes):
        txn = []
        command = {
            "command" : "getTrytes",
            "hashes" : hashes["hashes"]
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


    def getSources(self, hash):
        command = {
            'command': 'findTransactions',
            'bundles': [hash]
        }

        stringified = json.dumps(command)

        headers = {
            'content-type': 'application/json',
            'X-IOTA-API-Version': '1'
        }

        request = urllib.request.Request(url=self.host_ip, data=stringified.encode("utf-8"), headers=headers)
        returnData = urllib.request.urlopen(request).read()
        hash = json.loads(returnData)

        return self.getTransactions(hash)
