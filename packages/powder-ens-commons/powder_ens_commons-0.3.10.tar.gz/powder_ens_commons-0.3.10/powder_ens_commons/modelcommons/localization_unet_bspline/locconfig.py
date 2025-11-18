import torch
from typing import Union

class LocConfig():
    #"dataset","data_split","batch_size","random_state","include_elevation_map": passing only these 5 parameters from training file
    def __init__(self,
            # Model and dataset
            dataset: Union[int, str] = 6, # one of 1,2,3,4,5,6, or strings listed below
            #in our case 6
            data_split: str = 'random', #one of 'random', 'gridK' (where K is integer), 'radiusK'. If dataset==6, 'driving', 'april','july','nov'
            #in our case 'random'
            arch: str = 'unet', # String to select model, see localization.py:DLLocalization:build_model()
            #we didn't pass anything so by default 'unet' in our case
            min_inputs = None, # String
            #Minimum number of inputs required for dataset
            meter_scale = None,
            #Number of meters per pixel 
            random_state: int = 0,
            #random state has been passed. in our case its 0
            one_tx: bool = True,
            #if only one transmitter or more than that
            use_triangulation: bool = False,
            #learn weight and bias for each device
            device_multiplication: bool = False,
            #learn weight and bias for each device
            category_multiplication: bool = True,
            #learn weight and bias only for each sensor category
            remove_mobile: bool = False,
            #remove mobile inputs (if they exists)
            use_alt_for_ds8_grid2: bool = True,
            #more interesting separation for dataset 8 than was chosen by default
            # Training
            test_size: float = 0.2,
            #percentage of data in test set
            tx_marker_value: float = 0.01,
            #value of nonzero pixels adjacent to the tx location
            batch_size: int = 32,
            #number of samples in training. we passed 64 in our training case
            better_epoch_limit: int = 50,
            #without improving  still continue traning till
            lr: float = 5e-4,
            #learning rate
            device = None,
            #device to train on
            model_dir = None,
            #device to train on
            make_val = True,
            #whether to create a validation set
            # Data Augmentations
            apply_sensor_dropout: bool = False,
            #randomly remove sensors input during training
            min_dropout_inputs: int = None,
            #gurantee at least this many input exists after dropout
            apply_rss_noise: bool = False, # Scale RSS randomly
            #randomly apply some noise to rss input
            power_limit: float = 0.3,
            #maximum noise to add on rss input
            apply_power_scaling: bool = False, # Scale RSS uniformly
            #Add a random constant to all RSS inputs, simulating Tx power adjustment
            scale_limit: float = 0.3,
            #the maximum constant to add to the rss inputs
            introduce_new_randomization = False,
            adv_train: bool = False,
            #no adv_training
            testing_white_box: bool = False,
            #if testing white box attack
            include_elevation_map: bool = False,
            #whether to include elevation map. We passed as true
            should_augment = False,
            #should include data augmentation
            augmentation = None,
            #which method of augmentation to apply
            synthetic_only = False,
            #should include data augmentation
            augment_two_tx_only = False,
            #should include data augmentation
            tirem_augment_two_tx = False,
            #using tirem to augment two transmitter
            only_print_propagation_estimation = False,
            #using tirem to augment two transmitter
            tirem_two_tx_only_synthetic_on_train = False,
            #specific augmentation in train set
            tirem_two_tx_specific_augmentation = False,
            original_ratio = 1,
            train_two_tx_tirem_with_ood_samples = False,
            amount_aug_samples = 1500,
            training_now = False,
            testing_now = False,

    ):
        dataset_strings = {'utah44':1, 'outdoor44':2, 'hallways2tx':3, 'outdoor2tx':4, 'orbit5tx':5, 'utah_frs':6, 'antwerp_lora':7, 'utah_cbrs':8}
        dataset_options = [1,2,3,4,5,6,7,8, 'utah44', 'outdoor44', 'hallways2tx', 'outdoor2tx', 'orbit5tx', 'utah_frs', 'antwerp_lora', 'utah_cbrs']
        assert dataset in dataset_options
        #dataset has to be one from dataset_options
        if isinstance(dataset, str):
            dataset = dataset_strings[dataset]
            #if string, replace with corresponding integers 
        self.dataset_index = dataset
        #keeping the index on dataset_index value
        self.set_default_options(min_inputs, meter_scale, min_dropout_inputs)
        #set these three variables by default
        #for dataset 6 it is 5,15,25
        #meaning at least 5 input per sample
        #after dropout, at least keep 15 inputs
        #25 meters per pixel
        self.data_split = data_split
        #in our case it is 'random'
        self.introduce_new_randomization = introduce_new_randomization
        self.arch = arch
        #the default one 'unet'
        self.random_state = random_state
        #in our case 0
        self.one_tx = one_tx 
        #in our case True

        self.model_dir = model_dir

        self.use_triangulation = use_triangulation
        self.device_multiplication = device_multiplication
        #in our case False
        self.category_multiplication = category_multiplication
        #in our case True
        self.remove_mobile = remove_mobile
        #False
        self.use_alt_for_ds8_grid2 = use_alt_for_ds8_grid2
        #True but doesn't matter

        self.test_size = test_size #0.2
        self.training_size = 1 - test_size #0.8
        self.tx_marker_value = tx_marker_value #0.01
        self.batch_size = batch_size #64
        self.better_epoch_limit = better_epoch_limit #at least 50 epochs
        self.lr = lr #default learning rate
        if device is None:
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
            #assigning gpu use
        else:
            self.device = device
        self.make_val = make_val
        #True to compel you to make validation set

        self.sensor_dropout = apply_sensor_dropout
        #false
        self.apply_rss_noise = apply_rss_noise
        self.power_limit = power_limit
        self.apply_power_scaling = apply_power_scaling
        self.scale_limit = scale_limit
        self.adv_train = adv_train #false
        self.testing_white_box = testing_white_box
        self.include_elevation_map = include_elevation_map #true
        self.should_augment = should_augment #false
        self.augmentation = augmentation #None
        self.synthetic_only = synthetic_only
        self.augment_two_tx_only = augment_two_tx_only
        self.tirem_augment_two_tx = tirem_augment_two_tx
        self.tirem_two_tx_only_synthetic_on_train = tirem_two_tx_only_synthetic_on_train
        self.tirem_two_tx_specific_augmentation  = tirem_two_tx_specific_augmentation 
        self.original_ratio = original_ratio
        self.amount_aug_samples = amount_aug_samples
        self.partial_train = 0 #why partial train is 0?
        self.only_print_propagation_estimation = only_print_propagation_estimation
        self.train_two_tx_tirem_with_ood_samples = train_two_tx_tirem_with_ood_samples
        self.training_now = training_now
        self.testing_now = testing_now
        self.printable_keys = {
            'dataset_index': 'DS',
            'random_state': 'randstate',
            'test_size': 'test_size',
            'arch': 'arch',
            'data_split': 'split',
            'meter_scale': 'img_scale',
            'include_elevation_map': 'elev',
            'adv_train': 'AdvTr',
            'augmentation': 'Aug'
        }
        #this keys is actually assigning acronyms for each of the arguments

    def __str__(self):
        #if the function is called with args. Return the string for print() function
        if self.apply_rss_noise:
            self.printable_keys['power_limit'] = 'rand_pow'
        if self.apply_power_scaling:
            self.printable_keys['scale_limit'] = 'scale_pow'
        if self.device_multiplication:
            self.printable_keys['device_multiplication'] = 'DevMult'
        if self.category_multiplication:
            self.printable_keys['category_multiplication'] = 'CatMult'
        if self.sensor_dropout:
            self.printable_keys['min_dropout_inputs'] = 'dropout'
        if self.partial_train > 0:
            self.printable_keys['partial_train'] = 'partialTrain'
        #if these parameters are true, add a member to printable keys with respective acronym
        members = [member for member in dir(self) if not member.startswith('__')]
        #for each member of the object, take the list
        param_string = ''
        #empty parameter string
        for member in members:
            attr = getattr(self, member)
            #get the attribute value for this member
            if member in self.printable_keys and self.printable_keys[member] is not None:
                #if the member in keys list and the value is not None
                param_string += '%s:%s__' % (self.printable_keys[member], attr )
                #in string, write acronym:value
        param_string = param_string[:-2]#remove __ for the last entry
        return param_string #return the string to print
        #also the returned object stores the attribute value

    def set_default_options(self, min_inputs: int, meter_scale: int, min_dropout_inputs: int):
        ds = self.dataset_index
        if ds in [1,2,3,4,5]:
            self.min_sensors = 4 if min_inputs is None else min_inputs
            self.min_dropout_inputs = 4 if min_dropout_inputs is None else min_dropout_inputs
            self.meter_scale = 1 if meter_scale is None else meter_scale
        elif ds == 6:
            self.min_sensors = 5 if min_inputs is None else min_inputs
            self.min_dropout_inputs = 15 if min_dropout_inputs is None else min_dropout_inputs
            self.meter_scale = 25 if meter_scale is None else meter_scale
        elif ds == 7:
            self.min_sensors = 5 if min_inputs is None else min_inputs
            self.min_dropout_inputs = 5 if min_dropout_inputs is None else min_dropout_inputs
            self.meter_scale = 100 if meter_scale is None else meter_scale
        elif ds == 8:
            self.min_sensors = 5 if min_inputs is None else min_inputs
            self.min_dropout_inputs = 4 if min_dropout_inputs is None else min_dropout_inputs
            self.meter_scale = 25 if meter_scale is None else meter_scale