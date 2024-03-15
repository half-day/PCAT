import json
import math
import random
import time
import colorsys
import numpy as np

with open('labels.json', 'r', encoding='utf-8') as f:
    labels_dict = json.load(f)


# print(labels_dict)

def hsv_distance(hsv1, hsv2):
    x1 = math.cos(hsv1[0] * 2 * math.pi) * hsv1[1]
    y1 = math.sin(hsv1[0] * 2 * math.pi) * hsv1[1]
    z1 = hsv1[2]
    x2 = math.cos(hsv2[0] * 2 * math.pi) * hsv2[1]
    y2 = math.sin(hsv2[0] * 2 * math.pi) * hsv2[1]
    z2 = hsv2[2]
    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    return math.sqrt(dx * dx + dy * dy + dz * dz)


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

random.seed(time.time())
colors_hsv = [np.array([0, 0, 0])]
pre = colors_hsv[-1]

for i in range(100):
    h = random.randint(0, 100) / 100
    s = random.randint(20, 100) / 100
    v = random.randint(20, 100) / 100
    tmp = np.array([h, s, v])
    while hsv_distance(tmp, pre) < 1:
        h = random.randint(0, 100) / 100
        s = random.randint(20, 100) / 100
        v = random.randint(20, 100) / 100
        tmp = np.array([h, s, v])
    pre = tmp
    colors_hsv.append(tmp)

colors_rgb = [colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]) for hsv in colors_hsv]

# colors_hex = [
# '#000000',
# '#B0C4DE', '#FF00FF', '#1E90FF', '#FA8072',
# '#EEE8AA', '#FF1493', '#7B68EE', '#FFC0CB',
# '#696969', '#556B2F', '#CD853F', '#000080',
# '#32CD32', '#7F007F', '#B03060', '#800000',
# '#483D8B', '#008000', '#3CB371', '#008B8B',
# '#FF0000', '#FF8C00', '#FFD700', '#00FF00',
# '#9400D3', '#00FA9A', '#DC143C', '#00FFFF',
# '#00BFFF', '#0000FF', '#ADFF2F', '#DA70D6'
# ]
#
# colors_rgb = [tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5)) for hex_color in colors_hex]
# print(colors_rgb)
