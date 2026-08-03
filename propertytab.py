from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTableWidget, QTableWidgetItem, 
                             QToolBar, QApplication, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QAction

class PropertyTab(QTableWidget):
    def __init__(self):
        super().__init__()
    
    def set_property(self):
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Property", "Value", "Status"])
    # Настройка таблицы
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #f5f5f5;
                alternate-background-color: #e8e8e8;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #4a4a4a;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        
        self.populate_table()
    
    def populate_table(self):
        """Заполнение таблицы тестовыми данными"""
        sample_data = [
            ["Position X", "0.0", "Active"],
            ["Position Y", "0.0", "Active"],
            ["Position Z", "0.0", "Active"],
            ["Rotation X", "0°", "Pending"],
            ["Rotation Y", "0°", "Pending"],
            ["Rotation Z", "0°", "Pending"],
            ["Scale X", "1.0", "Active"],
            ["Scale Y", "1.0", "Active"],
            ["Scale Z", "1.0", "Active"],
            ["Material", "Default", "Loaded"],
            ["Texture", "None", "Missing"],
            ["Lighting", "Enabled", "Active"]
        ]
        
        self.setRowCount(len(sample_data))
        
        for row, (prop, value, status) in enumerate(sample_data):
            self.setItem(row, 0, QTableWidgetItem(prop))
            self.setItem(row, 1, QTableWidgetItem(value))
            
            status_item = QTableWidgetItem(status)
            if status == "Active":
                status_item.setBackground(QColor(200, 255, 200))
            elif status == "Pending":
                status_item.setBackground(QColor(255, 255, 200))
            elif status == "Missing":
                status_item.setBackground(QColor(255, 200, 200))
            elif status == "Loaded":
                status_item.setBackground(QColor(200, 200, 255))
                
            self.setItem(row, 2, status_item)
        
        self.resizeColumnsToContents()