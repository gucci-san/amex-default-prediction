import pandas as pd
import numpy as np
import os,random
import datetime
from contextlib import contextmanager
from tqdm import tqdm

from sklearn.metrics import roc_auc_score,mean_squared_error,average_precision_score,log_loss
from sklearn.model_selection import KFold, StratifiedKFold,GroupKFold

import lightgbm as lgb
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset,TensorDataset, DataLoader,RandomSampler

import torch.cuda.amp as amp

from scheduler import *

import argparse

class TaskDataset:
    def __init__(self, df_series, df_feature, uidx, df_y=None):
        self.df_series = df_series
        self.df_feature = df_feature
        self.df_y = df_y
        self.uidxs = uidxs
    
    def __len__(self):
        return (len(self.uidxs))

    def __getitem__(self, index):
        i1, i2, idx = self.uidxs[index]
        series = self.df_series.iloc[i1:i2+1, 1:].values

        if len(series.shape) == 1:
            series = series.reshape((-1,)+series.shape[-1:])
            series_ = series.copy()
            series_[series_!=0] = 1.0 - series_[series_!=0] + 0.001
            
            feature = self.df_feature.loc[idx].values[1:]
            feature_ = feature.copy()

            if self.df_y is not None:
                label = self.df_y.loc[idx, [label_name]].values
            
                return {
                    "SERIES": series,
                    "FEATURE": np.concatenate([feature, feature_]),
                    "LABEL": label,
                }
            else:
                return{
                    "SERIES": series,
                    "FEATURE": np.concatenate([feature, feature_])
                }

    def collate_fn(self, batch):
        """
        Padding to same size.
        """
        batch_size = len(batch)
        batch_series = torch.zeros((batch_size, 13, batch[0]["SERIES"].shape[1]))
        batch_mask = torch.zeros((batch_size, 13))
        batch_feature = torch.zeros((batch_size, batch[0]["FEATURE"].shape[0]))
        batch_y = torch.zeros((batch_size, 1))

        for i, item in enumerate(batch):
            v = item["SERIES"]
            batch_series[i, :v.shape[0], :] = torch.tensor(v).float()
            batch_mask[i, :v.shape[0]] = 1.0
            v = item["FEATURE"].astype(np.float32)
            batch_feature[i] = torch.tensor(v).float()
            if self.df_y is not None:
                v = item["LABEL"].astype(np.float32)
                batch_y[i] = torch.tensor(v).float()
        
        return {
            "batch_series": batch_series,
            "batch_mask": batch_mask,
            "batch_feature": batch_feature,
            "batch_y": batch_y
            }


def NN_train_and_predict(train, test, model_class, config, use_series_oof, logit=False, output_root="./output/", run_id=None):
    # 実験管理 --
    if not run_id:
        run_id = "run_nn_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        while os.path.exists(output_root+run_id+"/"):
            time.sleep(1)
            run_id = "run_nn_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_root + f"{args.save_dir}/"
    else:
        output_path = output_root + run_id + "/"

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    os.system(f"cp ./*.py {output_path}")

    # configをローカル化 --
    feature_name = config["feature_name"]
    obj_max = config["obj_max"]
    epochs = config["epochs"]
    smoothing = config["smoothing"]
    patience = config["patience"]
    lr = config["lr"]
    batch_size = config["batch_size"]
    folds = config["folds"]
    seed = config["seed"] 

    if train is not None:
        train_series, train_feature, train_y, train_series_idx = train
        # train_series : nn_series.feather
        # train_feature: nn_all_feature.feather
        # train_y : train_labels.csv
        # train_series_idx : df.groupby("customer_ID")["idx"].agg(min, max), なんだこれ？
        oof = train_y[[id_name]]
        oof["fold"] = -1
        oof[label_name] = 0.0
        oof[label_name] = oof[label_name].astype(np.float32)
    else:
        oof = None

    # 学習のメインセクション --
    if train is not None:
        log = open(output_path + "train.log", "w", buffering=1)
        log.write(str(config)+"\n")

        all_valid_metric = []

        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)

        model_num = 0
        train_folds = []

        for fold, (trn_index, val_index) in enumerate(skf.split(train_y, train_y[label_name])):
            train_dataset = TaskDataset(
                train_series, 
                train_feature, 
                [train_series_idx[i] for i in trn_index], 
                train_y
                )
            train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True, collate_fn=train_dataset.collate_fn, num_workers=args.num_workers)
