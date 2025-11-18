#!/usr/bin/env python3

from soup_files import File, ProgressBarAdapter, CreatePbar
import pandas as pd


def _rd_csv(f: File, sep: str = '\t') -> pd.DataFrame:
    try:
        return pd.read_csv(f.absolute(), sep=sep)
    except:
        try:
            return pd.read_csv(f.absolute(), encoding="ISO-8859-1", sep=sep)
        except:
            return pd.DataFrame()


def _rd_excel(f: File) -> pd.DataFrame:
    return pd.read_excel(f.absolute())


def _rd_ods(f: File) -> pd.DataFrame:
    return pd.read_excel(f.absolute(), engine='odf')


def read_file(f: File, *, pbar: ProgressBarAdapter = CreatePbar().get()) -> pd.DataFrame:
    pbar.start()
    pbar.update(0, f'Lendo: {f.basename()}')
    df = pd.DataFrame()
    if f.is_csv():
        df = _rd_csv(f)
    elif f.is_excel():
        df = _rd_excel(f)
    elif f.is_ods():
        df = _rd_ods(f)
    print()
    pbar.update(100, 'OK')
    pbar.stop()
    return df
