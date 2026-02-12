import glfw
import numpy as np
from OpenGL.GL import *
import glm

# 1. ИСХОДНЫЕ ДАННЫЕ (как у вас)
# Координаты 8 вершин куба
coords = np.array([
    [-0.5, -0.5, -0.5],  # 0
    [ 0.5, -0.5, -0.5],  # 1
    [ 0.5,  0.5, -0.5],  # 2
    [-0.5,  0.5, -0.5],  # 3
    [-0.5, -0.5,  0.5],  # 4
    [ 0.5, -0.5,  0.5],  # 5
    [ 0.5,  0.5,  0.5],  # 6
    [-0.5,  0.5,  0.5]   # 7
], dtype=np.float32)

# Цвета для 8 вершин
colors = np.array([
    [1.0, 0.0, 0.0],  # 0 - красный
    [0.0, 1.0, 0.0],  # 1 - зеленый
    [0.0, 0.0, 1.0],  # 2 - синий
    [1.0, 1.0, 0.0],  # 3 - желтый
    [1.0, 0.0, 1.0],  # 4 - пурпурный
    [0.0, 1.0, 1.0],  # 5 - голубой
    [0.5, 0.5, 0.5],  # 6 - серый
    [1.0, 0.5, 0.0]   # 7 - оранжевый
], dtype=np.float32)

# Нормали для 6 граней
normals = np.array([
    [ 0.0,  0.0, -1.0],  # 0 - задняя
    [ 0.0,  0.0,  1.0],  # 1 - передняя
    [ 0.0, -1.0,  0.0],  # 2 - нижняя
    [ 0.0,  1.0,  0.0],  # 3 - верхняя
    [-1.0,  0.0,  0.0],  # 4 - левая
    [ 1.0,  0.0,  0.0]   # 5 - правая
], dtype=np.float32)

# Индексы вершин для 12 треугольников
coordIndex = np.array([
    # Задняя грань
    0, 1, 2, 2, 3, 0,
    # Передняя грань
    4, 5, 6, 6, 7, 4,
    # Нижняя грань
    0, 1, 5, 5, 4, 0,
    # Верхняя грань
    3, 2, 6, 6, 7, 3,
    # Левая грань
    0, 3, 7, 7, 4, 0,
    # Правая грань
    1, 2, 6, 6, 5, 1
], dtype=np.uint32)

# Индексы нормалей для треугольников (по граням)
normalIndex = np.array([
    # Задняя грань - нормаль 0
    0, 0, 0, 0, 0, 0,
    # Передняя грань - нормаль 1
    1, 1, 1, 1, 1, 1,
    # Нижняя грань - нормаль 2
    2, 2, 2, 2, 2, 2,
    # Верхняя грань - нормаль 3
    3, 3, 3, 3, 3, 3,
    # Левая грань - нормаль 4
    4, 4, 4, 4, 4, 4,
    # Правая грань - нормаль 5
    5, 5, 5, 5, 5, 5
], dtype=np.uint32)

# 2. ПОДГОТОВКА ДАННЫХ ДЛЯ EBO
def prepare_ebo_data(coords, colors, normals, coordIndex, normalIndex):
    """Подготавливает данные для использования с EBO"""
    
    # Создаем массивы для VBO
    num_vertices = len(coords)
    vertices = []
    
    # Просто объединяем координаты и цвета вершин
    # Нормали будут присоединены позже через EBO
    for i in range(num_vertices):
        vertices.extend(coords[i])   # x,y,z
        vertices.extend(colors[i])   # r,g,b
    
    vertices_array = np.array(vertices, dtype=np.float32)
    
    return vertices_array

