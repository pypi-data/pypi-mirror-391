#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from soup_files import File
from gui_stream.app_ui.core.page import ThreadApp
from gui_stream.app_ui.core.select_files import PreferencesApp, AppFileDialog, ControllerConfig
from gui_stream.app_ui.ui.ui_pages import UiController
from gui_stream.app_ui.ui.ui_menu_bar import UIMenuBar
from gui_stream.app_ui.run_app import load_conf_user
import ocr_stream as ocr

__version__ = '2.3'


def create_controller(prefs_app: PreferencesApp) -> Controller:
    """
        Gera uma controller personalizada, priorizando
    as preferências do usuário em detrimento das informações padrão.
    """
    prefs_app = load_conf_user(prefs_app)
    # Definir controller para arquivos
    file_dialog: AppFileDialog = AppFileDialog(prefs_app)
    controller_files: ControllerConfig = ControllerConfig(file_dialog)
    
    # Definir controller do App.
    controller: UiController = Controller(
        controller_conf=controller_files, pages=[]
    )
    return controller 
    
    
class Controller(UiController):
    def __init__(self, *, thread_app=ThreadApp(), controller_conf, pages):
        super().__init__(thread_app=thread_app, controller_conf=controller_conf, pages=pages)
        self.binary: ocr.BinTesseract = ocr.BinTesseract()
        
    def __get_path_tesseract_system(self) -> File | None:
        __bn = self.binary.get_tesseract()
        if __bn is None:
            return None
        return __bn if __bn.exists() else None
            
    def __get_path_tesseract_config(self) -> File | None:
        """
            Retorna o caminho do tesseract salvo nas preferências do usuário.
        """
        for k in self.appPrefs.config:
            if k == 'path_tesseract':
                self.binary.set_tesseract(File(self.appPrefs.config['path_tesseract']))
                break
        __bin_tess = self.binary.get_tesseract()
        if __bin_tess is None:
            return None
        return __bin_tess if __bin_tess.exists() else None
    
    def get_path_tesseract(self) -> File | None:
        if self.__get_path_tesseract_config() is not None:
            return self.__get_path_tesseract_config()
        return self.__get_path_tesseract_system()
        
 
class AppMenuBar(UIMenuBar):
    
    def __init__(self, *, controller: Controller, version='-'):
        super().__init__(controller=controller, version=version)
        self.controller: Controller = controller
        
        # Executável tesseract
        out = self.controller.get_path_tesseract()
        tess = '-' if out is None else out.absolute()
        text_tooltip = 'indisponível' if out is None else 'disponível'
        
        self.index_file_webdriver: int = self.add_item_menu(
            tooltip=tess,
            name=f'Tesseract: ',
            cmd=self.change_file_tesseract,
            submenu=self.menu_config,
        )

    def change_file_tesseract(self):
        f = self.controller.controller_conf.fileDialog.open_filename()
        if f is None:
            return
        self.controller.appPrefs.set_config('path_tesseract', f)
        self.menu_config.entryconfig(
            self.index_file_webdriver,
            label=f'Tesseract: {f}'
        )
        self.controller.send_notify_files()

    def update_menu_bar(self):
        super().update_menu_bar()
        # Atualizar o webdriver
        f_tess: File = File(self.controller.appPrefs.config['path_tesseract'])
        self.menu_config.entryconfig(
            self.index_file_webdriver,
            label=f'Arquivo: {f_tess.absolute()}' if f_tess.exists() else 'Tesseract: indisponível',
        )
         
         
