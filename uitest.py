import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class Switch(QCheckBox):
    def __init__(self, parent=None):
        super(Switch, self).__init__(parent)
        self.setFixedSize(60, 30)
        self.setStyleSheet('''
            QCheckBox {
                background-color: #ccc;
                border-radius: 15px;
                border: 2px solid #ccc;
                width: 60px;
                height: 30px;
                padding: 0;
                margin: 0;
            }
            QCheckBox::indicator {
                width: 26px;
                height: 26px;
                border-radius: 13px;
                background-color: white;
                position: absolute;
                left: 1px;
                top: 1px;
                transition: all .3s;
            }
            QCheckBox::indicator:checked {
                left: 32px;
            }
            QCheckBox:checked {
                background-color: #66bb6a;
                border: 2px solid #66bb6a;
            }
        ''')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Switch Example")
        self.setFixedSize(300, 200)

        switch = Switch()

        layout = QVBoxLayout()
        layout.addWidget(switch)
        layout.setAlignment(switch, Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
