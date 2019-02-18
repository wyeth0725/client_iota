#!/usr/bin/env python
## -*- coding: utf-8 -*-

import kivy

from kivy.app import App
from kivy.app import Builder
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivy.properties import StringProperty, ObjectProperty, DictProperty
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from functools import partial

from iota import *
from image_lib import *
from iota_lib import Iota_lib
from transaction_lib import tx_lib
import subprocess
import random
import sys
import time
import os
import glob
from datetime import datetime

#read font file
directory = os.path.dirname(os.path.abspath(__file__))
resource_add_path(directory)
LabelBase.register(DEFAULT_FONT, 'mplus-2c-regular.ttf')

class PopupChooseFile(BoxLayout):
    #corrent directory. throw path of FileChooserIconView
    current_dir = os.path.dirname(os.path.abspath(__file__))
    select = ObjectProperty(None)
    cancel = ObjectProperty(None)

class PopupSourceFile(BoxLayout):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    select = ObjectProperty(None)
    cancel = ObjectProperty(None)

class IpPopup(BoxLayout):
    ip = ObjectProperty(None)
    text = StringProperty()
    input_seed = ObjectProperty(None)
    seed = StringProperty()

class TagPopup(BoxLayout):
    tag = ObjectProperty(None)
    validate = ObjectProperty(None)
    text = StringProperty()
    selection = StringProperty()
    source = StringProperty()

class Confirm_source(BoxLayout):
    text = StringProperty()
    upload = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SourcePopup(BoxLayout):
    source = StringProperty()
    text = StringProperty()

class ConfirmPopup_trunk(BoxLayout):
    text = StringProperty()
    y_a = ObjectProperty(None)
    n_a = ObjectProperty(None)
    pic = ObjectProperty()
    approve = DictProperty()

class ConfirmPopup_branch(BoxLayout):
    text = StringProperty()
    y_a = ObjectProperty(None)
    n_a = ObjectProperty(None)
    pic = ObjectProperty()
    approve = DictProperty()

class HashPopup(BoxLayout):
    text = StringProperty()
    validate = ObjectProperty(None)
    cancel = ObjectProperty(None)

