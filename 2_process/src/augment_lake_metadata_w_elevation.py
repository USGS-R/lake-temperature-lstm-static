import os
import requests
import urllib
import pandas as pd


def elevation_query(lat, lon):
    """
    Query service using lat, lon and return the corresponding elevation values.
    Thanks to https://gis.stackexchange.com/questions/338392/getting-elevation-for-multiple-lat-long-coordinates-in-python

    :param lat: latitude values in decimal degrees
    :param lon: longitude values
    :returns: elevation at the specified coordinates

    """
    # USGS Elevation Point Query Service
    url = r'https://nationalmap.gov/epqs/pqs.php?'
    # define rest query params
    params = {
        'output': 'json',
        'x': lon,
        'y': lat,
        'units': 'Meters'
    }

    # format query string and return query value
    result = requests.get((url + urllib.parse.urlencode(params)))
    elevation = result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']

    return elevation


def add_elevation_from_EPQS(in_file, out_file):
    """
    Add "elevation" column to metadata file and save to new file.
    Use the USGS Elevation Point Query Service.
    
    Currently unused.

    :param in_file: Filename of csv to read existing lake metadata from
    :param out_file: Filename of csv to save metadata augmented with elevation
        to

    """
    lake_metadata = pd.read_csv(in_file)
    # Add elevation to metadata
    lake_metadata['elevation'] = lake_metadata.apply(
        lambda row: elevation_query(
            row['centroid_lat'], row['centroid_lon']),
        axis=1)
    destination_dir = os.path.dirname(out_file)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    lake_metadata.to_csv(out_file)


def add_elevation_from_file(in_file, elevation_file, out_file, lat_col, lon_col, elevation_col):
    """
    Add "elevation" column to metadata file and save to new file. Use the
    Elevation Point Query Service (EPQS) to fill in missing elevation values.

    :param in_file: Filename of csv to read existing lake metadata from
    :param elevation_file: Filename of csv file to read elevation data from
    :param out_file: Filename of csv to save metadata augmented with elevation
        to
    :param lat_col: Name of column with latitudes in in_file
    :param lon_col: Name of column with longitudes in in_file
    :param elevation_col: Name of column with elevations in elevation file

    """
    lake_metadata = pd.read_csv(in_file)
    lake_elevations = pd.read_csv(elevation_file)
    lake_elevations_only = lake_elevations.loc[:, ['site_id', elevation_col]]
    # Add elevation to metadata
    augmented = pd.merge(lake_metadata, lake_elevations_only, how="left", on='site_id')
    # Rename column to elevation
    augmented = augmented.rename({elevation_col: 'elevation'}, axis='columns')

    # If a site is missing from lake_elevations, 'elevation' in the merged
    # dataframe will be NaN in that site's row.
    # If elevation is NaN, use EPQS to fill in the missing elevation
    def fill_nan_from_EPQS(row):
        """
        Fill a NaN value in the 'elevation' column with elevation from the
        USGS Elevation Point Query Service.
        
        If the value of 'elevation' is not NaN, it is returned unchanged.

        :param row: One row of the Dataframe containing lake metadata
        :returns: Elevation value

        """
        if pd.isna(row['elevation']):
            elevation = elevation_query(row[lat_col], row[lon_col])  
        else:
            elevation = row['elevation']
        return elevation
    print(f"Querying EPQS to fill in {pd.isna(augmented.elevation).sum()} missing elevations")
    augmented['elevation'] = augmented.apply(fill_nan_from_EPQS, axis=1)
    destination_dir = os.path.dirname(out_file)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    augmented.to_csv(out_file)


if __name__ == '__main__':
    # Use surface metadata for elevations instead of USGS EPQS
    add_elevation_from_file(
        snakemake.input.lake_metadata,
        snakemake.input.elevation_metadata,
        snakemake.output.augmented_metadata,
        snakemake.params.latitude_column_name,
        snakemake.params.longitude_column_name,
        snakemake.params.elevation_column_name
    )
