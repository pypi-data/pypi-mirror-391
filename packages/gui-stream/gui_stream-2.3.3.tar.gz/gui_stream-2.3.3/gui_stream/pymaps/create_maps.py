#!/usr/bin/env python3
from abc import ABC, abstractmethod
from enum import Enum
from gui_stream.pymaps.map_adapter import MapConvert, LibMap
from soup_files import File, Directory, ProgressBarAdapter, CreatePbar
import pandas as pd


def concat_columns(
            df: pd.DataFrame, *,
            cols: list[str] = ['numliv', 'codlcd', 'numrota'],
            new_col: str = 'concatenar',
            separator: str = '-',
        ) -> pd.DataFrame:
    df[new_col] = df[cols].astype(str).agg(separator.join, axis=1)
    return df.astype('str')


def get_circuit_columns() -> list[str]:
    return [
        'numliv', 'codlcd', 'numrota', 'numcdc',
        'vlr_coordenada_latitude', 'vlr_coordenada_longitude'
    ]


class OutputMap(Enum):

    HTML = 'html'
    EXCEL = 'excel'
    NOT_IMPLEMENTED = 'not_implemented'


class ABCMapToFile(ABC):
    """
        Criar mapas circuit/html a partir de um arquivo excel/csv ou dataframe.
    """

    def __init__(
            self, *,
            col_split_maps: str = 'numliv',
            col_lat: str = 'vlr_coordenada_latitude',
            col_lon: str = 'vlr_coordenada_longitude',
            cols_name_point: list[str] = [],
            col_filenames: str = None,
            prefix_name: str = None,
            lib_map: LibMap = LibMap.GMPLOT,
            pbar: ProgressBarAdapter = CreatePbar().get(),
            ):
        #
        self.col_split_maps: str = col_split_maps
        self.col_lat: str = col_lat
        self.col_lon: str = col_lon
        self.cols_name_point: list[str] = cols_name_point
        self.col_filenames: str = col_filenames
        self.prefix_name = prefix_name
        self.lib_map: LibMap = lib_map
        self.pbar: ProgressBarAdapter = pbar

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.pbar = pbar

    @abstractmethod
    def to_files(self, data: pd.DataFrame, *, output_dir: Directory, replace: bool = False):
        pass


class ImplementMapToHtml(ABCMapToFile):

    def __init__(
                self, *,
                col_split_maps: str = 'numliv',
                col_lat: str = 'vlr_coordenada_latitude',
                col_lon: str = 'vlr_coordenada_longitude',
                cols_name_point: list[str] = [],
                col_filenames: str = None,
                prefix_name: str = None,
                lib_map: LibMap = LibMap.GMPLOT,
                pbar: ProgressBarAdapter = CreatePbar().get()
            ):
        super().__init__(
            col_split_maps=col_split_maps,
            col_lat=col_lat,
            col_lon=col_lon,
            cols_name_point=cols_name_point,
            col_filenames=col_filenames,
            prefix_name=prefix_name,
            lib_map=lib_map, pbar=pbar
        )
        self.map_convert: MapConvert = MapConvert(
            lat_col=self.col_lat, lon_col=self.col_lon, name_col=self.cols_name_point, lib_map=self.lib_map
        )

    def to_files(self, df: pd.DataFrame, *, output_dir: Directory, replace: bool = False):
        if df.empty:
            print(f'{__class__.__name__} DataFrame vazio.')
            return
        output_dir.mkdir()
        # Remover linhas vazias das coordenadas.
        df = df[
            df[self.col_lat].notna() & (df[self.col_lon].astype(str).str.strip() != "")
            ]
        # Dividir o DataFrame em partes, separados pelo limitador de rota => self.col_split_maps
        col_items: list[str] = df[self.col_split_maps].drop_duplicates().values.tolist()
        max_num: int = len(col_items)
        print()
        self.pbar.start()
        for idx, route in enumerate(col_items):
            current: pd.DataFrame = df[df[self.col_split_maps] == route]
            if current.empty:
                continue
            if self.prefix_name is None:
                file_path: File = output_dir.join_file(f'{idx+1}-{route}.html')
            else:
                file_path: File = output_dir.join_file(f'{self.prefix_name}-{route}.html')
            if not replace:
                if file_path.exists():
                    self.pbar.update_text(f'[PULANDO]: {file_path.absolute()}')
                    continue
            # Exportar para html
            self.pbar.update(
                ((idx+1) / max_num) * 100,
                f'[EXPORTANDO Html]: {idx+1} / {max_num} {file_path.basename()}',
            )
            try:
                self.map_convert.export_html(current, output_file=file_path)
            except Exception as err:
                print(err)
            finally:
                del file_path


