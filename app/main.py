from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import sys
import os
from to_json import first, move

selecteditem, itemname, foldername = "", "", ""

class MainWindow(QtWidgets.QDialog):
    global selecteditem, itemname, foldername
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "gui.ui"), self)

        self.browse.clicked.connect(self.browsefiles)
        self.browse_folder.clicked.connect(self.browsefolder)
        #there is a combobox in the gui.ui file, but I don't know how to access it
        self.add_to_combo()
        self.comboBox.currentIndexChanged.connect(self.print_selected_item)
        

    def browsefiles(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.', '.png files (*.png)')
        self.filename.setText(filename[0])
        print(filename[0])
        itemname = filename[0]

    
    def browsefolder(self):
        foldername = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder', '.')
        self.packname.setText(foldername)
        print(foldername)

    def add_to_combo(self):
        #open item-list.txt and add everry item to the combobox, seperated with a ; in the file
        with open(os.path.join(os.path.dirname(__file__), "item-list.txt"), 'r') as file:
            items = file.read().split(';')
            for item in items:
                self.comboBox.addItem(item)
    
    # print the selected item in the combobox
    def print_selected_item(self):
        selecteditem = self.comboBox.currentText()
        print(first(selecteditem))


app = QApplication(sys.argv)
mainwindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle('Resourcepack Editing')
icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "pack.png"))
widget.setWindowIcon(icon)
widget.setFixedWidth(300)
widget.setFixedHeight(200)
widget.show()
sys.exit(app.exec_())
