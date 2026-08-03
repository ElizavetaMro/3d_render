from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter,  QTableWidgetItem, 
                             QToolBar, QLabel, QFrame, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QAction
from propertytab import PropertyTab
from readfile import DataLight
from render2 import OpenGLRenderWidget

import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Render Application")
        self.resize(1000, 900)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный горизонтальный layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем сплиттер - используем Qt.Orientation.Horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая часть - область рендера
        self.render_widget = OpenGLRenderWidget()
        self.render_widget.setStyleSheet("background-color: #2b2b2b; color: white;")

        self.render_widget.setMinimumWidth(500)
        
        # Правая часть - таблица
        self.table_widget = PropertyTab()
        self.table_widget.set_property()

        # Добавляем виджеты в сплиттер
        splitter.addWidget(self.render_widget)
        splitter.addWidget(self.table_widget)
        
        # Устанавливаем пропорции
        splitter.setSizes([530, 270])
        
        main_layout.addWidget(splitter)
        
        self.create_toolbar()        
    
    
    def create_toolbar(self):
        """Создание тулбара"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #3c3c3c;
                spacing: 3px;
                padding: 5px;
            }
            QToolButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 5px 10px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #5a5a5a;
            }
            QToolButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        
        file_action = QAction("📁 File", self)
        file_action.setStatusTip("Open file")
        file_action.triggered.connect(self.file_action_clicked)
        toolbar.addAction(file_action)
        
        toolbar.addSeparator()
        
        property_action = QAction("⚙️ Property", self)
        property_action.setStatusTip("Edit properties")
        property_action.triggered.connect(self.property_action_clicked)
        toolbar.addAction(property_action)
        
        toolbar.addSeparator()
        
        points_action = QAction("📍 Points", self)
        points_action.setStatusTip("Manage points")
        points_action.triggered.connect(self.points_action_clicked)
        toolbar.addAction(points_action)
        
        toolbar.addSeparator()
        
        calculate_action = QAction("🧮 Calculate", self)
        calculate_action.setStatusTip("Perform calculations")
        calculate_action.triggered.connect(self.calculate_action_clicked)
        toolbar.addAction(calculate_action)
        
        self.statusBar().showMessage("Ready")

    
    def file_action_clicked(self):
        self.statusBar().showMessage("Select file to open...")
        
        # Более простой и надежный способ
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            os.getcwd(),  # или os.path.expanduser("~")
            "All Files (*.*);;3D Models (*.obj *.stl *.fbx);;Images (*.png *.jpg)"
        )
        
        if file_path:
            self.current_file_path = file_path
            self.load_file(file_path)

    def load_file(self, file_path):
        self.data = DataLight(file_path)
        self.render_widget.load_models(self.data.model_list, k=2)



    def property_action_clicked(self):
        self.statusBar().showMessage("Property menu clicked - Edit object properties")
        print("Property action triggered")
    
    def points_action_clicked(self):
        self.statusBar().showMessage("Points menu clicked - Manage points")
        print("Points action triggered")
    
    def calculate_action_clicked(self):
        self.statusBar().showMessage("Calculating...")
        print("Calculate action triggered")
        
        row_count = self.table_widget.rowCount()
        for row in range(min(3, row_count)):
            current_value = self.table_widget.item(row, 1).text()
            try:
                if current_value.replace('.', '').replace('-', '').isdigit():
                    new_value = str(float(current_value) + 1)
                    self.table_widget.setItem(row, 1, QTableWidgetItem(new_value))
                    self.statusBar().showMessage(f"Updated value at row {row+1}")
            except ValueError:
                pass

    