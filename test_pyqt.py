import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

def main():
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Test PyQt5 App")
    window.setGeometry(100, 100, 300, 200)
    
    label = QLabel("Hello, PyQt5!", parent=window)
    label.move(100, 80)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()