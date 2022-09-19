import numpy as np
import pandas as pd
from colorama import Fore
y_ = Fore.YELLOW
b_ = Fore.BLUE
g_ = Fore.GREEN
sr_ = Fore.RESET

def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.        
    """
    start_mem = df.memory_usage().sum() / 1024**2
    #print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype
        #print(f"{y_}col:{col}...type:{col_type}{sr_}")

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            #print(f"{b_}    ......c_min:{c_min} // c_max:{c_max}{sr_}")

            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                    #print(f"{g_}        .........converted to np.int8{sr_}")
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                    #print(f"{g_}        .........converted to np.int16{sr_}")
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                    #print(f"{g_}        .........converted to np.int32{sr_}")
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
                    #print(f"{g_}        .........converted to np.int64{sr_}")
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                    #print(f"{g_}        .........converted to np.float16{sr_}")
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                    #print(f"{g_}        .........converted to np.float32{sr_}")
                else:
                    df[col] = df[col].astype(np.float64)
                    #print(f"{g_}        .........converted to np.float64{sr_}")
        else:
            df[col] = df[col].astype('category')
            #print(f"{g_}    ......converted to category")

    end_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df