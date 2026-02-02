import numpy as np

def rotation2D(x, y, alpha):
    x_rot = x * np.cos(alpha)-y * np.sin(alpha)
    y_rot = x * np.sin(alpha) + y * np.cos(alpha)
    return x_rot, y_rot

def rotation3D(coord, tranparam):
    x = tranparam[0]
    y = tranparam[1]
    z = tranparam[2]
    alpha = tranparam[-1]
    c = np.cos(alpha)
    s = np.sin(alpha)
    r = 1 - c
    rot_matrix = np.array([[c + r*x**2, r*x*y - s*z, r*x*z + s*y],
                           [r*y*x + s*z, c + r*y**2, r*y*z - s*x],
                           [r*z*x - s*y, r*z*y + s*x, c + r*z**2]])
    coord_rot = np.dot(rot_matrix, coord.T).T
    return coord_rot
    


class Model:
    def __init__(self, vertices, indices, 
                 color=None, transform = {"center":[0, 0, 0],
                 "rotation" : [0, 0, 1, 0], "scale" : [1, 1, 1],
                 "scaleOrientation" : [0, 0, 1, 0],
                 "translation" : [0, 0, 0]}):
        """
        vertices: массив вершин [[x1,y1,z1], [x2,y2,z2], ...]
        indices: массив индексов
        colors: массив цветов [[r,g,b], ...] или None для автоматических цветов
        transform: словарь, в котором указаны параметры трансформации модели
        """
        self.vertices = np.array(vertices, dtype=np.float32) 
        self.indices = np.array(indices, dtype=np.uint32)
        if transform['rotation'][-1] != 0:
            self.t_vertices = rotation3D(self.vertices - transform['center'],
                                        transform['rotation']) + transform['center'] + transform['translation']
        else:  self.t_vertices = self.vertices + transform['translation']

        if color is None:
            # Автогенерация цветов если не указаны
            # self.colors = np.random.rand(len(vertices), 3).astype(np.float32)
            color = np.random.rand(1, 3)

        self.colors = (color*np.ones((len(vertices),3))).astype(np.float32)
            
        # Объединение вершин и цветов в один массив
        self.vertex_data = np.zeros(len(vertices), dtype=[
            ('position', np.float32, 3),
            ('color', np.float32, 3)
        ])
        
        self.vertex_data['position'] = self.t_vertices
        self.vertex_data['color'] = self.colors
        
    def get_vertex_buffer(self):
        """Возвращает объединенный буфер вершин и цветов"""
        return self.vertex_data.view(np.float32).reshape(-1, 6)
