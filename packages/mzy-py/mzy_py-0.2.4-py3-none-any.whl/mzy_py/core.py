from typing import List
import pandas as pd
import numpy as np


def du_csv(filepath:str):
    df = pd.read_csv(filepath)
    return df
#def print_my_name() -> str:
#    return "My name is Mzy, I am a student in BPU."
def du_excel(filepath:str):
    df = pd.read_excel(filepath)
    return df

def dayin(a:str):
    print(a)

def lianjie(a:str,b:str):
    df = pd.concat([a,b],axis=1)
    return df

def plus_mzy(a, b):
    """两个数相加"""
    return a + b

def minus_mzy(a, b):
    """两个数相减"""
    return a - b