class IotaWidget(BoxLayout):
    text = StringProperty()
    image = False
    status = ObjectProperty(None)
    source = StringProperty(None)
    selection = StringProperty(None)

    def __init__(self, **kwargs):
        super(IotaWidget, self).__init__(**kwargs)
        self.text = ""
        self.ip = "http://163.225.223.50:14265" #default. change by bottun
        self.source = ""
        self.tag = ""
        self.flag = 0
        self.yn = [False, False]
        #if there is a seed file, read seed
        if os.path.exists(directory + "/.seed"):
            with open(directory + "/.seed") as f:
                self.seed = f.read()
                self.iota_init()
        else:
            self.seed = ""

        self.tx_lib = tx_lib(self.ip)

        self.editer_flag = 0
        self.edited = False
        self.done_approvee_bundle = []
        self.dont_approvee_bundle = []
        #画像じゃなければ無視するようにしたいので要変更
        #というか変更したらこれいらない
        #seedみたいにファイルから読み込む形式にする？
        #編集プログラムの登録のときにそのハッシュも登録すれば避けれる
        self.ignore_bundle = ['OXFDFUFHGWFZKDHKRPQDDSWZCXNVFJT9WVYNULRNLQZJKGZLHWL9CDFQXMAIDWHPCTKKUWFKQZYKBTVHC','YZZLNUFYRFOVLGBXZCWDJVEAHI9BLVNPTLPFYHUAHKSXDAH9GFJXREXOMZBX9BLADZGTFUISWWULKBZLC']

    #init iota. set to False so that it can not be upload if not init
    def iota_init(self):
        if self.ip != "" and self.seed != "" and self.flag == 0:
            self.iota = Iota_lib(self.ip, self.seed)
            self.tx_lib = tx_lib(self.ip)
            self.flag = 1
            return True
        elif self.flag == 1:
            return True
        else:
            return False

    def choose_picture(self):
        content = PopupChooseFile(select = self.select, cancel = self.cancel)
        self.popup = Popup(title = "Select picture", content = content)
        self.popup.open()

    def select(self, selection):
        self.popup.dismiss()
        content = TagPopup(tag = self.input_tag, validate = self.validate_picture, text = "Input tag", selection = selection)
        self.popup = Popup(title = "Input tag", content = content)
        self.popup.open()

    def cancel(self):
        self.source = ""
        self.popup.dismiss()

    def validate_picture(self, path):
        root, ext = os.path.splitext(path)
        ext_list = ["jpg", "jpeg", "png"]
        if ext != ".jpg" and ext != ".jpeg" and ext != ".png":
            self.status.text = "Should image file"
            self.source = ""
            self.popup.dismiss()
        else:
            self.popup.dismiss()
            self.source = path
            self.status.text = "Picture: {}, Tag: {}".format(os.path.basename(path), self.tag)

    def input_tag(self, tag):
        self.tag = tag

    def choose_ip(self):
        content = IpPopup(ip = self.address, text = "choose full node IP", input_seed = self.input_seed, seed = self.seed)
        self.popup = Popup(title = "choose IP", content = content)
        self.popup.open()

    def address(self, ip):
        self.ip = ip
        self.popup.dismiss()

    def input_seed(self, seed):
        self.seed = seed
        #save the newly input seed
        self.flag = 0
        with open(directory + "/.seed", "w") as f:
            f.write(self.seed)

    def prepare_upload(self):
        if self.iota_init():
            if self.source != "" and self.tag != "":
                tx = self.prepare_transaction()
                self.prepare_bundle(tx)
            else:
                self.status.text = "Choose picture"
        else:
            self.status.text = "Input seed"

    #def prepare_upload_trace(self, pic, tag, origin, hash):
    def prepare_upload_trace(self):
        print(str(self.pic_index) + "/" + str(len(self.pic_list)))
        if self.iota_init():
            #tx = self.prepare_transaction_trace(pic, tag, origin, hash)
            tx = self.prepare_transaction_trace(self.pic_list[self.pic_index][0], self.pic_list[self.pic_index][1], self.pic_list[self.pic_index][2], self.pic_list[self.pic_index][3])
            self.prepare_bundle(tx)

    def prepare_transaction(self):
        tryte = to_tryte_from_picture(self.source)
        trytes = []
        for i in range(math.ceil(len(tryte) / 2187)):
            trytes.append(TryteString.from_string("{0:03d}_".format(i)) + tryte[0 + i * 2179 : 2179 + i * 2179])

        self.iota.node_info()
        address = self.iota.new_address(random.randint(0, 100), len(trytes))
        if( self.iota.check_index() ):
            tx = self.iota.set_transaction(address["addresses"], trytes, [TryteString.from_string(self.tag) for _ in range(len(trytes))])
            self.iota.bundle_init()
            return tx
        else: raise ValueError("Different latestMilestoneIndex and latestSolidSubtangleMilestoneIndex")

    def prepare_transaction_trace(self, pic, tag, origin, hash):
        print(pic)
        tryte = to_tryte_from_picture_trace(pic)
        trytes = []
        for i in range(math.ceil(len(tryte)/ 2187)):
            trytes.append(TryteString.from_string("{0:03d}_".format(i)) + tryte[0 + i * 2179 : 2179 + i * 2179])

        #ここでこのトランザクションだけ弾けるようになんかする
        trytes.append(TryteString.from_string("-01_origin : " + origin + "\nediter : " + hash))
        self.iota.node_info()
        address = self.iota.new_address(random.randint(0, 100), len(trytes))
        if(self.iota.check_index()):
            tx = self.iota.set_transaction(address["addresses"], trytes, [TryteString.from_string(tag) for _ in range(len(trytes))])
            self.iota.bundle_init()
            return tx
        else: raise ValueError("Different latestMilestoneIndex and latestSolidSubtangleMilestoneIndex")

    def prepare_bundle(self, tx):
        self.index = 0
        self.length = len(tx)
        approve_image = self.iota.get_bundle()
        #self.display_trunk_image(approve_image, tx)
        self.next(tx, approve_image)

    def display_trunk_image(self, approve, tx):
        if not approve["trunk"]["bundle"] in self.ignore_bundle + self.dont_approvee_bundle + self.done_approvee_bundle:
            pic = self.iota.get_picture(approve["trunk"]["image"])
            if pic.all() == np.ndarray([0]).all():
                self.yn[0] = True
                #tx[self.index].trunk_transaction_hash = approve["approve_hash"]["trunkTransaction"]
                self.done_approvee_bundle.append(approve["trunk"]["bundle"])
                self.display_branch_image(approve, tx)
            else:
                self.confirm_picture_trunk(approve, pic, tx)
        elif approve["trunk"]["bundle"] in self.done_approvee_bundle:
            self.yn[0] = True
            #tx[self.index].trunk_transaction_hash = approve["approve_hash"]["trunkTransaction"]
            self.display_branch_image(approve, tx)
        else:
            self.display_branch_image(approve, tx)

    def display_branch_image(self, *args, **kwargs):
        approve = args[0]
        tx = args[1]
        if not approve["branch"]["bundle"] in self.ignore_bundle + self.dont_approvee_bundle + self.done_approvee_bundle:
            pic = self.iota.get_picture(approve["branch"]["image"])
            if pic.all() == np.ndarray([0]).all():
                self.yn[1] = True
                self.done_approvee_bundle.append(approve["branch"]["bundle"])
                self.next(tx, approve)
            else:
                self.confirm_picture_branch(approve, pic, tx)
        elif approve["branch"]["bundle"] in self.done_approvee_bundle:
            self.yn[1] = True
            self.next(tx, approve)
        else:
            self.next(tx, approve)

    def confirm_picture_trunk(self, approve, pic, tx):
        texture = Texture.create(size = (pic.shape[1], pic.shape[0]), colorfmt = "bgr", bufferfmt = "ubyte")
        texture.blit_buffer(pic.tostring(), colorfmt = "bgr", bufferfmt = "ubyte")
        texture.flip_vertical()
        self.pic = Image(size_hint = (pic.shape[1], pic.shape[0]))
        self.pic.texture = texture
        self.pic.opacity = 1
        #ここcontentからtx消す
        content = ConfirmPopup_trunk(text = approve["trunk"]["image"][0].tag.as_string(), pic = self.pic, y_a = self.yes_t, n_a = self.no_t, approve = approve)
        self.trunk_popup = Popup(title = "confirm picture trunk", content = content)
        self.trunk_popup.open()
        self.trunk_popup.bind(on_dismiss = partial(self.display_branch_image, approve, tx))

    def confirm_picture_branch(self, approve, pic, tx):
        texture = Texture.create(size = (pic.shape[1], pic.shape[0]), colorfmt = "bgr", bufferfmt = "ubyte")
        texture.blit_buffer(pic.tostring(), colorfmt = "bgr", bufferfmt = "ubyte")
        texture.flip_vertical()
        self.pic = Image(size_hint = (pic.shape[1], pic.shape[0]))
        self.pic.texture = texture
        self.pic.opacity = 1
        #ここcontentからtx消す
        content = ConfirmPopup_branch(text = approve["branch"]["image"][0].tag.as_string(), approve = approve, pic = self.pic, y_a = self.yes_b, n_a = self.no_b)
        self.branch_popup = Popup(title = "confirm picture branch", content = content)
        self.branch_popup.open()
        self.branch_popup.bind(on_dismiss = partial(self.next, tx, approve))

    #引数にapprove追加してこの中で
    #tx[self.index].trunk_transaction_hash = approve["approve_hash"]["trunkTransaction"]
    #tx[self.index].branch_transaction_hash = approve["approve_hash"]["branchTransaction"]
    #これ実行する
    #そうすればpopup objectにtx含まれないようにできるからクソみたいなエラー消せるはず
    #それかもうtxもself.txにしてしまうかどっちか
    def next(self, *args, **kwargs):
        tx = args[0]
        approve = args[1]
        if(self.yn[0]):
            tx[self.index].trunk_transaction_hash = approve["approve_hash"]["trunkTransaction"]
        elif(self.yn[1]):
            tx[self.index].branch_transaction_hash = approve["approve_hash"]["branchTransaction"]
        self.iota.add_tx(tx[self.index])
        self.index += 1
        self.yn = [False, False]
        if self.index < self.length:
            approve_image = self.iota.get_bundle()
            #self.display_trunk_image(approve_image, tx)
            self.next(tx, approve_image)
        else:
            self.upload_picture(tx)
            if self.edited and self.pic_index < len(self.pic_list) - 1:
                self.pic_index += 1
                self.prepare_upload_trace()


    def upload_picture(self, tx):
        editer_hash = self.iota.send_tx(tx)
        if self.editer_flag == 1:
            self.status.text = "hash: {}".format(editer_hash)
        elif self.edited:
            self.bundlelist.append(str(editer_hash) + "\n")

    def yes_t(self, approve):
        self.done_approvee_bundle.append(approve["trunk"]["bundle"])
        self.yn[0] = True
        self.trunk_popup.dismiss()
        #tx[self.index].trunk_transaction_hash = approve["approve_hash"]["trunkTransaction"]

    def no_t(self, approve):
        self.dont_approvee_bundle.append(approve["trunk"]["bundle"])
        self.trunk_popup.dismiss()

    def yes_b(self, approve):
        self.done_approvee_bundle.append(approve["branch"]["bundle"])
        self.yn[1] = True
        self.branch_popup.dismiss()
        #tx[self.index].branch_transaction_hash = approve["approve_hash"]["branchTransaction"]
        #self.iota.add_tx(tx[self.index])

    def no_b(self, approve):
        self.dont_approvee_bundle.append(approve["branch"]["bundle"])
        self.branch_popup.dismiss()
        #self.iota.add_tx(tx[self.index])

