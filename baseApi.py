# -*- coding:UTF-8 -*-
# Created by Shing at 2020/1/17

import base64
from PIL import Image
import tempfile
import os, sys
from hashlib import md5 as lib_md5
import re, logging
import cv2
from numpy import sqrt
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from rect import Rect


def duration_from_mp4(path):
    cmd = """ffprobe '{}' -select_streams v -show_entries stream=duration -of default=nk=1:nw=1 -v quiet""".format(
        path)
    logging.info(cmd)
    with os.popen(cmd) as stdout:
        total_duration = stdout.read()
        total_duration = re.sub('\s+', '', total_duration)
        if not total_duration:
            raise Exception(str(path) + '获取视频时长异常')
    logging.info(str(path) + '视频时长' + str(total_duration))
    return float(total_duration)


def dec_to_hex(dec):
    hex_map = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    for x in range(0, 10):
        hex_map[x] = str(x)

    dec = int(dec)
    result = ''
    while dec >= 16:
        mod = dec % 16
        dec = int(dec / 16)
        result = hex_map[mod] + result
    result = hex_map[dec] + result
    if list(hex_map.values()).__contains__(result):
        result = '0' + result
    return result


def md5(will_md5_str):
    if str is None:
        return ''
    md5_obj = lib_md5()
    md5_obj.update(will_md5_str.encode(encoding='utf-8'))
    return md5_obj.hexdigest()


def read_content(path_or_file):
    if isinstance(path_or_file, str):
        with open(path_or_file, 'rb') as f:
            return f.read()
    else:
        return path_or_file.read()


def base64StrFromImage(path_or_file):
    return base64.b64encode(read_content(path_or_file))


def size_of_image(path_or_file):
    '''return tuple (width,height)'''
    im = Image.open(path_or_file)
    if im is None:
        raise Exception('没有读取到图片width和height')
    return im.size


def ensure_directory(path_to_file):
    directory = '/'.join(path_to_file.split('/')[:-1])
    if directory:
        os.makedirs(directory, exist_ok=True)


def crop_image(image_path, rect_dict):
    if rect_dict is None:
        return None
    im = Image.open(image_path)
    if im is None:
        return None
    im = im.crop((float(rect_dict['left']),
                  float(rect_dict['top']),
                  float(rect_dict['left']) + float(rect_dict['width']),
                  float(rect_dict['top']) + float(rect_dict['height'])))
    return im


def main_colors_from_image_rect(image_path, rect_dict):
    im = crop_image(image_path, rect_dict)
    if im is None:
        return None
    '''先保存到本地，再从本地读取，结果更准确'''
    crop_tmp_dir = os.path.join(tempfile.gettempdir(), 'jnx', 'tmp')
    if not os.path.exists(crop_tmp_dir):
        os.makedirs(crop_tmp_dir)
    crop_image_path = os.path.join(crop_tmp_dir, os.path.split(image_path)[-1])
    colors = []
    try:
        im.save(crop_image_path)
        # os.system('cp {} {}'.format(crop_image_path, '/mnt/c/Users/admin/Downloads'))
        im = Image.open(crop_image_path)
        colors = im.getcolors(88888)
        if colors is None or len(colors) == 0:
            return None
        colors = sorted(colors, key=lambda x: x[0], reverse=True)[:3]
        colors = list(map(lambda x: x[1], colors))
        colors = list(map(lambda x: '#' + dec_to_hex(x[0]) + dec_to_hex(x[1]) + dec_to_hex(x[2]), colors))
    finally:
        if os.path.exists(crop_image_path):
            os.system('rm -f {}'.format(crop_image_path))
    return colors


def rect_is_image_center(rect, image_shape):
    return rect_is_image_hcenter(rect, image_shape) or rect_is_image_vcenter(rect, image_shape)


def rect_is_image_hcenter(rect, image_size):
    image_width = image_size[0]
    rect_left = rect.left
    rect_width = rect.width
    offset = 10
    return rect_left <= 0.5 * image_width + offset and rect_left + rect_width >= 0.5 * image_width - offset


def rect_is_image_vcenter(rect, image_size):
    image_height = image_size[1]
    rect_top = rect.top
    rect_height = rect.height
    offset = 10
    return rect_top <= 0.5 * image_height + offset and rect_top + rect_height >= 0.5 * image_height - offset


class WeightedGridFilter:
    '''
    加权重的网格，可以过滤或计算物体坐标是否在图片中心
    '''

    def __init__(self, weight_matrix):
        self._assert_weight_matrix(weight_matrix)
        self.weight_matrix = weight_matrix

        row_num = len(weight_matrix)
        col_num = len(weight_matrix[0])
        self.grid = [Rect(i / row_num, j / col_num, 1 / col_num, 1 / row_num)
                     for i in range(row_num) for j in range(col_num)
                     ]
        self.weight_array = [weight_matrix[i][j]
                             for i in range(row_num) for j in range(col_num)
                             ]

    def _assert_weight_matrix(self, weight_matrix):
        assert weight_matrix, weight_matrix[0]
        for row in weight_matrix:
            assert len(row) == len(weight_matrix[0])
            for weight in row:
                try:
                    float(weight)
                except ValueError as e:
                    raise AssertionError(e)

    def compute_crossing_score(self, object_rect, half_score=False,
                               crossing_score=1, touching_score=0, enclosing_score=0):
        def grid_crossing():
            for section in self.grid:
                score = 0
                x, y = section.middle_point()
                if section.isOverLay(object_rect):
                    if object_rect.left < x and object_rect.right > x:
                        score += crossing_score / 2
                    if object_rect.top < y and object_rect.bottom > y:
                        score += crossing_score / 2
                    score = max(score, touching_score,
                                enclosing_score * section.contains(object_rect)
                                )
                yield score if half_score else int(score)

        weighted_score = (weight * score
                          for weight, score in zip(self.weight_array, grid_crossing())
                          )
        return sum(weighted_score)


default_center_filter = WeightedGridFilter([
    [-1, 1, 1, -1],
    [1, 2, 2, 1],
    [-1, 1, 1, -1],
])


def rect_is_image_center_v2(rect, width=1, height=1):
    rect = rect.resize(1 / width, 1 / height)
    return default_center_filter.compute_crossing_score(rect, half_score=True) >= 4


def image_is_grayscale(image_path, variation: float = 2):
    if not os.path.exists(image_path):
        return False
    img = plt.imread(image_path, cv2.IMREAD_ANYDEPTH)
    if len(img.shape) == 2:
        return True

    channels = cv2.split(img)
    delta1 = cv2.absdiff(channels[0], channels[1])
    delta2 = cv2.absdiff(channels[0], channels[2])
    normalized = sqrt(delta1 ** 2 + delta2 ** 2).mean()
    return normalized <= variation


if __name__ == '__main__':
    image='/mnt/c/Users/VDI-WIN10/Downloads/2020-11-30-02-28-10.jpg'
    print(image_is_grayscale(image))
    # dir = '/mnt/d/mj/doc/jnx/test/信德汽车总部机电工位1-20191202140000'
    # imagepath = '3240.jpg'
    # rect = {'left': 148.56266784668,
    #         'top': 0,
    #         'width': 493.03881835938,
    #         'height': 523.23706054688
    #         }
    # colors = main_colors_from_image_rect(os.path.join(dir, imagepath), rect)
    # print(colors)
    print(md5('亮马名居店'))
