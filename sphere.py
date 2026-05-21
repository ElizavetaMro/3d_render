import numpy as np
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import ctypes

class Sphere:
    """Класс для визуализации лучей из заданной точки"""
    
    def __init__(self, center, radius=1.0, rays_count=36, color=(1.0, 0.0, 0.0)):
        """
        center: координаты центра (x, y, z)
        radius: радиус сферы (длина лучей)
        rays_count: количество лучей (чем больше, тем детальнее)
        color: цвет лучей (r, g, b)
        """
        self.center = np.array(center, dtype=np.float32)
        self.radius = radius
        self.rays_count = rays_count
        self.color = np.array(color, dtype=np.float32)
        self.vertices = None
        self.indices = None
        self.directions = None
        self.vao = None
        self.vbo = None
        self.ebo = None
        
        self.generate_rays()
    
    def generate_rays(self):
        """Генерирует лучи из центра сферы"""
        # Используем равномерное распределение точек на сфере
        vertices = []
        indices = []
        directions = []
        
        # Метод Фибоначчи для равномерного распределения
        phi_golden = np.pi * (3 - np.sqrt(5))  # Золотой угол
        
        for i in range(self.rays_count):
            # Вычисляем координаты на полусфере
            y = 1 - (i / float(self.rays_count))  # y от 1 до 1/rays_count
            radius_at_y = np.sqrt(1 - y*y)
            theta = i * phi_golden * 2
            
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            
            # Точка на сфере
            direction = np.array([x, y, z])
            
            # Добавляем две вершины для линии (центр -> точка)
            start_idx = len(vertices)
            vertices.append(self.center - direction * self.radius)  # Начало луча (с одной стороны сферы)
            vertices.append(self.center + direction * self.radius)  # Конец луча
            directions.append(direction)
            
            # Индексы для линии
            indices.append([start_idx, start_idx + 1])
        
        # Конвертируем в numpy массивы
        self.vertices = np.array(vertices, dtype=np.float32).reshape(-1, 3)
        self.indices = np.array(indices, dtype=np.uint32).reshape(-1, 2)
        self.directions = np.array(directions, dtype=np.float32)
        # Добавляем цвета для каждой вершины
        colored_vertices = []
        for vertex in self.vertices:
            colored_vertices.extend([vertex[0], vertex[1], vertex[2], 
                                    self.color[0], self.color[1], self.color[2]])
        
        self.colored_vertices = np.array(colored_vertices, dtype=np.float32)
    
    def setup_buffers(self):
        """Создает буферы OpenGL для рендеринга"""
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # Вершинный буфер (позиция + цвет)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.colored_vertices.nbytes, 
                    self.colored_vertices, GL_STATIC_DRAW)
        
        # Буфер индексов
        indices_flat = self.indices.flatten()
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_flat.nbytes, 
                    indices_flat, GL_STATIC_DRAW)
        
        # Атрибуты
        glEnableVertexAttribArray(0)  # Позиция
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)  # Цвет
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
        
        glBindVertexArray(0)
    
    def render(self, shader_program):
        """Рендерит лучи"""
        if self.vao is None:
            self.setup_buffers()
        
        glBindVertexArray(self.vao)
        glDrawElements(GL_LINES, len(self.indices) * 2, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
    
    def update_color(self, new_color):
        """Обновляет цвет лучей"""
        self.color = np.array(new_color, dtype=np.float32)
        
        # Пересоздаем вершины с новым цветом
        colored_vertices = []
        for vertex in self.vertices:
            colored_vertices.extend([vertex[0], vertex[1], vertex[2], 
                                    self.color[0], self.color[1], self.color[2]])
        
        self.colored_vertices = np.array(colored_vertices, dtype=np.float32)
        
        # Обновляем буфер если он уже создан
        if self.vbo is not None:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.colored_vertices.nbytes, 
                        self.colored_vertices, GL_STATIC_DRAW)
    
    def cleanup(self):
        """Освобождает ресурсы OpenGL"""
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.ebo:
            glDeleteBuffers(1, [self.ebo])