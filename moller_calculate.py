from tkinter import filedialog, Tk
import time
from readfile import DataLight
import numpy as np
from sphere import Sphere

class Moller_Calculator():
    """Расчет расстояния прохождения луча через заданные объекты"""
    def __init__(self, sphere, file_path):
        self.data = DataLight(file_path)
        self.center = sphere.center
        self.directions = sphere.directions
        self.solutions = self.sphere_calculate()

    def ray_triangle_calculate(self, ray, triangle):
        """Проверка, что луч проходит через треугольник. 
        Если проходит возвращает значение t - расстояние от начала луча
        до точки пересечения треугольника"""
        y = self.center - triangle[0]
        A = np.array([-ray , triangle[1]- triangle[0], triangle[2]- triangle[0]]).T
        if np.linalg.det(A) != 0:
            X = np.linalg.solve(A, y)
            if (X[1] >= 0)&(X[2] >= 0)&(X[1]+X[2] < 1): return X[0]
            return None
        return None
    
    def ray_object_calculate(self, ray, model):
        vertices = model.t_vertices
        indeces = model.indices
        color = model.color
    

        x_solutions = []
        n_triangles = len(indeces)//3
        triangles = vertices[indeces].reshape(n_triangles, 3, 3)
        for triangle in triangles:
            x = self.ray_triangle_calculate( ray, triangle)
            if x: x_solutions.append(x)
        if len(x_solutions)==2:
            dx = np.abs(x_solutions[1]-x_solutions[0])
            print ("материал", color, "значение", dx)
        return (color, x_solutions)

    def ray_calculate(self, ray):
        ray_solutions = []
        for model in self.data.model_list:
            ray_solutions.append(self.ray_object_calculate(ray, model))
        return ray_solutions

    def sphere_calculate(self):
        sphere_solutions = []
        for ray in self.directions:
            sphere_solutions.append(self.ray_calculate(ray))
        return sphere_solutions


if __name__ == "__main__":
    
    def select_file():

        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Выберите WRL файл",
            filetypes=[("VRML files", "*.wrl")]
        )
        return file_path

    file_path = select_file()
    sphere = Sphere(center=(0.0, 0.0, 0.1), rays_count=12)
    calculator = Moller_Calculator(sphere, file_path)
    calculator.sphere_calculate