import os

# Linux --
DATA = "/mnt/sdb/KAGGLE_DATA/amex-default-prediction"
PICKLE = "_pickle"
PARQUET = "_parquet"

train_data_csv = os.path.join(DATA, "train_data.csv")
test_data_csv = os.path.join(DATA, "test_data.csv")
train_data_pickle = os.path.join(DATA, PICKLE, "train_data.pkl")
test_data_pickle = os.path.join(DATA, PICKLE, "test_data.pkl")
train_data_parquet = os.path.join(DATA, PARQUET, "train.parquet")
test_data_parquet = os.path.join(DATA, PARQUET, "test.parquet")