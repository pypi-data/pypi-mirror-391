import json
import random
from typing import Dict, Tuple

def split_train_test_json(json_data, test_size=0.2, seed=42):
    random.seed(seed)

    one_tx_keys = []
    two_tx_keys = []

    for k, v in json_data.items():
        tx = v.get("tx_coords")
        if tx is None:
            continue  # ✅ skip entries with missing tx_coords
        if len(tx) == 1:
            one_tx_keys.append(k)
        elif len(tx) == 2:
            two_tx_keys.append(k)

    def split_keys(keys):
        n_test = int(len(keys) * test_size)
        shuffled = keys.copy()
        random.shuffle(shuffled)
        return shuffled[n_test:], shuffled[:n_test]

    one_tx_train, one_tx_test = split_keys(one_tx_keys)
    two_tx_train, two_tx_test = split_keys(two_tx_keys)

    train_keys = one_tx_train + two_tx_train
    test_keys = one_tx_test + two_tx_test

    train_data = {k: json_data[k] for k in train_keys}
    test_data = {k: json_data[k] for k in test_keys}

    return train_data, test_data

