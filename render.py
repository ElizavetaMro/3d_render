import numpy as np
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import ctypes

class ModelRenderer:
    def __init__(self, window_width=800, window_height=600, title="3D Renderer"):
        self.window = None
        self.shader = None
        self.model = None # список моделей
        self.init_glfw(window_width, window_height, title)
        self.init_shaders()
        
    def init_glfw(self, width, height, title):
        if not glfw.init():
            raise Exception("GLFW initialization failed")
            
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Window creation failed")
            
        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
    def init_shaders(self):
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
           
    def load_model(self, vertices, indices, normalize = 1):
        """Загружает модель в память GPU"""
        normal_vector = np.array([normalize, normalize, normalize, 1, 1, 1])
        vertices = (vertices/normal_vector).astype(np.float32)
        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)
        
        glBindVertexArray(VAO)
        
        # Вершинный буфер
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Буфер индексов
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        # Атрибуты вершин
        glEnableVertexAttribArray(0)  # Позиция
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)  # Цвет
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
        
        self.model = {
            'VAO': VAO,
            'VBO': VBO,
            'EBO': EBO,
            'indices': indices,
        }
        
    def load_models(self, models, k=1.5):
        """Загрузка нескольких моделей одним батчем"""
        all_vertices = np.concatenate([m.get_vertex_buffer() for m in models])
        all_indices = np.concatenate([m.indices + i*len(m.vertices) for i, m in enumerate(models)])
        normalize = max(all_vertices.min(), all_vertices.max(), key=abs)*k
        normal_vector = np.array([normalize, normalize, normalize, 1, 1, 1])
        all_vertices = (all_vertices/normal_vector).astype(np.float32)

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
        glEnableVertexAttribArray(0)  # Позиция
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)  # Цвет
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
        
        self.model = {
            'VAO': VAO,
            'VBO': VBO,
            'EBO': EBO,
            'indices': all_indices,
        }
        
    def key_callback(self, window, key, scancode, action, mods):
        global rotation_x, rotation_y
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_UP:
                rotation_x -= 5
            elif key == glfw.KEY_DOWN:
                rotation_x += 5
            elif key == glfw.KEY_LEFT:
                rotation_y -= 5
            elif key == glfw.KEY_RIGHT:
                rotation_y += 5
            elif key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

    def render(self, camera_pos=(0, 0, -1), fov=60, near=0.01, far=2):
        """Основной цикл рендеринга"""
        global rotation_x, rotation_y
        rotation_x = 0
        rotation_y = 0
        glfw.set_key_callback(self.window, self.key_callback)

        while not glfw.window_should_close(self.window):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    
                    
            # Матрицы вида и проекции
            view = glm.translate(glm.mat4(1.0), glm.vec3(*camera_pos))
            projection = glm.perspective(glm.radians(fov), 
                                      8/6, near, far)
            
            #ПОМЕНЯТЬ
            # angleX = glfw.get_time()

            model_matrix = np.identity(4, dtype=np.float32)
            model_matrix = glm.scale(model_matrix, glm.vec3(1, 1, 1))
            model_matrix = glm.rotate(model_matrix, np.radians(rotation_x), glm.vec3(1.0, 0.0, 0.0))
            model_matrix = glm.rotate(model_matrix, np.radians(rotation_y), glm.vec3(0.0, 0.0, 0.1))
        
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
            #пусть все крутится
            glUniformMatrix4fv(
                glGetUniformLocation(self.shader, "model"), 
                1, GL_FALSE, 
                glm.value_ptr(model_matrix)
            )
            
            # Рендеринг всех моделей
            glBindVertexArray(self.model['VAO'])
            glDrawElements(
                GL_TRIANGLES, 
                len(self.model['indices']), 
                GL_UNSIGNED_INT, 
                None
            )
            glfw.swap_buffers(self.window)
            glfw.wait_events()  

            
    def cleanup(self):
        """Освобождение ресурсов"""
        glDeleteProgram(self.shader)
        
        glDeleteVertexArrays(1, [self.model['VAO']])
        glDeleteBuffers(1, [self.model['VBO']])
        glDeleteBuffers(1, [self.model['EBO']])
        glfw.terminate()