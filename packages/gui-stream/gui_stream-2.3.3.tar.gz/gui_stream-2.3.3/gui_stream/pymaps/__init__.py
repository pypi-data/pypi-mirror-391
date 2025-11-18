#!/usr/bin/env python3
import shutil
from soup_files import Directory, ProgressBarAdapter, CreatePbar
from gui_stream.pymaps._read_sheets import read_file
from gui_stream.pymaps.map_adapter import MapConvert, LibMap
from gui_stream.pymaps.create_maps import (
    DataToFileMap, OutputMap, concat_columns, get_circuit_columns
)


def create_maps_html(
            df, *,
            col_split_maps: str = 'numliv',
            col_lat: str = 'vlr_coordenada_latitude',
            col_lon: str = 'vlr_coordenada_longitude',
            cols_name_point: list[str] = ['numcdc', 'concatenar'],
            col_filenames: str = None,
            prefix_name: str = None,
            lib_map: LibMap = LibMap.GMPLOT,
            output_dir: Directory,
            replace=True,
            pbar: ProgressBarAdapter = CreatePbar().get(),
        ):
    #
    df = df[get_circuit_columns()]
    df = concat_columns(df)
    mp_to_html = DataToFileMap(
            col_split_maps=col_split_maps,
            col_lat=col_lat,
            col_lon=col_lon,
            cols_name_point=cols_name_point,
            col_filenames=col_filenames,
            prefix_name=prefix_name,
            lib_map=lib_map,
            pbar=pbar,
            output_map=OutputMap.HTML,
        )
    mp_to_html.to_files(df, output_dir=output_dir, replace=replace)


def create_maps_excel(
            df, *,
            col_split_maps: str = 'numliv',
            col_lat: str = 'vlr_coordenada_latitude',
            col_lon: str = 'vlr_coordenada_longitude',
            cols_name_point: list[str] = ['numcdc', 'concatenar'],
            col_filenames: str = None,
            prefix_name: str = None,
            lib_map: LibMap = LibMap.GMPLOT,
            output_dir: Directory,
            replace=True,
            pbar: ProgressBarAdapter = CreatePbar().get(),
        ):
    #
    df = df[get_circuit_columns()]
    df = concat_columns(df)
    mp_to_xlsx = DataToFileMap(
        col_split_maps=col_split_maps,
        col_lat=col_lat,
        col_lon=col_lon,
        cols_name_point=cols_name_point,
        col_filenames=col_filenames,
        prefix_name=prefix_name,
        lib_map=lib_map,
        pbar=pbar,
        output_map=OutputMap.EXCEL,
    )
    mp_to_xlsx.to_files(df, output_dir=output_dir, replace=replace)


def split_files_in_dir(d: Directory, max_files: int = 100):
    """
    Divide os arquivos de um diretório em subpastas numeradas (01, 02, 03...),
    cada uma contendo no máximo `max_files` arquivos.
    """
    files = d.content_files(recursive=False)  # só os arquivos da pasta raiz
    if not files:
        return
    max_num = len(files)
    for i in range(0, max_num, max_files):
        batch = files[i:i + max_files]
        subdir_name = f"{(i // max_files) + 1:02d}"
        subdir = d.concat(subdir_name, create=True)

        for f in batch:
            src = f.absolute()
            dst = subdir.join_file(f.basename()).absolute()
            shutil.move(src, dst)
