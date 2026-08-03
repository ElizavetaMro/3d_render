import numpy as np
import glm
import os
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QSurfaceFormat, QOpenGLContext

class OpenGLRenderWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        # Настройка формата OpenGL
        format = QSurfaceFormat()
        format.setVersion(3, 3)
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        format.setSamples(4)
        self.setFormat(format)

        # Матрицы (будут инициализированы в initializeGL)
        self.view = None
        self.projection = None
                
        # Параметры камеры
        self.camera_pos = glm.vec3(0.0, 0.0, -1.0)
        self.fov = 60.0
        self.near = 0.01
        self.far = 2.0
        
        # Параметры света
        self.light_pos = glm.vec3(0.0, 1.0, 1.0)
        self.light_color = glm.vec3(1.0, 1.0, 1.0)
        self.view_pos = glm.vec3(10.0, 0.0, 10.0)

    def initializeGL(self):
        """Инициализация OpenGL"""
        self.shader = None
        self.model = None
        self.width = 800
        self.height = 600
        self.view = glm.translate(glm.mat4(1.0), self.camera_pos)
        # Устанавливаем clear color
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
    
    def resizeGL(self, w, h):
        """Обработка изменения размера"""
        glViewport(0, 0, w, h)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.model:
            glUseProgram(self.shader)
            projection = glm.perspective(
                glm.radians(self.fov), 
                1, 
                self.near, 
                self.far
            )

            glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"),
                                1, GL_FALSE, glm.value_ptr(self.view))
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"),
                                1, GL_FALSE, glm.value_ptr(projection))
            if self.model['size_point'] == 9:
                light_pos_loc = glGetUniformLocation(self.shader, "lightPos")
                glUniform3f(light_pos_loc, 
                            self.light_pos.x, 
                            self.light_pos.y, 
                            self.light_pos.z)
            
            light_color_loc = glGetUniformLocation(self.shader, "lightColor")
            glUniform3f(light_color_loc,
                           self.light_color.x,
                           self.light_color.y,
                           self.light_color.z)
            
            view_pos_loc = glGetUniformLocation(self.shader, "viewPos")
            glUniform3f(view_pos_loc,
                           self.view_pos.x,
                           self.view_pos.y,
                           self.view_pos.z)
        
            model_loc = glGetUniformLocation(self.shader, "model")
            if model_loc is not None and model_loc >= 0:
                model_matrix = glm.mat4(1.0)
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_matrix))
                
                # Привязываем VAO
                glBindVertexArray(self.model['VAO'])
                
                # Рисуем
                glDrawElements(
                    GL_TRIANGLES,
                    len(self.model['indices']),
                    GL_UNSIGNED_INT,
                    None
                )
                
                # Отвязываем VAO (хорошая практика)
                glBindVertexArray(0)
            
            # 8. Деактивируем шейдер
            glUseProgram(0)
                

    def load_shader_source(self, filename):
        """Загружает текст шейдера из файла"""
        filepath = os.path.join("shaders", filename)
        
        if not os.path.exists(filepath):
            print(f"Файл не найден: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def init_shaders(self, mode):
        if self.shader is not None:
            self.makeCurrent()
            glDeleteProgram(self.shader)
            self.doneCurrent()
            self.shader = None

        self.makeCurrent()
        vertex_src = self.load_shader_source("vertex_"+ mode + ".glsl")
        fragment_src = self.load_shader_source("fragment_"+ mode + ".glsl")

        self.shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        self.doneCurrent()

    def clear_buffers(self):
        """Очищает буферы для моделей"""
        
        self.makeCurrent()
        if self.model is not None:
            glDeleteVertexArrays(1, [self.model['VAO']])
            glDeleteBuffers(1, [self.model['VBO']])
            glDeleteBuffers(1, [self.model['EBO']])
            self.model['indices'] = None
            self.model['size_point'] = None
            self.model = None
        self.doneCurrent()

    def cleanup(self):
        """Освобождение ресурсов"""
        self.makeCurrent()
        glDeleteProgram(self.shader)
        self.doneCurrent()
        self.clear_buffers()
        
    def load_buffers(self, all_vertices, all_indices, size_point):
        """Загрузка нескольких моделей одним батчем"""

        self.clear_buffers()

        self.makeCurrent()
        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)
        
        glBindVertexArray(VAO)
        
        # Вершинный буфер
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, all_vertices.nbytes, all_vertices, GL_STATIC_DRAW)
        
        # Буфер индексов
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, all_indices.nbytes, all_indices, GL_STATIC_DRAW)
        
        # Атрибуты вершин
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, size_point * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, size_point * 4, ctypes.c_void_p(3 * 4))

        if size_point==9:
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, size_point * 4, ctypes.c_void_p(6 * 4))
        
        self.model = {
            'VAO': VAO,
            'VBO': VBO,
            'EBO': EBO,
            'indices': all_indices,
            'size_point': size_point
        }
        glBindVertexArray(0)
        self.doneCurrent()

    def load_models(self, models, k=1.5):
        """Загрузка моделей
          определение размерности, выбор работы со светом
          создание шейдеров
          загрузка буфферов"""
        
        all_vertices = np.concatenate([m.get_vertex_buffer() for m in models])
        size_point = all_vertices[0].shape[-1]
        step_indices = [0]
        for i in range(len(models)-1):
            new_add = step_indices[-1] + len(models[i].vertices)
            step_indices += [new_add]

        all_indices = np.concatenate([m.indices + step_indices[i] for i, m in enumerate(models)])
        normalize = max(all_vertices.min(), all_vertices.max(), key=abs)*k
        if size_point == 6:
            normal_vector = np.array([normalize, normalize, normalize, 1, 1, 1])
            mode = "smpl"
            self.init_shaders(mode)
            print("init_shaders_Simple()")

        elif size_point == 9:
            normal_vector = np.array([normalize, normalize, normalize, 1, 1, 1, 1, 1, 1])
            mode = "light"
            self.init_shaders(mode)
            print("init_shaders_Light()")
        else: print("Ошибка в загрузке модели")
        all_vertices = (all_vertices/normal_vector).astype(np.float32)
        self.load_buffers(all_vertices, all_indices, size_point)