# Альтернативный подход: создаем расширенные вершины с нормалями
def prepare_interleaved_with_normals(coords, colors, normals, coordIndex, normalIndex):
    """Создает VBO с нормалями, дублируя вершины для разных нормалей"""
    interleaved = []
    
    for i in range(len(coordIndex)):
        v_idx = coordIndex[i]      # индекс вершины
        n_idx = normalIndex[i]     # индекс нормали для этой вершины в треугольнике
        
        # Координаты вершины
        interleaved.extend(coords[v_idx])   # x,y,z
        # Цвет вершины
        interleaved.extend(colors[v_idx])   # r,g,b
        # Нормаль для этого треугольника
        interleaved.extend(normals[n_idx])  # nx,ny,nz
    
    return np.array(interleaved, dtype=np.float32)

# 3. ВАРИАНТ С EBO (Рекомендуемый)
def setup_with_ebo(coords, colors, normals, coordIndex, normalIndex):
    """
    Настройка с EBO:
    - VBO содержит только уникальные вершины (координаты + цвета)
    - EBO содержит индексы для треугольников
    - Отдельный VBO для нормалей (или их можно объединить с вершинами)
    """
    
    # A. СОЗДАЕМ VBO ДЛЯ ВЕРШИН (координаты + цвета)
    vertices = []
    for i in range(len(coords)):
        vertices.extend(coords[i])   # x,y,z
        vertices.extend(colors[i])   # r,g,b
    
    vertices_array = np.array(vertices, dtype=np.float32)
    
    # B. СОЗДАЕМ VBO ДЛЯ НОРМАЛЕЙ (индексированный доступ)
    # Нужно преобразовать normalIndex в массив нормалей для каждой вершины в треугольнике


    triangle_normals = []
    for n_idx in normalIndex:
        triangle_normals.extend(normals[n_idx])  # nx,ny,nz
    
    normals_array = np.array(triangle_normals, dtype=np.float32)
    
    # C. СОЗДАЕМ EBO С ИНДЕКСАМИ
    # В данном случае coordIndex уже содержит индексы вершин
    indices_array = coordIndex
    
    # Создаем буферы
    VAO = glGenVertexArrays(1)
    VBO_vertices = glGenBuffers(1)
    VBO_normals = glGenBuffers(1)
    EBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    
    # 1. VBO для вершин (координаты + цвета)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices_array.nbytes, vertices_array, GL_STATIC_DRAW)
    
    # Атрибуты для вершин
    # Позиции: location 0, 3 float, шаг 6*4=24 байта
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Цвета: location 1, 3 float, шаг 24 байта, смещение 12 байт
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    
    # 2. VBO для нормалей (отдельный буфер)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_normals)
    glBufferData(GL_ARRAY_BUFFER, normals_array.nbytes, normals_array, GL_STATIC_DRAW)
    
    # Нормали: location 2, 3 float, без шага (один к одному с индексами)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)
    
    # 3. EBO для индексов вершин
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_array.nbytes, indices_array, GL_STATIC_DRAW)
    
    # Отвязываем
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    return VAO, VBO_vertices, VBO_normals, EBO, len(indices_array)

# 4. АЛЬТЕРНАТИВА: ОДИН VBO С ВСЕМИ ДАННЫМИ + EBO
def setup_single_vbo_with_ebo(coords, colors, normals, coordIndex, normalIndex):
    """Более эффективный вариант: один VBO со всеми данными + EBO"""
    
    # Создаем массив вершин с нормалями
    vertex_data = []
    for i in range(len(coords)):
        vertex_data.extend(coords[i])   # x,y,z
        vertex_data.extend(colors[i])   # r,g,b
        # Нормаль пока не добавляем
    
    vertex_array = np.array(vertex_data, dtype=np.float32)
    
    # Создаем массив нормалей для каждой вершины в каждом треугольнике
    normals_for_triangles = []
    for n_idx in normalIndex:
        normals_for_triangles.extend(normals[n_idx])
    
    normals_array = np.array(normals_for_triangles, dtype=np.float32)
    
    # Создаем буферы
    VAO = glGenVertexArrays(1)
    VBO_vertex = glGenBuffers(1)
    VBO_normal = glGenBuffers(1)
    EBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    
    # VBO для вершин (координаты + цвета)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertex)
    glBufferData(GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, GL_STATIC_DRAW)
    
    stride = 6 * 4  # 6 значений * 4 байта
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)  # позиции
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)  # цвета
    
    # VBO для нормалей (instanced или отдельный)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_normal)
    glBufferData(GL_ARRAY_BUFFER, normals_array.nbytes, normals_array, GL_STATIC_DRAW)
    
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)  # нормали
    
    # EBO
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, coordIndex.nbytes, coordIndex, GL_STATIC_DRAW)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    return VAO, VBO_vertex, VBO_normal, EBO, len(coordIndex)

