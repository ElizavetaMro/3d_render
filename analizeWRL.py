import re

with open("wrls\\Detal_2.wrl", 'r') as f:
    lines = f.readlines()

dict_mat = dict()
dict_app = dict()
flag_mat_def = 0
flag_app_def = 0
flag_model = 0
name_mat = r"Ml\w*\b"
name_app = r"App\w*\b"

for line in lines:
    if re.search(r"DEF T.* Transform", line):
        flag_model = 1
        continue

    if line.find('appearance DEF')!=-1:
        flag_app_def = 1
        new_app = re.search(name_app, line)[0]
        continue
    if flag_app_def == 1:
        if line.find('material USE ')!=-1:
            old_mat = re.search(name_mat, line)[0]
            dict_app[new_app] = dict_mat[old_mat]
            flag_app_def=0
            color = dict_app[new_app]
            print(color)
            continue

        if line.find('material DEF ')!=-1:
            flag_mat_def = 1
            new_mat= re.search(name_mat, line)[0]
            continue
        if flag_mat_def==1:
            if line.find('diffuseColor') != -1:
                color = list(map(float, line[len('diffuseColor '):-1].split()))
                dict_mat[new_mat] = color
                dict_app[new_app] = color
                flag_mat_def=0
                flag_app_def=0
                print(color)
                continue

print(dict_app)

    


# pattern = r"DEF T.* Transform"

# count_def_transform = 0
# number_line = 0
# transform_flag = 0
# count_point = 0
# for line in lines:
#     number_line += 1
#     if re.search(pattern, line):
#         count_def_transform += 1
#         transform_flag = 1
#     if  line=='point\n':
#         if transform_flag == 1:
#             count_point += 1
#             transform_flag = 0
#         else: print(number_line)
