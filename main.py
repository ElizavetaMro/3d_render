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

end_time = time.time()
execution_time = end_time-start_time
print(f"{execution_time:.4f}")
# Запускаем рендеринг

try:
    renderer.render()
finally:
    renderer.cleanup()