# 5. ОСНОВНАЯ ПРОГРАММА С EBO

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(800, 600, "Куб с EBO", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    
    # Настройка с EBO (выберите один из вариантов)
    VAO, VBO_v, VBO_n, EBO, index_count = setup_single_vbo_with_ebo(
        coords, colors, normals, coordIndex, normalIndex
    )
    
    # Шейдеры (такие же)
    vertex_shader = """
    #version 330 core
    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aColor;
    layout(location = 2) in vec3 aNormal;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    out vec3 FragPos;
    out vec3 VertexColor;
    out vec3 Normal;
    
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
    in vec3 VertexColor;
    in vec3 Normal;
    
    out vec4 FragColor;
    
    uniform vec3 lightPos;
    uniform vec3 lightColor;
    uniform vec3 viewPos;
    
    void main() {
        vec3 norm = normalize(Normal);
        vec3 lightDir = normalize(lightPos - FragPos);
        
        // Ambient
        float ambient = 0.2;
        
        // Diffuse
        float diff = max(dot(norm, lightDir), 0.0);
        
        // Specular
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        
        vec3 result = (ambient + diff + spec * 0.5) * lightColor * VertexColor;
        FragColor = vec4(result, 1.0);
    }
    """
    
    # Компиляция шейдеров
    def compile_shader(source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        return shader
    
    vertex = compile_shader(vertex_shader, GL_VERTEX_SHADER)
    fragment = compile_shader(fragment_shader, GL_FRAGMENT_SHADER)
    shader = glCreateProgram()
    glAttachShader(shader, vertex)
    glAttachShader(shader, fragment)
    glLinkProgram(shader)
    
    # Uniform locations
    model_loc = glGetUniformLocation(shader, "model")
    view_loc = glGetUniformLocation(shader, "view")
    proj_loc = glGetUniformLocation(shader, "projection")
    light_pos_loc = glGetUniformLocation(shader, "lightPos")
    light_color_loc = glGetUniformLocation(shader, "lightColor")
    view_pos_loc = glGetUniformLocation(shader, "viewPos")
    
    # Параметры сцены
    model = glm.mat4(1.0)
    view = glm.lookAt(glm.vec3(0, 0, 3), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45.0), 800/600, 0.1, 100.0)
    
    light_pos = glm.vec3(2.0, 2.0, 2.0)
    light_color = glm.vec3(1.0, 1.0, 1.0)
    view_pos = glm.vec3(0.0, 0.0, 3.0)
    
    angle = 0.0
    
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        angle += 1.0
        model = glm.rotate(glm.mat4(1.0), glm.radians(angle), glm.vec3(0, 1, 0))
        
        glUseProgram(shader)
        
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
        
        glUniform3f(light_pos_loc, light_pos.x, light_pos.y, light_pos.z)
        glUniform3f(light_color_loc, light_color.x, light_color.y, light_color.z)
        glUniform3f(view_pos_loc, view_pos.x, view_pos.y, view_pos.z)

# ОТРИСОВКА С EBO
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    # Очистка
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO_v])
    glDeleteBuffers(1, [VBO_n])
    glDeleteBuffers(1, [EBO])
    glDeleteProgram(shader)
    glfw.terminate()

if __name__ == "__main__":
    main()