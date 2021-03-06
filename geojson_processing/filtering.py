#!/usr/bin/env python
__author__ = "solivr"
__license__ = "GPL"

from typing import List, Dict, Union
from shapely.geometry import shape
import shapely
import geojson
import json
import os
import re
import pandas as pd
import geopandas as gpd
import numpy as np


def get_valid_shapes(features: List[Dict], verbose: bool=False) -> List[Dict]:
    """
     Remove invalid shapes from a list of GeometryFeatures.

    :param features: list of geojson Feature type objects (shapely.geometry.shape)
    :param verbose: if True will print the invalid Features
    :return: the filtered ``features`` vector
    """

    valid_features = list()
    invalid_count = 0
    for feature in features:
        try:
            shapely_object = shape(feature['geometry'])
            if shapely_object.is_valid:
                valid_features.append(feature)
            else:
                invalid_count += 1
                if verbose:
                    print('- Shape is not valid. (counter invalid: {})'.format(invalid_count))
                    print(feature)
        except ValueError:
            invalid_count += 1
            if verbose:
                print(' - Geojson shape is not readable. (counter invalid: {})'.format(invalid_count))
                print(feature)

    print('   Found {} invalid shapes.'.format(invalid_count))

    return valid_features


def clean_and_export(filename_original: str, export_dir: str) -> None:
    """
    Remove invalid shapes from geojsonfile and exports a nes geojson file

    :param filename_original: filename of the original geojson file
    :param export_dir: directory to export the cleaned geojson files
    :return:
    """

    # Load the geojson file content
    with open(filename_original, 'r') as f:
        geojson_content = geojson.load(f)

    # Filter out invalid shapes
    geojson_content['features'] = get_valid_shapes(geojson_content['features'])

    # Export cleaned content
    basename = os.path.basename(filename_original)
    clean_geojson_filename = os.path.join(export_dir, basename)

    with open(clean_geojson_filename, 'w') as f:
        json.dump(geojson_content, f)


def batch_clean_and_export(list_filenames: List[str], export_dir: str):
    """

    :param list_filenames: list of filename of the original geojson files
    :param export_dir: directory to export the cleaned geojson files
    :return:
    """

    if os.path.isdir(export_dir):
        print('Export directory already exists')
    else:
        os.makedirs(export_dir)

    for filename in list_filenames:
        print('Processing {}'.format(filename))
        clean_and_export(filename, export_dir)


def filter_by_area(geodataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
                   min_area: float=0,
                   max_area: float=np.inf) -> gpd.GeoDataFrame:

    geodataframe['area'] = geodataframe.geometry.apply(lambda s: s.area)

    # remove small area regions
    geodataframe = geodataframe[geodataframe.area > min_area]
    # remove big area
    geodataframe = geodataframe[geodataframe.area < max_area]

    return geodataframe


def remove_empty_transcripts(geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    # remove transcription and score columns
    geodataframe.drop(['transcription', 'score'], axis=1, inplace=True)

    # Keep only the rows that have a transcription
    gdf_with_numbers = geodataframe[geodataframe.best_transcription != '']

    return gdf_with_numbers


def _float2int(unit):
    if isinstance(unit, float) and not pd.isnull(unit):
        return int(unit)
    else:
        return unit


def clean_manually_annotated_parcels(geodataframe_annotated: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    labels_to_keep = ['WKT', 'best_trans', 'uuid', 'ID']

    geodataframe_annotated = geodataframe_annotated[labels_to_keep]

    # Create a geometry from the WKT
    geodataframe_annotated['geometry'] = geodataframe_annotated.WKT.apply(lambda s: shapely.wkt.loads(s)[0])
    geodataframe_annotated = geodataframe_annotated.drop(['WKT'], axis=1)

    # Change float into int
    geodataframe_annotated.ID = geodataframe_annotated.ID.apply(lambda t: _float2int(t))

    # Remove non digits chars and convert transcription to float type
    geodataframe_annotated.ID = geodataframe_annotated.ID.apply(lambda t: re.sub(r"\D", "", str(t)))
    geodataframe_annotated.ID.replace('', np.nan, inplace=True)
    # geodataframe_annotated.ID = geodataframe_annotated.ID.apply(lambda t: float(t) if t != "" else np.nan)

    # Find invalid shapes in groundtruth and remove them also
    invalid_polygons = geodataframe_annotated[~geodataframe_annotated.geometry.apply(lambda s: s.is_valid)]
    print("Removed {} invalid polygons.".format(len(invalid_polygons)))

    gdf_corrected = geodataframe_annotated.drop(index=invalid_polygons.index, axis=0)

    return gdf_corrected
