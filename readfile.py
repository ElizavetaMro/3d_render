from model import Model
import re

class Data:
    def __init__(self, file):
        self.model_list, self.max_coord = self.parse_wrl(file)
    
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

        dict_mat = dict()
        dict_app = dict()
        flag_mat_def = 0
        flag_app_def = 0
        name_mat = r"Ml\w*\b"
        name_app = r"App\w*\b"

        for line in lines:
            line = line[:-1]

            #READ Appearence
            if line.find('appearance USE')!=-1:
                old_app = re.search(name_app, line)[0]
                color = dict_app[old_app]
            if line.find('appearance DEF')!=-1:
                flag_app_def = 1
                new_app = re.search(name_app, line)[0]
                continue
            if flag_app_def == 1:
                if line.find('material USE ')!=-1:
                    old_mat = re.search(name_mat, line)[0]
                    dict_app[new_app] = dict_mat[old_mat]
                    flag_app_def=0
                    color= dict_app[new_app]
                    continue
                if line.find('material DEF ')!=-1:
                    flag_mat_def = 1
                    new_mat= re.search(name_mat, line)[0]
                    continue
                if flag_mat_def==1:
                    if line.find('diffuseColor') != -1:
                        color = list(map(float, line[len('diffuseColor '):].split()))
                        dict_mat[new_mat] = color
                        dict_app[new_app] = color
                        flag_mat_def=0
                        flag_app_def=0
                        continue

            #READ COORDS AND INDEXS
            if line == 'point':
                indexs = ''
                flag_point = 1
                continue
            if flag_point == 1:
                if line[-1] == ']':
                    points = line[:-1]
                    flag_point = 0

            if indexs == '':
                if line  == 'coordIndex [':
                    flag_index = 1
                    continue
                if flag_index == 1:
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
                        model_list += [Model(points_list, indexs_list, color)]
                        max_coord_new = max(max(points_list))
                        max_coord = max_coord if max_coord > max_coord_new else max_coord_new
                

        return model_list, max_coord

    def parse_wrl(self, file_path):
        with open(file_path, 'r') as f:
            for i in range(3):
                line = f.readline()
        if "T-FLEX" in line: return self.parse_wrl_TFlex(file_path)
        return self.parse_wrl_Solid(file_path)
            
            


if __name__ == "__main__":
    data = Data("wrls\\Example2.0.wrl")
    print(len(data.model_list))