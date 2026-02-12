## READ .wrl-files from SolidWorks and T-Flex
from model import Model
import numpy as np
import time
import re

import cProfile
import pstats

class Data:
    def __init__(self, file):
        self.model_list = self.parse_wrl(file)
    
    def parse_wrl_Solid(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        flag_point = 0
        flag_index = 0
        # flag_normal = 0
        model_list = []
        color = None
        for line in lines:
            line = line[:-1]
            if "diffuseColor" in line:
                color = list(map(float,line.split(' ')[-3:]))

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
            
            # if line == 'vector [':
            #     normal = ''
            #     flag_normal = 1
            #     continue
            # if flag_normal == 1:
            #     if line == ']':
            #         flag_normal = 0
            #         continue
            #     normal = ''.join([normal, line])

            if line  == 'coordIndex [':
                flag_index = 1
                continue
            if flag_index == 1:
                if line == ']':
                    flag_index = 0
                    points_list = np.fromstring(points.replace(', ', ' '), sep=' ', dtype=np.float32).reshape(-1,3)
                    # В Solid работа с normals сложнее чем в TFLEX, поэтому в этих WRL она не будет реализвана  
                    # normal_list = np.fromstring(normal.replace(', ', ' '), sep=' ', dtype=np.float32).reshape(-1,3)
                    indexs_list = np.fromstring( indexs.replace(', -1', ''), sep=', ', dtype=np.float32)
                    model_list += [Model(points_list, indexs_list, normals= None, color = color)]
                    continue
                indexs = ' '.join([indexs, line])
        return model_list
    
    def parse_wrl_TFlex(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        flag_point = 0
        flag_index = 0
        flag_normal = 0
        points = ''
        indexs = ''
        normal = ''
        transform_dict = {}
        flag_transform = 0

        model_list = []

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
            if re.search(r"DEF T.* Transform", line):
                flag_transform = 1
                continue
            if flag_transform != 0:
                key = re.search(r"\w+", line)[0]
                transform_dict[key] = list(map(float, line[len(key)+1:].split()))
                if key == "translation" : flag_transform = 0

            #READ COORDS, INDEXS AND NORMALS 
            if line == 'point':
                normal = ''
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

            if normal == '':
                if line == 'vector':
                    flag_normal = 1
                    continue
                if flag_normal == 1:
                    if line[-1] == ']':
                        normal = line[:-1]
                        flag_normal = 0

                        points_list = np.fromstring(points.replace(',', ' '), sep=' ', dtype=np.float32).reshape(-1,3)
                        normal_list = np.fromstring(normal.replace(',', ' '), sep=' ', dtype=np.float32).reshape(-1,3)
                        indexs_list =np.fromstring( indexs.replace(',-1', ''), sep=',', dtype=np.float32)
                        model_list += [Model(points_list, indexs_list, normal_list, color = color, transform = transform_dict)]  
        return model_list

    def parse_wrl(self, file_path):
        with open(file_path, 'r') as f:
            for i in range(3):
                line = f.readline()
        if "T-FLEX" in line: return self.parse_wrl_TFlex(file_path)
        return self.parse_wrl_Solid(file_path)
            
            
if __name__ == "__main__":

    start_time = time.time()
    data = Data("wrls\\aabb_tests.wrl")
    print(data.model_list[0].normals)
    print(data.model_list[1].normals)
    # cProfile.run('Data("wrls\\Example2.0.wrl")', 'profile_stats') # Example2.0.wrl")
   
    end_time = time.time()
    execution_time = end_time-start_time
    print(f"{execution_time:.4f}")
    # stats = pstats.Stats('profile_stats')
    # stats.sort_stats('time').print_stats(10)
