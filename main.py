from render import ModelRenderer
from readfile import DataLight
from tkinter import filedialog, Tk
import time

def select_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Выберите WRL файл",
        filetypes=[("VRML files", "*.wrl")]
    )
    return file_path

start_time = time.time()
# Создаем рендерер
file_path = select_file()
print(file_path)
renderer = ModelRenderer()
if file_path:
    data = DataLight(file_path)

renderer.load_models(data.model_list, k=2)

# renderer.add_sphere(
#     center=(0.0, 0.0, 0.1),  # Координата точки
#     radius=1.0,               # Длина лучей
#     rays_count=360,            # Количество лучей (36-144 оптимально)
#     color=(1.0, 0.0, 0.0)     # Красный цвет
# )

end_time = time.time()
execution_time = end_time-start_time
print(f"{execution_time:.4f}")
# Запускаем рендеринг

try:
    renderer.render()
finally:
    renderer.cleanup()
