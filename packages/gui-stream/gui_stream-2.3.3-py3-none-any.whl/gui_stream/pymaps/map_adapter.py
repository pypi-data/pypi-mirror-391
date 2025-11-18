# /usr/bin/env python3
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd
from soup_files import File, Directory
from gmplot import gmplot
try:
    import folium
except ImportError as e:
    print(e)


class LibMap(Enum):

    FOLIUM = 'folium'
    GMPLOT = 'gmplot'
    NOT_IMPLEMENTED = 'not implemented'

# ==============================
# Adapter Interface
# ==============================


class MapAdapter(ABC):
    def __init__(self, lat_col: str, lon_col: str, name_point_cols: list[str] = []):
        """
        :param lat_col: nome da coluna de latitude
        :param lon_col: nome da coluna de longitude
        :param name_point_cols: colunas para incluir títulos de cada marcador (opcional)
        """
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.name_point_cols: list[str] = name_point_cols
        self.current_lib: LibMap = LibMap.NOT_IMPLEMENTED

    @abstractmethod
    def export_html(self, df: pd.DataFrame, *, output_file: File):
        """
                :param output_file: nome do arquivo/mapa html a ser gerado.
                :param df: DataFrame com as coordenadas
        """
        pass


# ==============================
# Folium Adapter
# ==============================
class ImplementMapFolium(MapAdapter):

    def __init__(self, lat_col: str, lon_col: str, name_point_cols: list[str] = []):
        super().__init__(lat_col, lon_col, name_point_cols)
        self.current_lib: LibMap = LibMap.FOLIUM

    def export_html(self, df: pd.DataFrame, *, output_file: File):
        first: pd.Series[float] = df.iloc[0]
        folium_map = folium.Map(
            location=[first[self.lat_col], first[self.lon_col]],
            zoom_start=12
        )

        if len(self.name_point_cols) > 0:
            for _, row in df.iterrows():
                name_point = ''
                for col in self.name_point_cols:
                    name_point = f'{name_point} {row[col]}'

                popup = name_point
                folium.Marker(
                    location=[row[self.lat_col], row[self.lon_col]],
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(folium_map)
        else:
            for _, row in df.iterrows():
                popup = f"{row[self.lat_col]}, {row[self.lon_col]}"
                folium.Marker(
                    location=[row[self.lat_col], row[self.lon_col]],
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(folium_map)
        folium_map.save(output_file.absolute())


# ==============================
# gmplot Adapter
# ==============================


class ImplementMapGmplot(MapAdapter):

    def __init__(self, lat_col: str, lon_col: str, name_point_cols: list[str] = str):
        super().__init__(lat_col, lon_col, name_point_cols)

    def export_html(self, df: pd.DataFrame, *, output_file: File):
        lats: list[float] = df[self.lat_col].values.tolist()
        lons: list[float] = df[self.lon_col].values.tolist()
        gmap = gmplot.GoogleMapPlotter(lats[0], lons[0], 12)

        if len(self.name_point_cols) > 0:
            for _, row in df.iterrows():
                name_point = ''
                for col in self.name_point_cols:
                    name_point = f'{name_point} {row[col]}'

                gmap.marker(
                    row[self.lat_col],
                    row[self.lon_col],
                    title=name_point
                )
        else:
            for _, row in df.iterrows():
                gmap.marker(
                    row[self.lat_col],
                    row[self.lon_col],
                    title=None,
                )
        gmap.draw(output_file.absolute())


class MapConvert(object):

    def __init__(
                self, *,
                lat_col='vlr_coordenada_latitude',
                lon_col='vlr_coordenada_longitude',
                name_col: str = None,
                lib_map: LibMap = LibMap.GMPLOT,
            ):
        self.lat_col = lat_col
        self.lon_col = lon_col
        if lib_map == LibMap.FOLIUM:
            self.map_adapter: MapAdapter = ImplementMapFolium(
                lat_col, lon_col, name_col
            )
        elif lib_map == LibMap.GMPLOT:
            self.map_adapter: MapAdapter = ImplementMapGmplot(
                lat_col, lon_col, name_col
            )
        else:
            raise ValueError()

    @property
    def lib_map(self) -> LibMap:
        return self.map_adapter.current_lib

    def export_html(self, df, *, output_file: File):
        if df.empty:
            print(f'DataFrame vazio: {df}')
            return
        self.map_adapter.export_html(df, output_file=output_file)



