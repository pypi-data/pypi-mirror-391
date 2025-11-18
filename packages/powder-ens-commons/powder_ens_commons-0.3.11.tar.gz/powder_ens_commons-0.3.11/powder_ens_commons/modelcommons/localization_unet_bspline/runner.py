import os
import torch
import urllib.request
from .localization_bspline2 import DLLocalization
from .dataset2 import RSSLocDataset
from .locconfig import LocConfig
from .models_bspline2 import SlicedEarthMoversDistance

def ensure_dir_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def download_to_cache_if_needed(remote_url, local_path):
    """
    Download a file from remote_url and save it to local_path if not already present.
    """
    ensure_dir_exists(local_path)
    if not os.path.exists(local_path):
        print(f"[INFO] Downloading model weights from:\n  {remote_url}\n→ to local cache:\n  {local_path}")
        urllib.request.urlretrieve(remote_url, local_path)
    else:
        print(f"[INFO] Cached model already exists at:\n  {local_path}")

def load_model_and_fit_dataset(train_data, receivers_list, bmap = None, dsm = None, one_tx = False, num_epoch = 1000, device='cuda'):
    """
    Load pretrained UNet-bspline model weights from public GitLab URL into cache, then train using the provided dataset.

    Returns:
    - model: trained model
    - train_loss_arr: training loss history
    - test_errors: evaluation results
    """

    should_train = True #making training true
    should_load_model = True #making load model true
    restart_optimizer = False #don't restart optimizer
    if one_tx == True:
        one_tx = True #one transmitter only
    else:
        one_tx = False #one transmitter only
    tirem_augment_two_tx = False
    training_now = True
    # Specify params
    max_num_epochs = 1000 #number of epochs in training process
    # max_num_epochs = 10
    if dsm != None:
        include_elevation_map = True #include elevation map in training
    batch_size = 32 if should_train else 32 #batch size 64
    num_training_repeats = 1 #traning repeat one time
    device = torch.device('cuda') #using gpu
    all_results = {} #dictionary to store all results
    # Step 1: Define parameters
    dict_params = {
        "dataset": 6,
        "data_split": 'random',
        "batch_size": 32,
        "random_state": 0,
        "include_elevation_map": include_elevation_map,
        "one_tx": one_tx,
        "tirem_augment_two_tx": False,
        "training_now": True,
    }
    params = LocConfig(**dict_params)
    loss_func = SlicedEarthMoversDistance(num_projections=100, scaling=0.01, p=1)

    # Step 2: Paths
    remote_model_url = (
        "https://gitlab.flux.utah.edu/mumtahin_habib/powder_ens_datasets/-/raw/main/"
        "models/localization_unet_bspline/"
        "AdvTrFalse__arch_unet__Aug_None__CatMult_True__split_random__DS_6__elev_True__img_scale_25__randstate_0__test_size_0.2_emd__model_train_val.pt"
    )
    cache_dir = "cache/localization_unet_bspline/"
    load_model_path = os.path.join(cache_dir, "pretrained_model.pt")
    save_model_path = os.path.join(cache_dir, "fine_tuned_model.pt")

    # Step 3: Download model weights into cache
    download_to_cache_if_needed(remote_model_url, load_model_path)

    # Step 4: Build dataset
    dataset = RSSLocDataset(
        params,
        train_data=train_data,
        receivers_list=receivers_list,
        dsm_map=dsm,
        building_map=bmap
    )
    dataset.print_dataset_stats()

    # Step 5: Train model
    dlloc = DLLocalization(dataset, loss_object=loss_func)
    model, train_loss_arr, test_errors = dlloc.train_model(
        num_epochs=num_epoch,
        save_model_file=save_model_path,
        load_model=True,
        restart_optimizer=False,
        load_model_file=load_model_path
    )

    return model, train_loss_arr, test_errors
