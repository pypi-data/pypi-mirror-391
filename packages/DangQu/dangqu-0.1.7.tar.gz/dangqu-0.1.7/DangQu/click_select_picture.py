#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/4 17:22
@Author  : dmj-11740
@File    : click_select_picture.py
@Software: PyCharm
@desc    : 
"""
import base64

import cv2
import numpy as np

from typing import Tuple


def convert_to_web_coords(max_loc, sim_shape, bim_shape, web_size):
    """
    将模板匹配得到的坐标转换为 web 端展示图的点击坐标（模板中心点）

    参数:
        max_loc: tuple(int, int) 匹配左上角坐标 (x, y)
        sim_shape: 模板图的 shape（H, W, ...）
        bim_shape: 匹配用大图的 shape（H, W, ...）
        web_size: web 端展示图大小 (W, H)

    返回:
        (web_x, web_y): 模板中心在 web 端的坐标
    """
    # 解包尺寸
    sim_h, sim_w = sim_shape[:2]
    bim_h, bim_w = bim_shape[:2]
    web_w, web_h = web_size

    # 左上角坐标
    x, y = max_loc

    # 模板中心（在匹配图坐标系下）
    center_x = x + sim_w / 2
    center_y = y + sim_h / 2

    # 比例换算
    scale_x = web_w / bim_w
    scale_y = web_h / bim_h

    # 转换到 web 坐标系
    web_x = int(center_x * scale_x)
    web_y = int(center_y * scale_y)

    return (web_x, web_y), (scale_x, scale_y)


def base64_to_cv2(base64_str):
    """
    将 base64 字符串转为 OpenCV 图像 (numpy.ndarray)
    """
    # 去掉可能的 data:image/png;base64, 前缀
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


def get_select_picture(simg_b64: str,
                       bimg_b64: str,
                       web_size: Tuple[int, int] = (290, 179),
                       inside: int = 7,
                       debug=False):
    """

    :param simg_b64: 小图base64
    :param bimg_b64: 大图base64
    :param web_size: 图片在web端上大小
    :param inside: 剪切外边 我感觉7最好，自行调整
    :param debug: 打印结果
    :return:
    """
    bim = base64_to_cv2(bimg_b64)
    sim = base64_to_cv2(simg_b64)

    # 缩放比例，大小图更好适配
    scale = 0.7
    bim = cv2.resize(bim, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    _, bim = cv2.threshold(bim, 127, 255, cv2.THRESH_BINARY)
    _, sim = cv2.threshold(sim, 127, 255, cv2.THRESH_BINARY)

    # 剪切小图, 去除边缘及背景
    w, h = sim.shape[1], sim.shape[0]
    radio3 = w // 3
    sim = sim[inside: h - inside, radio3 + inside: radio3 * 2 - inside]
    w, h = sim.shape[1], sim.shape[0]

    matched = cv2.matchTemplate(bim, sim, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(matched)

    (web_x, web_y), (sx, sy) = convert_to_web_coords(
        max_loc,
        sim.shape,  # 小图 shape
        bim.shape,  # 匹配用大图 shape
        web_size,  # web端图尺寸
    )
    if debug:
        print(f"匹配到左上角: {max_loc}")
        print(f"点击中心点 (web端): ({web_x}, {web_y})")

    return web_x, web_y
