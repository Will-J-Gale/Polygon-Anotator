import sys
from libs.MainWindow import Window
from PyQt5.QtWidgets import QApplication

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_()) 

if __name__ == "__main__":
    run()