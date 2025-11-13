import os
import json
import requests
from pathlib import Path

# Base URL for raw access to dataset files
BASE_URL = "https://gitlab.flux.utah.edu/mumtahin_habib/powder_ens_datasets/-/raw/main/datasets"

# Local cache directory for downloaded files
LOCAL_CACHE = Path.home() / ".powder_ens_cache"
LOCAL_CACHE.mkdir(exist_ok=True)

def download_file(url: str, local_path: Path):
    if not local_path.exists():
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
    return local_path

def load_dataset(name: str, version: str):
    if name == "frs":
        dataset_dir = f"{BASE_URL}/frs"

        # Download receiver list
        loc_idx_url = f"{dataset_dir}/location_indexes.json"
        loc_idx_path = LOCAL_CACHE / "frs_location_indexes.json"
        download_file(loc_idx_url, loc_idx_path)
        with open(loc_idx_path, "r") as f:
            receivers = json.load(f)

        # Download map files
        buildings_url = f"{dataset_dir}/Maps/corrected_buildings.tif"
        dsm_url = f"{dataset_dir}/Maps/corrected_dsm.tif"

        buildings_path = download_file(buildings_url, LOCAL_CACHE / "frs_buildings.tif")
        dsm_path = download_file(dsm_url, LOCAL_CACHE / "frs_dsm.tif")

        # Handle different versions
        version = version.lower()
        if version in ["full"]:
            file_url = f"{dataset_dir}/Full_Dataset/powder_462.7_rss_data.json"
            file_path = LOCAL_CACHE / f"frs_{version}.json"
            download_file(file_url, file_path)
            with open(file_path, "r") as f:
                data = json.load(f)
            return data, receivers, buildings_path, dsm_path
        elif version in ["no_tx", "single_tx", "two_tx"]:
            file_url = f"{dataset_dir}/Separated_Dataset_JSON/all_data/{version}.json"
            file_path = LOCAL_CACHE / f"frs_{version}.json"
            download_file(file_url, file_path)
            with open(file_path, "r") as f:
                data = json.load(f)
            return data, receivers, buildings_path, dsm_path
        elif version in ["november", "april", "july"]:
            file_url = f"{dataset_dir}/Separated_Dataset_JSON/train_test_splits/seasonal_split/{version}.json"
            file_path = LOCAL_CACHE / f"frs_{version}.json"
            download_file(file_url, file_path)
            with open(file_path, "r") as f:
                data = json.load(f)
            return data, receivers, buildings_path, dsm_path

        elif version in ["random"]:
            train_url = f"{dataset_dir}/Separated_Dataset_JSON/train_test_splits/random_split/{version}_train.json"
            test_url = f"{dataset_dir}/Separated_Dataset_JSON/train_test_splits/random_split/{version}_test.json"
            train_path = LOCAL_CACHE / f"frs_{version}_train.json"
            test_path = LOCAL_CACHE / f"frs_{version}_test.json"

            download_file(train_url, train_path)
            download_file(test_url, test_path)

            with open(train_path, "r") as f:
                train_data = json.load(f)
            with open(test_path, "r") as f:
                test_data = json.load(f)
            return [train_data, test_data], receivers, buildings_path, dsm_path

        elif version in ["grid"]:
            train_url = f"{dataset_dir}/Separated_Dataset_JSON/train_test_splits/grid_split/{version}_train.json"
            test_url = f"{dataset_dir}/Separated_Dataset_JSON/train_test_splits/grid_split/{version}_test.json"
            train_path = LOCAL_CACHE / f"frs_{version}_train.json"
            test_path = LOCAL_CACHE / f"frs_{version}_test.json"

            download_file(train_url, train_path)
            download_file(test_url, test_path)

            with open(train_path, "r") as f:
                train_data = json.load(f)
            with open(test_path, "r") as f:
                test_data = json.load(f)
            return [train_data, test_data], receivers, buildings_path, dsm_path

        else:
            raise ValueError(f"Unsupported version '{version}' for dataset 'frs'.")

    elif name == "cbrs":
        dataset_dir = f"{BASE_URL}/cbrs/slc_cbrs_data"
        # Download receiver list
        loc_idx_url = f"{dataset_dir}/location_indexes.json"
        loc_idx_path = LOCAL_CACHE / "cbrs_location_indexes.json"
        download_file(loc_idx_url, loc_idx_path)
        with open(loc_idx_path, "r") as f:
            receivers = json.load(f)

        # Download map files
        buildings_url = f"{dataset_dir}/Maps/corrected_buildings.tif"
        dsm_url = f"{dataset_dir}/Maps/corrected_dsm.tif"

        buildings_path = download_file(buildings_url, LOCAL_CACHE / "cbrs_buildings.tif")
        dsm_path = download_file(dsm_url, LOCAL_CACHE / "cbrs_dsm.tif")

        file_url = f"{dataset_dir}/slc_prop_measurement/data/data.json"
        file_path = LOCAL_CACHE / f"cbrs_{version}.json"
        download_file(file_url, file_path)
        with open(file_path, "r") as f:
            data = json.load(f)
        return data, receivers, buildings_path, dsm_path


    else:
        raise ValueError(f"Unsupported dataset name: {name}")
