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

def QRcodegen_txt(text: str, save_path: str = "qr.png") -> None:
    """把字符串生成二维码图片。"""
    import qrcode
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

def compress_img(src: str, dst: str, quality: int = 75) -> None:
    """JPEG 压缩到指定质量。"""
    import PIL.Image
    img = PIL.Image.open(src)
    img.save(dst, "JPEG", quality=quality)