from render import ModelRenderer
# from model import Model
from readfile import Data
# import glfw
import time

start_time = time.time()
# Создаем рендерер
renderer = ModelRenderer()
data = Data("wrls\\aabb_tests.wrl")#("wrls\\aabb_tests.wrl")#("wrls\\кубхкубхкуб 2мм.wrl")


renderer.load_models(data.model_list, k=2)

end_time = time.time()
execution_time = end_time-start_time
print(f"{execution_time:.4f}")
# Запускаем рендеринг

try:
    renderer.render()
finally:
    renderer.cleanup()
