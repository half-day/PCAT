import copy
from math import pi
import numpy as np
import file_utils
import pptk
from labels import colors_rgb


class AnnotateViewer(pptk.viewer):
    def __init__(self, port):
        self._portNumber = port
        self._process = None


class AnnotateViewerHelpler:
    def __init__(self, client_port, viewer_hwnd) -> None:
        self.port = client_port
        self.hwnd = viewer_hwnd
        self.viewer = AnnotateViewer(self.port)
        self._anno_mode = 'sem'
        self.init_default_params()

    def init_default_params(self):
        self.set_point_size_range([0.0001, 0.001, 0.005, 0.01, 0.02])
        self.setup(np.zeros(0), np.zeros(0))

    @property
    def cur_labels_stack(self):
        if self._anno_mode == 'sem':
            return self.sem_labels_stack
        else:
            return self.ins_labels_stack

    @property
    def cur_scale(self):
        if self._anno_mode == 'sem':
            return self._sem_scale
        else:
            return self._ins_scale

    @property
    def cur_color_map(self):
        if self._anno_mode == 'sem':
            return self._sem_color_map
        else:
            return self._ins_color_map

    def set_anno_mode(self, value):
        self._anno_mode = str(value)

    # init data

    def setup(self, points, colors):
        # data
        self.points = points
        self.colors = colors
        # label
        self.sem_labels_stack = [np.zeros(points.shape[0]).astype(np.int16)]
        self.ins_labels_stack = [np.zeros(points.shape[0]).astype(np.int16)]
        self._anno_mode = 'sem'
        # focus
        self.focus_stack = [np.arange(points.shape[0])]
        self.lock_laebl = np.array([])
        self.focus_label = np.array([])
        return

    def set_sem_color_map(self, color_map='jet', scale=None):
        self._sem_color_map = color_map
        self._sem_scale = scale

    def set_ins_color_map(self, color_map='jet', scale=None):
        self._ins_color_map = color_map
        self._ins_scale = scale

    # def set_color_map(self, color_map='jet', scale=None):
    #     self.color_map = color_map
    #     self.scale = scale
    #     self.viewer.color_map(color_map, scale)

    # pack data

    def get_labels_info(self):
        sem_label_points = np.bincount(self.sem_labels_stack[-1])
        sem_label_points = np.pad(sem_label_points, (0, len(self._sem_color_map) - len(sem_label_points)), 'constant',
                                  constant_values=0)

        ins_label_counts = [''] * len(sem_label_points)
        for i in range(len(ins_label_counts)):
            cur_sem_ins = self.ins_labels_stack[-1][self.sem_labels_stack[-1] == i]
            nonzero_cnt = len(np.unique(cur_sem_ins[cur_sem_ins != 0]))
            unanno_cnt = (cur_sem_ins == 0).sum()
            if len(cur_sem_ins) == 0:
                ins_label_counts[i] = ''
            else:
                ins_label_counts[i] = f'{nonzero_cnt} <{unanno_cnt}>'

        return sem_label_points, ins_label_counts

    # io

    def load_data(self, filepath):
        points, colors = file_utils.load_data(filepath)
        self.setup(points, colors)
        self.viewer.clear()
        self.viewer.reset()
        self.viewer.load(points, colors, self.cur_labels_stack[-1], color_map=self.cur_color_map, scale=self.cur_scale)
        return self.get_labels_info()

    def load_labels(self, filepath):
        labels = file_utils.load_label(filepath)
        print('labels load', labels.shape)
        sem_labels = labels[0]
        ins_labels = labels[1]
        print('sem:', sem_labels.shape, self.sem_labels_stack[-1].shape)
        print('ins:', ins_labels.shape, self.ins_labels_stack[-1].shape)
        if sem_labels.shape == self.sem_labels_stack[-1].shape and ins_labels.shape == self.ins_labels_stack[-1].shape:
            self.sem_labels_stack[-1] = sem_labels
            self.ins_labels_stack[-1] = ins_labels
            if len(self.focus_stack) == 1:
                self.viewer.attributes(self.colors, self.cur_labels_stack[-1])
            else:
                cur_focus_mask = self.focus_stack[-1]
                self.render(cur_focus_mask)
        else:
            print('点云与标签 shape 不一致')
        return self.get_labels_info()

    def save_labels(self, filepath):
        labels = np.vstack([self.sem_labels_stack[-1], self.ins_labels_stack[-1]])
        file_utils.save_label(filepath, labels)
        print('labels saved:', labels.shape)

    # action

    def undo(self):
        if len(self.cur_labels_stack) > 1:
            print(self.cur_labels_stack)
            self.cur_labels_stack.pop()

            attr_id = self.viewer.get('curr_attribute_id')
            mask = self.focus_stack[-1]
            self.viewer.attributes(self.colors[mask], self.cur_labels_stack[-1][mask])
            self.viewer.set(curr_attribute_id=attr_id[0], selected=[])
            return self.get_labels_info()
        else:
            # print('no undo')
            return

    def set_camera(self, direction):
        if direction == 'front':
            self.viewer.set(theta=0, phi=0)
        elif direction == 'back':
            self.viewer.set(theta=0, phi=pi)
        elif direction == 'top':
            self.viewer.set(theta=pi / 2, phi=0)
        elif direction == 'bottom':
            self.viewer.set(theta=-pi / 2, phi=0)
        elif direction == 'left':
            self.viewer.set(theta=0, phi=-pi / 2)
        elif direction == 'right':
            self.viewer.set(theta=0, phi=pi / 2)
        else:
            return

    def render(self, mask, label_type='sem'):
        if mask is None:
            self.focus_label = []
            if len(self.focus_stack) > 1:
                del self.focus_stack[-1]
            mask = self.focus_stack[-1]
        # for value in self.lock_dict.values():
        #     mask = np.append(mask, value)
        #     mask = np.unique(mask)
        #     mask = np.sort(mask)
        points = self.points[mask]
        colors = self.colors[mask]
        cur_labels = self.cur_labels_stack[-1][mask]
        # p = get_perspective()
        self.viewer.clear()
        self.viewer.reset()
        self.viewer.load(points, colors, cur_labels, color_map=self.cur_color_map, scale=self.cur_scale)
        # print(self.cur_color_map)
        # set_perspective(p)
        return self.get_labels_info()

    def annotate(self, label: str, overwrite=True, atype='sem'):
        selected = self.viewer.get('selected')
        if len(selected) == 0:
            return

        mask = self.focus_stack[-1]

        if atype == 'sem':
            label = int(label)
        else:
            label = 0 if label is None else self.cur_labels_stack[-1].max() + 1
            if label > len(colors_rgb) - 1:
                # print('over')
                return
            # print(label)

        # if overwrite or int(label) == 0:
        #     if len(self.cur_labels_stack) < 4:
        #         self.cur_labels_stack.append(copy.deepcopy(self.cur_labels_stack[-1]))
        #         self.cur_labels_stack[-1][mask[selected]] = int(label)
        #     else:
        #         # print('over stack')
        #         del self.cur_labels_stack[0]
        #         self.cur_labels_stack.append(copy.deepcopy(self.cur_labels_stack[-1]))
        #         self.cur_labels_stack[-1][mask[selected]] = int(label)
        # else:
        #     cur_region_mask = mask[selected]
        #     print(cur_region_mask)
        #     cur_region_change_mask = np.where(self.cur_labels_stack[-1][cur_region_mask] == 0)
        #     print(cur_region_change_mask)
        #     self.cur_labels_stack[-1][cur_region_mask[cur_region_change_mask]] = int(label)
        if len(self.cur_labels_stack) < 4:
            self.cur_labels_stack.append(copy.deepcopy(self.cur_labels_stack[-1]))
        else:
            del self.cur_labels_stack[0]
            self.cur_labels_stack.append(copy.deepcopy(self.cur_labels_stack[-1]))
        if len(self.lock_laebl) == 0:
            self.cur_labels_stack[-1][mask[selected]] = int(label)
        else:
            cur_region_mask = np.array(mask[selected])
            cur_region_change_mask = np.where(~np.isin(self.cur_labels_stack[-1][cur_region_mask], self.lock_laebl))
            self.cur_labels_stack[-1][cur_region_mask[cur_region_change_mask]] = int(label)

        attr_id = self.viewer.get('curr_attribute_id')
        self.viewer.attributes(self.colors[mask], self.cur_labels_stack[-1][mask])
        self.viewer.set(curr_attribute_id=attr_id[0], selected=[])
        return self.get_labels_info()

    # def annotate_ins(self, sem_label: str, overwrite=True):
    #     selected = self.viewer.get('selected')
    #     if len(selected) == 0:
    #         return

    #     mask = self.focus_stack[-1]

    #     if overwrite or int(label) == 0:
    #         self.sem_labels[mask[selected]] = int(label)
    #     else:
    #         print('here')
    #         cur_region_mask = mask[selected]
    #         cur_region_change_mask = np.where(self.sem_labels[cur_region_mask] == 0)
    #         self.sem_labels[cur_region_mask[cur_region_change_mask]] = int(label)

    #     attr_id = self.viewer.get('curr_attribute_id')
    #     self.viewer.attributes(self.colors[mask], self.sem_labels[mask])
    #     self.viewer.set(curr_attribute_id=attr_id[0], selected=[])
    #     pass

    # # lock
    # def lock(self, lockMode):
    #     if lockMode is True:
    #         selected = self.viewer.get('selected')
    #         print(np.sort(selected))
    #         if len(selected) != 0:
    #             print(self.lock_stack[-1])
    #             self.lock_stack.append(self.lock_stack[-1][selected])
    #             print(self.lock_stack[-1])
    #         else:
    #             return
    #     else:
    #         if len(self.lock_stack) > 1:
    #             self.lock_stack.pop()
    #         else:
    #             return
    #
    #     cur_focus_mask = self.focus_stack[-1]
    #     print(cur_focus_mask)
    #     self.render(cur_focus_mask)

    def lock(self, label: str):
        self.lock_laebl = np.append(self.lock_laebl, int(label))
        # cur_focus_mask = self.focus_stack[-1]
        # self.render(cur_focus_mask)

    def unlock(self, label: str):
        selected = self.lock_laebl != int(label)
        self.lock_laebl = self.lock_laebl[selected]
        # cur_focus_mask = self.focus_stack[-1]
        # self.render(cur_focus_mask)

    def focus(self, ftype, atype='sem'):
        # select
        if ftype == 'forward':
            selected = self.viewer.get('selected')
            if len(selected) != 0:
                self.focus_stack.append(self.focus_stack[-1][selected])
            else:
                return
        elif ftype == 'backward':
            if len(self.focus_label) > 0:
                if len(self.focus_stack) > 2:
                    self.focus_stack.pop()
                else:
                    return
            elif len(self.focus_stack) > 1:
                self.focus_stack.pop()
            else:
                return
        # sem label
        elif ftype is None:
            self.focus_stack = self.focus_stack[:1]
            self.focus_label = []
        else:
            if atype == 'sem':
                filter_id = int(ftype)
                if filter_id == 0:
                    if 0 in self.focus_label:
                        selected = self.focus_label != filter_id
                        self.focus_label = self.focus_label[selected]
                    else:
                        self.focus_label = np.append(self.focus_label, filter_id)
                elif filter_id > 0:
                    self.focus_label = np.append(self.focus_label, filter_id)
                else:
                    filter_id = -filter_id
                    selected = self.focus_label != filter_id
                    self.focus_label = self.focus_label[selected]
                result = self.sem_labels_stack[-1] == len(self.cur_color_map) + 1
                for label_id in self.focus_label:
                    selected = self.sem_labels_stack[-1] == label_id
                    result = [x | y for x, y in zip(result, selected)]
                if len(self.focus_label) > 0:
                    self.focus_stack = self.focus_stack[:1]
                    self.focus_stack.append(self.focus_stack[-1][result])
                else:
                    self.focus_stack = self.focus_stack[:1]
            else:
                filter_id = int(ftype)
                selected = self.sem_labels_stack[-1] == filter_id
                self.focus_stack = self.focus_stack[:1]
                self.focus_stack.append(self.focus_stack[-1][selected])

        cur_focus_mask = self.focus_stack[-1]
        self.render(cur_focus_mask)

    # point size

    def set_point_size_range(self, point_size_range_list):
        self._point_size_idx = 0
        self._point_size_range = list(sorted(point_size_range_list))

    def increase_point_size(self):
        if self._point_size_idx < len(self._point_size_range) - 1:
            self._point_size_idx += 1
            self.viewer.set(point_size=self._point_size_range[self._point_size_idx])

    def decrease_point_size(self):
        if self._point_size_idx > 0:
            self._point_size_idx -= 1
            self.viewer.set(point_size=self._point_size_range[self._point_size_idx])
