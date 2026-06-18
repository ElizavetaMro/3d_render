from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow

app = QApplication([])

window = MainWindow() # по умолчанию скрыт
window.show()

app.exec() #запуск цикла событий
