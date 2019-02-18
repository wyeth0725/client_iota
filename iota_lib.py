#/usr/bin/env python
# -*- coding: utf-8 -*-

from iota import *

import json
import urllib
import random
import numpy as np
from transaction_lib import tx_lib
from image_lib import from_tryte_to_picture

class Iota_lib:
    def __init__(self, ip, seed):
        self.api = Iota(ip, seed.replace("\n", ""))
        self.ip = ip
        self.tx_lib = tx_lib(ip)
        self.depth = 10

    def node_info(self):
        self.node_state = self.api.get_node_info()

    def check_index(self):
        if( str(self.node_state["latestMilestoneIndex"]) == str(self.node_state["latestSolidSubtangleMilestoneIndex"])):
            return True
        else:
            return False

    def set_transaction(self, address, message, tag):
        tx = []
        for adr, msg, tg in zip(address, message, tag):
            tx.append(ProposedTransaction(
                            address = adr,
                            message = msg,
                            tag = tg,
                            value = 0,
            ))
        return tx

    def new_address(self, index, count):
        return self.api.get_new_addresses(index, count)

    def bundle_init(self):
        self.bundle = ProposedBundle()

    def get_bundle(self):
        approve_hash = self.get_approvee_hash()
        trunk_bundle, trunk_image = self.tx_lib.getTrytes(approve_hash["trunkTransaction"])
        branch_bundle, branch_image = self.tx_lib.getTrytes(approve_hash["branchTransaction"])
        return {"trunk":{"bundle": trunk_bundle, "image": trunk_image},"branch":{"bundle": branch_bundle, "image": branch_image},"approve_hash": approve_hash}

    def get_approvee_hash(self):
        command = {
            "command" : "getTransactionsToApprove",
            "depth": self.depth,
        }
        stringified = json.dumps(command)

        headers = {
            "content-type" : "application/json",
            "X-IOTA-API-Version" : "1",
        }
        request = urllib.request.Request(url = self.ip, data = stringified.encode("utf-8"), headers = headers)
        returnData = urllib.request.urlopen(request).read()

        return json.loads(returnData)

    def get_picture(self, image):
        msg = str(self.combine_tryte(image))
        if len(msg) % 2 == 1:
            msg = msg[:-1]
        try:
        #print(TryteString(msg).as_string())
        #int(TryteString(msg)[0:8].as_string()[0:3])
            return from_tryte_to_picture(TryteString(msg))
        except:
            return np.ndarray([0])

    def combine_tryte(self, image):
        trytes = [ _ for _ in range(len(image))]
        tryte = TryteString.from_string("")
        for frag in image:
            if frag.signature_message_fragment[0:6].as_string().isdecimal():
                index = int(frag.signature_message_fragment[0:8].as_string()[0:3])
                if index >= 0:
                    trytes[index] = frag.signature_message_fragment[8:]
        if not all([type(x) == int for x in trytes]):
            for val in trytes:
                if type(val) is not int:
                    tryte += val
        return tryte

    def send_tx(self, tx):
        try:
            depth = random.randint(3,12)
            self.bundle.finalize()
            print(self.bundle.hash)
            self.api.send_transfer(depth, tx)
            print("uploaded")
            return self.bundle.hash
        except:
            pass

    def add_tx(self, tx):
        self.bundle.add_transaction(tx)

    def combine_tryte_for_source(self, code):
        index = []
        trytes = [_ for _ in range(len(code))]
        tryte = TryteString.from_string("")
        for fragment in code:
            if fragment.signature_message_fragment[0:6].as_string().isdecimal():
                index = int(fragment.signature_message_fragment[0:8].as_string()[0:3])
                if index >= 0:
                    trytes[index] = fragment.signature_message_fragment[8:]
        if not all([type(x) == int for x in trytes]):
            for val in trytes:
                tryte += val
        return tryte
