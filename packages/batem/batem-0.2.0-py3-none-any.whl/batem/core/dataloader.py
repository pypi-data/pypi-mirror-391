"""Data loading and download module for building energy analysis datasets.

.. module:: batem.core.dataloader

This module provides utilities for downloading and managing datasets from external
repositories, specifically designed for building energy analysis applications.
It supports downloading data from Zenodo repositories and organizing files
according to project configuration.

Functions
---------

.. autosummary::
   :toctree: generated/

   load_data

Key Features
------------

* Zenodo API integration for dataset discovery and download
* Automatic directory creation based on project configuration
* File existence checking to avoid redundant downloads
* Progress reporting during download operations
* Support for multiple file downloads from single records
* Integration with project configuration system (setup.ini)
* Error handling for network and API failures

The module is designed for building energy analysis, research data management,
and automated dataset acquisition for building energy modeling and simulation.

:Author: stephane.ploix@grenoble-inp.fr
:License: GNU General Public License v3.0
"""
import os
import requests
from .library import Setup


def load_data(zenodo_record_id: str, folder: str = 'data') -> None:
    """Download datasets from a Zenodo record to the specified folder.

    This function downloads all files from a Zenodo record (identified by record ID)
    to a local directory. It automatically creates the target directory if it doesn't
    exist and skips files that are already present locally.

    :param zenodo_record_id: The Zenodo record ID to download from
    :type zenodo_record_id: str
    :param folder: The folder name in the project configuration to download to, defaults to 'data'
    :type folder: str, optional
    :raises Exception: If the Zenodo API request fails or returns an error status
    :raises KeyError: If the specified folder is not found in the project configuration
    """
    output_dir_path = Setup.folder_path(folder)
    output_dir = str(output_dir_path)

    # Use the proper Zenodo API endpoint
    api_url = f"https://zenodo.org/api/records/{zenodo_record_id}"
    response: requests.Response = requests.get(api_url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch record: {response.status_code} - {response.text}")

    record = response.json()
    print(f"Found record: {record['metadata']['title']}")

    for file in record['files']:
        file_name = file['key']
        file_url = file['links']['self']
        file_path = os.path.join(output_dir, file_name)

        if os.path.isfile(file_path):
            print(f"File {file_name} already exists in folder: {output_dir}")
        else:
            print(f"Downloading {file_name}...")
            file_data = requests.get(file_url).content
            with open(os.path.join(output_dir, file_name), 'wb') as f:
                f.write(file_data)

    print(f"All files downloaded in folder: {output_dir}")
