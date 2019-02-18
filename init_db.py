#!/usr/bin/env python
# -*- coding: utf-8 -*-

import iota
from image_lib import *
from iota_lib import Iota_lib
from transaction_lib import tx_lib

import random
import sys
import os
import numpy as np
import math


ip = "http://163.225.223.80:14265"
with open("./.seed") as f:
    seed = f.read()

iota = Iota_lib(ip, seed)
tx_lib = tx_lib(ip)

tryte = to_tryte_from_picture("./mou.jpeg")
trytes = []
for i in range(math.ceil(len(tryte) / 2187)):
    trytes.append(TryteString.from_string("{0:03d}_".format(i)) + tryte[0 + i * 2179 : 2179 + i * 2179])

tag = "mouse"
iota.node_info()
address = iota.new_address(random.randint(0,100), len(trytes))
if iota.check_index():
    tx = iota.set_transaction(address["addresses"], trytes, [TryteString.from_string(tag) for _ in range(len(trytes))])
    iota.bundle_init()
count = 0

for txn in tx:
    count += 1
    iota.add_tx(txn)
    print(count)

iota.send_tx()