################add####################
    def resister_program(self):
        content = PopupSourceFile(select = self.select_source, cancel = self.cancel_source)
        self.popup = Popup(title = "Select python file", content = content)
        self.popup.open()

    def select_source(self, path):
        root, ext = os.path.splitext(path)
        if ext != ".py":
            self.status.text = "Should python file"
            self.popup.dismiss()
        else:
            self.popup.dismiss()
            self.python_file = path
            self.status.text = path
            content = Confirm_source(upload = self.upload_source, cancel = self.cancel_up, text = path)
            self.popup = Popup(title = "upload?", content = content)
            self.popup.open()

    def cancel_source(self):
        self.python_file = ""
        self.popup.dismiss()
        self.status.text = ""

    def upload_source(self):
        self.popup.dismiss()
        with open(self.python_file) as f:
            data = "".join(f.readlines()).replace("\n","@@@@")
        data = TryteString.from_string(data)
        trytes = []
        for i in range(math.ceil(len(data) / 2187)):
            trytes.append(TryteString.from_string("{0:03d}_".format(i)) + data[0 + i * 2179 : 2179 + i * 2179])

        self.iota.node_info()
        address = self.iota.new_address(random.randint(0, 100), len(trytes))
        if( self.iota.check_index() ):
            tx = self.iota.set_transaction(address["addresses"], trytes, [TryteString.from_string(os.path.basename(self.python_file)[0:13]) for _ in range(len(trytes))])
        else: raise ValueError("Different latestMilestoneIndex and latestSolidSubtangleMilestoneIndex")
        if self.iota_init():
            self.editer_flag = 1
            self.iota.bundle_init()
            self.prepare_bundle(tx)

    def cancel_up(self):
        self.popup.dismiss()
        self.python_file = ""

    def run_edit(self):
        #ハッシュと画像のjsonがあるディレクトリを入力して処理する
        content = HashPopup(text = "input editer hash and picture directory", validate = self.validate_hash, cancel = self.cancel_edit)
        self.popup = Popup(title = "input editer hash and picture directory", content = content)
        self.popup.open()

    def validate_hash(self, hash, path, args):
        self.popup.dismiss()
        self.bundlelist = []
        tx = self.tx_lib.getSources(hash)
        code = self.iota.combine_tryte_for_source(tx)
        editer = code.as_string().replace("@@@@","\n")
        subprocess.call("mkdir tmp", shell = True)
        os.chdir("./tmp")
        with open("./tmp.py","w") as f:
            f.writelines(editer)

        tx = self.tx_lib.getSources("FIWCAL9UOHCFJPHUJRNZRKHODHHIPZFWCUWLQXERJJIRWWDZRLKTAFHJXHFPWIGOKTEGNE9OZZIUTQJHW")
        code = self.iota.combine_tryte_for_source(tx)
        editer = code.as_string().replace("@@@@","\n")
        with open("edit_lib.py","w") as f:
            f.writelines(editer)
        if path != "":
            subprocess.call("python tmp.py", shell = True)
        else:
            subprocess.call("python tmp.py {} {} {}".format(path, self.ip, args), shell = True)

        picture_list = glob.glob("./*.jpg")
        picture_list += glob.glob("./*.png")
        picture_list += glob.glob("./*.jpeg")
        #このリストのファイルから.jpgを消したのが元画像のバンドルハッシュ
        #これとhash変数に入っているediterのバンドルハッシュをセットにしてエクストラトランザクションに入れて画像とそのトランザクションをバンドルにしてアップロード
        self.edited = True
        self.pic_list = []
        self.pic_index = 0
        for pic in picture_list:
            #全部処理してpopup出てきてる感じになってるから2回めのpopupからイカれる
            ls = pic.split("@")
            tag, ext = os.path.splitext(ls[1])
            self.pic_list.append([pic, tag, ls[0], hash])
            #self.prepare_upload_trace(pic, tag, ls[0], hash)
        self.prepare_upload_trace()
        os.chdir("..")
        #subprocess.call("rm -r tmp", shell = True)
        dt = datetime.now().strftime('%Y%m%d%H%M')
        with open("./" + dt + ".txt", "w") as f:
            f.writelines(self.bundlelist)

    def cancel_edit(self):
        self.popup.dismiss()

class IotaApp(App):
    def __init__(self, **kwargs):
        super(IotaApp, self).__init__(**kwargs)
        self.title = "iota"

    def build(self):
        return IotaWidget()

if __name__ == "__main__":
    IotaApp().run()
