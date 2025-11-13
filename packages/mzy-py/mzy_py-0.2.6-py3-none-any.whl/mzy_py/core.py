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

def QRcodegen_txt(text: str, save_path: str = None) -> None:
    """
    把字符串生成二维码图片；
    默认保存在**用户执行入口脚本**所在目录。
    """
    import qrcode
    import sys
    import os
    if save_path is None:
        # 真正跟随“用户执行入口”目录
        try:
            caller_file = sys.modules['__main__'].__file__   # 入口脚本路径
        except (KeyError, AttributeError):
            # 交互式 / notebook 没有 __main__.__file__
            caller_file = os.getcwd()
        save_path = os.path.join(os.path.dirname(os.path.abspath(caller_file)), "qr.png")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(save_path)

def compress_img(tar_src: str, res_dst: str, quality: int = 75) -> None:
    """JPEG 压缩到指定质量。"""
    import PIL.Image
    img = PIL.Image.open(tar_src)
    img.save(res_dst, "JPEG", quality=quality)
