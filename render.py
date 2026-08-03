import numpy as np
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QSurfaceFormat, QOpenGLContext
from sphere import Sphere

class OpenGLRenderWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rendering_enabled = False
        self.setMinimumSize(400, 400)
        
        # Настройка формата OpenGL
        format = QSurfaceFormat()
        format.setVersion(3, 3)
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        format.setSamples(4)
        self.setFormat(format)
        # Ваш рендерер
        self.model_renderer = None

    def initializeGL(self, models):
        """Инициализация OpenGL"""
        # Инициализируем GLAD или другой загрузчик OpenGL
    
        self.model_renderer = ModelRendererQt()
        self.model_renderer.load_models(models, k=2)

        # Устанавливаем clear color
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    
    def resizeGL(self, width, height):
        """Обработка изменения размера"""
        glViewport(0, 0, width, height)

    def paintGL(self):
        """Рендеринг каждого кадра"""
        # Очищаем буферы
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Вызываем рендеринг вашего класса
        if self.rendering_enabled:
            if self.model_renderer:
                self.model_renderer.render()
    
    def closeEvent(self, event):
        """Очистка ресурсов"""
        self.timer.stop()
        if self.model_renderer:
            self.model_renderer.cleanup()
        super().closeEvent(event)


class ModelRendererQt:
    def __init__(self):
        self.shader = None
        self.model = None
        self.width = 800
        self.height = 600

    
    def init_shaders_Simple(self):
        vertex_src = """
        #version 330 core
        layout(location = 0) in vec3 a_position;
        layout(location = 1) in vec3 a_color;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        out vec3 v_color;
        
        void main()
        {
            gl_Position = projection * view * model * vec4(a_position, 1.0);
            v_color = a_color;
        }
        """
        
        fragment_src = """
        #version 330 core
        in vec3 v_color;
        out vec4 frag_color;
        
        void main()
        {
            frag_color = vec4(v_color, 1.0);
        }
        """
        self.shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
  
    def init_shaders_Light(self):

        vertex_shader = """
        #version 330 core
        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec3 aNormal;
        layout(location = 2) in vec3 aColor;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        out vec3 FragPos;
        out vec3 Normal;
        out vec3 VertexColor;

        void main() {
            FragPos = vec3(model * vec4(aPos, 1.0));
            Normal = mat3(transpose(inverse(model))) * aNormal;
            VertexColor = aColor;
            
            gl_Position = projection * view * vec4(FragPos, 1.0);
        }
        """

        fragment_shader = """
        #version 330 core
        in vec3 FragPos;
        in vec3 Normal;
        in vec3 VertexColor;

        out vec4 FragColor;

        uniform vec3 lightPos;     // Позиция света (справа сверху)
        uniform vec3 lightColor;   // Белый цвет (1,1,1)
        uniform vec3 viewPos;

        void main() {
            // Нормализация (на всякий случай)
            vec3 norm = normalize(Normal);
            
            // Окружающее освещение
            float ambientStrength = 0.5;
            vec3 ambient = ambientStrength * lightColor;
            
            // Диффузное освещение
            vec3 lightDir = normalize(lightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor;
            
            
            // Комбинируем освещение с цветом вершины
            vec3 result = (ambient + diffuse) * VertexColor;
            
            FragColor = vec4(result, 1.0);
        }
        """
        self.shader = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )
        print(self.shader)
    
    def load_models(self, models, k=1.5):
        """Загрузка моделей, определение размерности, выбор работы со светом"""
        global size_point
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
            self.init_shaders_Simple()
            print("init_shaders_Simple()")

        elif size_point == 9:
            normal_vector = np.array([normalize, normalize, normalize, 1, 1, 1, 1, 1, 1])
            self.init_shaders_Light()
            print("init_shaders_Light()")

        else: print("Ошибка в загрузке модели")
        all_vertices = (all_vertices/normal_vector).astype(np.float32)
        self.load_buffers(all_vertices, all_indices)
        
    def load_buffers(self, all_vertices, all_indices):
        """Загрузка нескольких моделей одним батчем"""
        
        global size_point

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
        }

    def render(self, fov=60, near=0.01, far=2):
        """Основной цикл рендеринга"""
        # Проверка OpenGL контекста в PyQt6
        context = QOpenGLContext.currentContext()
        print(f"OpenGL context valid: {context is not None}")
    
        if context is None:
            print("No OpenGL context! Skipping render")
            return
        camera_pos= [0, 0, -1]

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Матрицы вида и проекции
        view = glm.translate(glm.mat4(1.0), glm.vec3(*camera_pos))

        projection = glm.perspective(glm.radians(fov), 8/6, near, far)
        
        # Источник света справа сверху (белый)
        light_pos = glm.vec3(0.0, 1.0, 1.0)
        light_color = glm.vec3(1.0, 1.0, 1.0)
        view_pos = glm.vec3(10.0, 0.0, 10.0)

        glUseProgram(self.shader)
        
        # Передача матриц в шейдер
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "view"), 
            1, GL_FALSE, 
            glm.value_ptr(view)
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 
            1, GL_FALSE, 
            glm.value_ptr(projection)
        )
        
        if size_point==9:
            # Передаем параметры освещения
            glUniform3f(glGetUniformLocation(self.shader, "lightPos"), light_pos.x, light_pos.y, light_pos.z)
            glUniform3f(glGetUniformLocation(self.shader, "lightColor"), light_color.x, light_color.y, light_color.z)
            glUniform3f(glGetUniformLocation(self.shader, "viewPos"), view_pos.x, view_pos.y, view_pos.z)

        # Рендеринг всех моделей
        glBindVertexArray(self.model['VAO'])
        glDrawElements(
            GL_TRIANGLES, 
            len(self.model['indices']), 
            GL_UNSIGNED_INT, 
            None
        )

    
    def cleanup(self):
        """Освобождение ресурсов"""
        glDeleteProgram(self.shader)
        
        glDeleteVertexArrays(1, [self.model['VAO']])
        glDeleteBuffers(1, [self.model['VBO']])
        glDeleteBuffers(1, [self.model['EBO']])
