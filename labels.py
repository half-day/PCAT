import json
import random
import colorsys
import numpy as np
from typing import Optional


def random_rgb_colors(num_colors: int, seed: int = 0, reserve_black: bool = False) -> 'np.array[num_colors, 3]':

    def hsv_distance(hsv1: 'np.array[3]', hsv2: 'np.array[3]') -> float:
        hsv1 = np.array(hsv1)
        hsv2 = np.array(hsv2)
        
        xy1 = hsv1[1] * np.exp(1j * 2 * np.pi * hsv1[0])
        xy2 = hsv2[1] * np.exp(1j * 2 * np.pi * hsv2[0])
        
        xyz1 = np.array([xy1.real, xy1.imag, hsv1[2]])
        xyz2 = np.array([xy2.real, xy2.imag, hsv2[2]])
        
        return np.linalg.norm(xyz1 - xyz2)
    
    def random_hsv(seed: 'Optional[int]' = None) -> 'np.array[3]':
        if seed is not None:
            random.seed(seed)
        h = random.random()
        s = 0.2 + random.random() * 0.8
        v = 0.2 + random.random() * 0.8
        return np.array([h, s, v])
    
    random.seed(seed)
    colors_hsv = []
    pre = np.array([0, 0, 0])
    if reserve_black:
        colors_hsv.append(pre)
        num_colors -= 1

    for _ in range(num_colors):
        now = random_hsv()
        while hsv_distance(now, pre) < 1:
            now = random_hsv()
        pre = now
        colors_hsv.append(now)

    colors_rgb = [colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]) for hsv in colors_hsv]

    return np.array(colors_rgb)


with open('labels.json', 'r', encoding='utf-8') as f:
    labels_dict = json.load(f)


class_labels = [item['label'] for item in labels_dict]
class_labels_cn = [item['label_cn'] for item in labels_dict]
# class_labels_id = [item['id'] for item in labels_dict]

#
class_labels_id = [str(i) for i in range(len(labels_dict))]
#

class_colors_hex = [item['color'] for item in labels_dict]
class_colors_rgb = [tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)) for hex_color in class_colors_hex]

labels_dict_pack = {
    'label_id': class_labels_id,
    'label': class_labels,
    'label_cn': class_labels_cn,
    'color_hex': class_colors_hex,
    'color_rgb': class_colors_rgb,
}

# print(class_labels)
# print(class_labels_cn)
# print(class_labels_id)
# print(class_colors_hex)
# print(class_colors_rgb)

ui_groups = {
    'unlabel': [0],
}

colors_rgb = random_rgb_colors(3000, seed=0, reserve_black=True)
