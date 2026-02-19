from render import ModelRenderer
# from model import Model
from readfile import DataLight
# import glfw
import time

start_time = time.time()
# Создаем рендерер
renderer = ModelRenderer()
data = DataLight("wrls\\meteor2526111.wrl")#("wrls\\aabb_tests.wrl")#("wrls\\кубхкубхкуб 2мм.wrl")

renderer.load_models(data.model_list, k=2)

end_time = time.time()
execution_time = end_time-start_time
print(f"{execution_time:.4f}")
# Запускаем рендеринг

try:
    renderer.render()
finally:
    renderer.cleanup()
