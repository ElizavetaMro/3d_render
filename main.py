from render import ModelRenderer
# from model import Model
from readfile import Data
# import glfw

# Создаем рендерер
renderer = ModelRenderer()
data = Data("wrls\\Example2.0.wrl")#("wrls\\aabb_tests.wrl")#("wrls\\кубхкубхкуб 2мм.wrl")

for model in data.model_list:

    renderer.load_model(model.get_vertex_buffer(), model.indices, data.max_coord*5)

    
# Запускаем рендеринг
try:
    renderer.render()
finally:
    renderer.cleanup()