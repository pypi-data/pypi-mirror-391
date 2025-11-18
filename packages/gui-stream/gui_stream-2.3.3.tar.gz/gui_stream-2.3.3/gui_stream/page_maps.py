#!/usr/bin/env python3
#
from __future__ import annotations
import pandas as pd
import tkinter as tk
from tkinter import ttk
from soup_files import File

from gui_stream.app_ui import ControllerNotifyProvider
from gui_stream.pymaps import read_file, concat_columns, DataToFileMap, LibMap, OutputMap
from gui_stream.controller_app import Controller
from gui_stream.app_ui.ui.ui_pages import UiPage
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles, Orientation, ProgressBarAdapter
)
from gui_stream.app_ui.ui.ui_pages import TopBar


#========================================================#
# Reconhecer Texto em PDF
#========================================================#

class PageMaps(UiPage):
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        # Inscreverse no objeto notificador
        self.controller.controller_conf.add_observer(self)
        self.PAGE_ROUTE = '/home/maps'
        self.PAGE_NAME = 'Gerador de Mapas'
        self.GEOMETRY = "630x345"

        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(fill='both', padx=1, pady=1)

        # Frame para os botões de input
        self.frameInputFiles = ttk.Frame(
            self.frameWidgets,
            style=self.controller.appTheme.value,
        )
        self.frameInputFiles.pack(expand=True, fill='both', padx=2, pady=3)
        self.widget_input = WidgetFiles(
            self.frameInputFiles,
            controller=self.controller,
            orientation=Orientation.H,
            disk_files=self.select_disk_files
        )
        self.widget_input.set_button_sheets()
        self.widget_input.set_button_folder()
        self.widget_input.set_button_clear()

        # Frame Inferior da janela.
        self.frameDownWidgets = ttk.Frame(
            self.frameWidgets,
            style=self.controller.appTheme.value,
        )
        self.frameDownWidgets.pack(expand=True, fill='both', padx=1, pady=1)

        # Frame para selecionar colunas com informações da planilha.
        self.frameComboboxSheet = ttk.Frame(self.frameDownWidgets, style=self.controller.appTheme.value)
        self.frameComboboxSheet.pack(expand=True, fill='both', padx=1, pady=1)

        # Combobox 1 - latitude
        self.frameLat = ttk.Frame(self.frameComboboxSheet, style=self.controller.appTheme.value)
        self.frameLat.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_lat = ttk.Label(self.frameLat, text='Coluna Latitude')
        self.lb_lat.pack(side=tk.LEFT)
        self.combo_col_latitude: ttk.Combobox = ttk.Combobox(self.frameLat, values=['vlr_coordenada_latitude'])
        self.combo_col_latitude.set('vlr_coordenada_latitude')
        self.combo_col_latitude.pack(padx=1, pady=1, expand=True, fill='both')

        # Combobox 2 - longitude
        self.frameLong = ttk.Frame(self.frameComboboxSheet, style=self.controller.appTheme.value)
        self.frameLong.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_long = ttk.Label(self.frameLong, text='Coluna Longitude')
        self.lb_long.pack(side=tk.LEFT)
        self.combo_col_longitude: ttk.Combobox = ttk.Combobox(self.frameLong, values=['vlr_coordenada_longitude'])
        self.combo_col_longitude.set('vlr_coordenada_longitude')
        self.combo_col_longitude.pack(padx=1, pady=1, expand=True, fill='both')

        # Combobox 3 - coluna separador de mapas
        self.frameSplitMap = ttk.Frame(self.frameComboboxSheet, style=self.controller.appTheme.value)
        self.frameSplitMap.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_split_map = ttk.Label(self.frameSplitMap, text='Coluna Separador de Mapa')
        self.lb_split_map.pack(side=tk.LEFT)
        self.combo_col_split_map: ttk.Combobox = ttk.Combobox(self.frameSplitMap, values=['numliv'])
        self.combo_col_split_map.set('numliv')
        self.combo_col_split_map.pack(padx=1, pady=1, expand=True, fill='both')

        # Combobox 4 - coluna identificador de ponto
        self.frameInfoPoint = ttk.Frame(self.frameComboboxSheet, style=self.controller.appTheme.value)
        self.frameInfoPoint.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_info_point = ttk.Label(self.frameInfoPoint, text='Indentificação de ponto')
        self.lb_info_point.pack(side=tk.LEFT)
        self.combo_info_point: ttk.Combobox = ttk.Combobox(self.frameInfoPoint, values=['numcdc'])
        self.combo_info_point.set('numcdc')
        self.combo_info_point.pack(padx=1, pady=1, expand=True, fill='both')

        # Combobox 5 - biblioteca plot.
        self.frameLibPlot = ttk.Frame(self.frameComboboxSheet, style=self.controller.appTheme.value)
        self.frameLibPlot.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_lib_plot = ttk.Label(self.frameLibPlot, text='Library')
        self.lb_lib_plot.pack(side=tk.LEFT)
        self.combo_lib_plot: ttk.Combobox = ttk.Combobox(self.frameLibPlot, values=['GMPLOT', 'FOLIUM'])
        self.combo_lib_plot.set('GMPLOT')
        self.combo_lib_plot.pack(padx=1, pady=1, expand=True, fill='both')

        # Botão Gerar mapa
        self.frameBtnMap = ttk.Frame(self.frameDownWidgets, style=self.controller.appTheme.value)
        self.frameBtnMap.pack(expand=True, fill='both', padx=1, pady=1)
        self.btn_create_map = ttk.Button(
            self.frameBtnMap,
            text='Gerar Mapas',
            command=self.export_maps,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_create_map.pack(expand=True, fill='both', padx=1, pady=1)

        # Adicionar os frames aqui, para receber as alterações de temas do usuário.
        self.controller.windowFrames.extend(
            [self.frameInputFiles]
        )

        self.__main_data: pd.DataFrame = pd.DataFrame()

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar
    
    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.controller.topBar.pbar

    def set_main_data(self, df: pd.DataFrame):
        self.__main_data = df

    def get_main_data(self) -> pd.DataFrame:
        return self.__main_data

    def export_maps(self):
        self.thread_main_create(self._run_export_maps)

    def _run_export_maps(self):
        self.pbar.start()
        if self.combo_lib_plot.get() == 'FOLIUM':
            _lib_map = LibMap.FOLIUM
        else:
            _lib_map = LibMap.GMPLOT

        _dir_maps = self.select_disk_files.save_dir.concat('MAPAS', create=True)
        mp_circuit = DataToFileMap(
            col_split_maps=self.combo_col_split_map.get(),
            col_lat=self.combo_col_latitude.get(),
            col_lon=self.combo_col_longitude.get(),
            cols_name_point=[self.combo_info_point.get()],
            lib_map=_lib_map,
            pbar=self.pbar,
            output_map=OutputMap.EXCEL,
        )
        mp_html = DataToFileMap(
            col_split_maps=self.combo_col_split_map.get(),
            col_lat=self.combo_col_latitude.get(),
            col_lon=self.combo_col_longitude.get(),
            cols_name_point=[self.combo_info_point.get()],
            lib_map=_lib_map,
            pbar=self.pbar,
            output_map=OutputMap.HTML,
        )
        mp_circuit.to_files(
            self.get_main_data().astype('str'),
            output_dir=_dir_maps.concat('CIRCUIT', create=True)
        )
        mp_html.to_files(
            self.get_main_data().astype('str'),
            output_dir=_dir_maps.concat('HTML', create=True)
        )
        self.pbar.stop()

    def receiver_notify_files(self, notify: ControllerNotifyProvider):
        print(f'{__class__.__name__} notificação de arquivos recebida {type(notify)}')
        self.thread_main_create(self._update_values_data_frame)

    def _update_values_data_frame(self):
        list_selected_sheets: list[File] = self.select_disk_files.get_files_sheets()
        list_data: list[pd.DataFrame] = []

        for file in list_selected_sheets:
            print(f'Lendo: {file.absolute()}')
            df = read_file(file, pbar=self.pbar)
            if not df.empty:
                list_data.append(df)
        if len(list_data) > 0:
            try:
                _data = pd.concat(list_data)
                _cols = _data.columns.tolist()
                if not 'concatenar' in _cols:
                    if ('numliv' in _cols) and ('codlcd' in _cols) and ('numrota' in _cols):
                        _data = concat_columns(_data)
                self.set_main_data(_data)
            except Exception as err:
                self.pbar.update(0, f'{err}')
                self.pbar.stop()
                self.set_main_data(pd.DataFrame())
            else:
                # Atualizar os combos
                self._update_combos()
                self.pbar.update(100, 'DataFrame atualizado!')
                self.pbar.stop()

    def _update_combos(self):
        if self.get_main_data().empty:
            return
        _cols = self.get_main_data().columns.tolist()
        self.combo_col_latitude['values'] = _cols
        self.combo_col_longitude['values'] = _cols
        self.combo_col_split_map['values'] = _cols
        self.combo_info_point['values'] = _cols

    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(self.PAGE_NAME)

    def update_state(self):
        pass
