import os

# Linux --
DATA = "/mnt/sdb/KAGGLE_DATA/amex-default-prediction"
PICKLE = "_pickle"

train_data_pickle = os.path.join(DATA, PICKLE, "train_data.pkl")
test_data_pickle = os.path.join(DATA, PICKLE, "test_data.pkl")