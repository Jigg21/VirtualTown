import sys
import random
from typing import Optional
from PySide6 import QtCore, QtWidgets, QtGui
import PySide6.QtCore
import PySide6.QtWidgets

class ShipWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.hello = ["Hallo Welt!","Hei maailma", "Hello World!"]
        self.button = QtWidgets.QPushButton("Refresh")
        self.text = QtWidgets.QLabel("Hello World!", alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.update)

        self.dictDisplay = dictDisplay()
        self.layout.addWidget(self.dictDisplay)

    
    def update(self,context):
        pass

class ListDisplay(QtWidgets.QWidget):
    def __init__(self,commaSeparated = False) -> None:
        super().__init__()
        self.text = QtWidgets.QLabel("List Display",alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.commaSeparated = commaSeparated   

    def update(self,newList):
        result = ""
        if type(newList) == list:
            for item in newList:
                result += item
                if newList.index(item) < len(newList) -1:
                    if self.commaSeparated:
                        result += ", "
                    else:
                        result += "\n"
        else:
            result = item 
        
        self.text.setText(result)

class dictDisplay(QtWidgets.QWidget):
    def __init__(self,commaSeparated = False) -> None:
        super().__init__()
        self.text = QtWidgets.QLabel("Dict Display",alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.commaSeparated = commaSeparated
    
    def update(self,newDict):
        result = ""
        for item in newDict.keys():
            result += "{Key} : {Val} ".format(Key=item,Val=newDict[item])
            if self.commaSeparated -1:
                if self.commaSeparated:
                    result += ", "
                else:
                    result += "\n"
        self.text.setText(result)

class ListMarquee(QtWidgets.QWidget):
    def __init__(self,width = 100,speed = 1,commaSeparated = False) -> None:
        super().__init__()
        self.text = QtWidgets.QLabel("List Marquee",alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.commaSeparated = commaSeparated
        self.width = width
        self.speed = speed
        self.idx = 0
    
    def update(self,newList):
        for val in newList:
            pass

    def progress(self):
        self.idx += 1
        if self.idx > self.width:
            self.idx = 0


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = ShipWindow()
    widget.resize(800,600)
    widget.show()
    sys.exit(app.exec())