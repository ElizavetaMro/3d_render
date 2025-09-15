from model import Model
import numpy as np

class Data:
    def __init__(self, file):
        self.model_list, self.max_coord = self.parse_wrl_Solid(file)
    
    def parse_wrl_Solid(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        flag_point = 0
        flag_index = 0
        model_list = []
        max_coord = 0

        for line in lines:
            line = line[:-1]
            if line == 'point [':
                points = ''
                indexs = ''
                flag_point = 1
                continue
            if flag_point == 1:
                if line == ']':
                    flag_point = 0
                    continue
                points = ''.join([points, line])

            if line  == 'coordIndex [':
                flag_index = 1
                continue
            if flag_index == 1:
                if line == ']':
                    flag_index = 0
                    points_list = list(map(lambda x: list(map(float, x.split())), points.split(', ')))
                    indexs_list = list(
                                    map(
                                        lambda x:
                                            list(map(int, x[1:].split(', '))) if x[0] == ',' else list(map(int, x.split(', '))),
                                            indexs.split(', -1')[:-1]
                                        )
                                    )
                    indexs_list = [el for els in indexs_list for el in els]
                    model_list += [Model(points_list, indexs_list)]
                    max_coord_new = max(max(points_list))
                    max_coord = max_coord if max_coord > max_coord_new else max_coord_new
                    continue
                indexs = ' '.join([indexs, line])
        return model_list, max_coord
    
    def parse_wrl_TFlex(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        flag_point = 0
        flag_index = 0
        points = ''
        indexs = ''

        model_list = []
        max_coord = 0

        for line in lines:
            line = line[:-1]
            if line == 'point':
                points = ''
                indexs = ''
                flag_point = 1
                continue
            if flag_point == 1:
                if line == '[': continue
                if line[-1] == ']':
                    points = line[:-1]
                    flag_point = 0

            if indexs == '':
                if line  == 'coordIndex [':
                    flag_index = 1
                    continue
                if flag_index == 1:
                    if line == '[': continue
                    if line[-1] == ']':
                        indexs = line[:-1]
                        flag_index = 0
                        points_list = list(map(lambda x: list(map(float, x.split())), points.split(',')))
                        indexs_list = list(
                                        map(
                                            lambda x:
                                                list(map(int, x[1:].split(','))) if x[0] == ',' else list(map(int, x.split(','))),
                                                indexs.split(',-1')[:-1]
                                            )
                                        )
                        indexs_list = [el for els in indexs_list for el in els]
                        model_list += [Model(points_list, indexs_list)]
                        max_coord_new = max(max(points_list))
                        max_coord = max_coord if max_coord > max_coord_new else max_coord_new

        return model_list, max_coord

if __name__ == "__main__":
    data = Data("wrls\\Detal_1.wrl")
    print(data.model_list[0].get_vertex_buffer() )

    print(data.model_list[0].indices)