class ImplementMapCircuit(ABCMapToFile):

    def __init__(
                self, *,
                col_split_maps: str = 'numliv',
                col_lat: str = 'vlr_coordenada_latitude',
                col_lon: str = 'vlr_coordenada_longitude',
                cols_name_point: list[str] = [],
                col_filenames: str = None,
                prefix_name: str = None,
                lib_map: LibMap = LibMap.GMPLOT,
                pbar: ProgressBarAdapter = CreatePbar().get()
            ):
        super().__init__(
                col_split_maps=col_split_maps,
                col_lat=col_lat,
                col_lon=col_lon,
                cols_name_point=cols_name_point,
                col_filenames=col_filenames,
                prefix_name=prefix_name,
                lib_map=lib_map, pbar=pbar
            )

    def to_files(self, df: pd.DataFrame, *, output_dir: Directory, replace: bool = False):
        if df.empty:
            print(f'{__class__.__name__} DataFrame vazio.')
            return
        output_dir.mkdir()
        # Remover linhas vazias das coordenadas.
        df = df[
            df[self.col_lat].notna() & (df[self.col_lon].astype(str).str.strip() != "")
            ]
        # Dividir o DataFrame em partes, separados pelo limitador de rota => self.col_split_maps
        col_items: list[str] = df[self.col_split_maps].drop_duplicates().values.tolist()
        max_num: int = len(col_items)
        print()
        self.pbar.start()
        for idx, route in enumerate(col_items):
            current: pd.DataFrame = df[df[self.col_split_maps] == route]
            if current.empty:
                continue
            if self.prefix_name is None:
                file_path: File = output_dir.join_file(f'{idx + 1}-{route}.xlsx')
            else:
                file_path: File = output_dir.join_file(f'{self.prefix_name}-{route}.xlsx')
            if not replace:
                if file_path.exists():
                    self.pbar.update_text(f'[PULANDO]: {file_path.absolute()}')
                    continue
            # Exportar para html
            self.pbar.update(
                ((idx + 1) / max_num) * 100,
                f'[EXPORTANDO Excel]: {idx + 1} / {max_num} {file_path.basename()}',
            )
            try:
                current.to_excel(file_path.absolute(), index=False)
            except Exception as err:
                print(err)
            finally:
                del file_path


class DataToFileMap(object):
    def __init__(
            self, *,
            col_split_maps: str = 'numliv',
            col_lat: str = 'vlr_coordenada_latitude',
            col_lon: str = 'vlr_coordenada_longitude',
            cols_name_point: list[str] = [],
            col_filenames: str = None,
            prefix_name: str = None,
            lib_map: LibMap = LibMap.GMPLOT,
            pbar: ProgressBarAdapter = CreatePbar().get(),
            output_map: OutputMap = OutputMap.HTML,
            ):
        self.lat_col = col_lat
        self.lon_col = col_lon
        if output_map == OutputMap.HTML:
            self.map_to_file: ABCMapToFile = ImplementMapToHtml(
                col_split_maps=col_split_maps,
                col_lat=col_lat,
                col_lon=col_lon,
                cols_name_point=cols_name_point,
                col_filenames=col_filenames,
                prefix_name=prefix_name,
                lib_map=lib_map,
                pbar=pbar,
            )
        elif output_map == OutputMap.EXCEL:
            self.map_to_file: ABCMapToFile = ImplementMapCircuit(
                col_split_maps=col_split_maps,
                col_lat=col_lat,
                col_lon=col_lon,
                cols_name_point=cols_name_point,
                col_filenames=col_filenames,
                prefix_name=prefix_name,
                lib_map=lib_map,
                pbar=pbar,
            )
        else:
            raise NotImplementedError()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.map_to_file.set_pbar(pbar)

    def to_files(
                self,
                df: pd.DataFrame, *,
                output_dir: Directory,
                replace: bool = False,
            ):
        try:
            df[self.lat_col] = df[self.lat_col].str.replace(",", ".").astype(float)
            df[self.lon_col] = df[self.lon_col].str.replace(",", ".").astype(float)
        except Exception as err:
            print(err)
            return
        print('----------------------')
        self.map_to_file.to_files(df, output_dir=output_dir, replace=replace)
