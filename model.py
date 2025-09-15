import numpy as np

class Model:
    def __init__(self, vertices, indices, colors=None):
        """
        vertices: массив вершин [[x1,y1,z1], [x2,y2,z2], ...]
        indices: массив индексов
        colors: массив цветов [[r,g,b], ...] или None для автоматических цветов
        """
        self.vertices = np.array(vertices, dtype=np.float32) 
        self.indices = np.array(indices, dtype=np.uint32)
        
        if colors is None:
            # Автогенерация цветов если не указаны
            self.colors = np.random.rand(len(vertices), 3).astype(np.float32)
            # color = np.random.rand(1, 3)
            # self.colors = (color*np.ones((len(vertices), 3))).astype(np.float32)
        else:
            self.colors = np.array(colors, dtype=np.float32)
            
        # Объединение вершин и цветов в один массив
        self.vertex_data = np.zeros(len(vertices), dtype=[
            ('position', np.float32, 3),
            ('color', np.float32, 3)
        ])
        
        self.vertex_data['position'] = self.vertices
        self.vertex_data['color'] = self.colors
        
    def get_vertex_buffer(self):
        """Возвращает объединенный буфер вершин и цветов"""
        return self.vertex_data.view(np.float32).reshape(-1, 6)
