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