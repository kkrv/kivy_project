import os
import time
import cv2
import numpy as np
from kivy import Logger
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager

from client import *

DIR = ''


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.path_to_src = App.get_running_app().storage #os.path.join('/sdcard', 'DCIM') if platform == 'android' else ''
        self.path_to_save = os.path.join(self.path_to_src, 'res')
        self.path_to_styles = os.path.join(self.path_to_src, 'styles')
        self.camera = Camera(resolution=(640, 480), play=True)

        Logger.critical("STYLETRANSFER = {}".format("successfuly set camera"))

        self.filters = ['mosaic', 'wave']
        Logger.critical("STYLETRANSFER = {}".format("successfuly set filters names"))

        self.cur_filter_id = 0
        Logger.critical("STYLETRANSFER = {}".format("successfuly set cur filter id"))

        self.style_img = Image(source=os.path.join(self.path_to_styles, "{}.jpg".format(self.filters[self.cur_filter_id])), size=(640, 480))
        Logger.critical("STYLETRANSFER = {}".format("successfuly set style image source {}".format(os.path.abspath(self.style_img.source))))

        self.result_img = Image(source="2.jpeg", size=(640, 480))
        Logger.critical("STYLETRANSFER = {}".format(
            "successfuly set result image source {}".format(os.path.abspath(self.result_img.source))))

        Logger.critical("STYLETRANSFER = {}".format("...creating main layout"))
        main_layout = BoxLayout(orientation='vertical')

        ngrok_addr = TextInput(font_size='20sp', height=30, size_hint=(None, None))
        main_layout.add_widget(ngrok_addr)

        Logger.critical("STYLETRANSFER = {}".format("...creating img layout"))
        img_layout = BoxLayout(orientation='horizontal')
        img_layout.add_widget(self.camera)
        Logger.critical("STYLETRANSFER = {}".format("successfully add camera to img layout"))
        img_layout.add_widget(self.style_img)
        Logger.critical("STYLETRANSFER = {}".format("successfully add style img to img layout"))
        img_layout.add_widget(self.result_img)
        Logger.critical("STYLETRANSFER = {}".format("successfully add res img to img layout"))

        main_layout.add_widget(img_layout)
        Logger.critical("STYLETRANSFER = {}".format("successfully add img layout to main layout"))

        def change_filter(instance):
            Logger.critical("STYLETRANSFER = {}".format("\nCHANGE FILTER: {} -> {}".format(self.cur_filter_id, (self.cur_filter_id + 1) % len(self.filters))))
            self.cur_filter_id = (self.cur_filter_id + 1) % len(self.filters)
            Logger.critical("STYLETRANSFER = {}".format("new style img path: {}".format(os.path.join(self.path_to_styles, "{}.jpg".format(self.filters[self.cur_filter_id])))))
            self.style_img.source = os.path.join(self.path_to_styles, "{}.jpg".format(self.filters[self.cur_filter_id]))
            Logger.critical("STYLETRANSFER = {}".format("successfully changed source"))
            self.style_img.reload()
            Logger.critical("STYLETRANSFER = {}".format("successfully reloaded"))

        def apply_filter(instance):
            Logger.critical("STYLETRANSFER = {}".format("APPLY FILTER {} ({})".format(self.cur_filter_id, self.filters[self.cur_filter_id])))
            timestr = time.strftime("%Y%m%d_%H%M%S")
            im_path = "IMG_{}.png".format(timestr)
            path = os.path.join(self.path_to_save, im_path)

            Logger.critical("STYLETRANSFER = {}".format("img path: {}".format(path)))
            self.camera.export_to_png(path)
            Logger.critical("STYLETRANSFER = {}".format("successfully exported to png"))

            gen_img = process_img(path, self.cur_filter_id, ngrok_addr.text if ngrok_addr.text.strip() != '' else None)
            gen_img = cv2.imdecode(np.fromstring(bytes.fromhex(gen_img), np.uint8), cv2.IMREAD_COLOR)
            Logger.critical("STYLETRANSFER = {}".format("successfully got styliezed image"))
            res_path = os.path.join(self.path_to_save, str(self.filters[self.cur_filter_id]) + '_' + im_path)
            Logger.critical("STYLETRANSFER = {}".format("gen img path: {}".format(res_path)))
            cv2.imwrite(res_path, gen_img)
            Logger.critical("STYLETRANSFER = {}".format("successfully saved"))
            self.result_img.source = res_path
            Logger.critical("STYLETRANSFER = {}".format("successfully changed source"))
            self.result_img.reload()
            Logger.critical("STYLETRANSFER = {}".format("successfully reloaded"))

        Logger.critical("STYLETRANSFER = {}".format("...creating btn layout"))

        btn_layout = BoxLayout(orientation='horizontal')

        but_change = Button(text='Change filter')
        but_change.bind(on_press=lambda x: change_filter(x))
        btn_layout.add_widget(but_change)
        Logger.critical("STYLETRANSFER = {}".format("successfully add btn change to btn layout"))

        but_transfer = Button(text='Apply filter')
        but_transfer.bind(on_press=lambda x: apply_filter(x))
        btn_layout.add_widget(but_transfer)
        Logger.critical("STYLETRANSFER = {}".format("successfully add btn apply to btn layout"))

        main_layout.add_widget(btn_layout)
        Logger.critical("STYLETRANSFER = {}".format("successfully add btn layout to main layout"))

        self.add_widget(main_layout)
        Logger.critical("STYLETRANSFER = {}".format("successfully add widget main layout"))


class MyApp(App):

    def build(self):
        self.initilize_global_vars()
        sm = ScreenManager()
        sm.add_widget(MainScreen())
        return sm

    def initilize_global_vars(self):
        root_folder = os.path.dirname(self.user_data_dir)
        Logger.critical("STYLETRANSFER = {}".format("ROOT: {}".format(root_folder)))
        cache_folder = os.path.join(root_folder, 'style_transfer')
        Logger.critical("STYLETRANSFER = {}".format("CACHE: {}".format(cache_folder)))

        if not os.path.exists(cache_folder):
            Logger.critical("STYLETRANSFER = {}".format("create cache folder..."))
            os.makedirs(cache_folder)

        res_path = os.path.join(cache_folder, 'res')
        if not os.path.exists(res_path):
            Logger.critical("STYLETRANSFER = {}".format("create res folder..."))
            os.makedirs(res_path)

    @property
    def storage(self):
        Logger.critical("STYLETRANSFER = {}".format("storage: {}".format(os.path.join(os.path.dirname(self.user_data_dir), 'style_transfer'))))
        return os.path.join(os.path.dirname(self.user_data_dir), 'style_transfer')


MyApp().run()
