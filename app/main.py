from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
import sys
import os
from to_json import first, move_texture, create_model, edit_or_create

class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "gui.ui"), self)
        
        # Initialize instance variables
        self.itemname = ""
        self.foldername = ""
        self.selected_item = ""

        # Connect buttons to their respective functions
        self.browse.clicked.connect(self.browsefiles)
        self.browse_folder.clicked.connect(self.browsefolder)
        
        # Connect the combobox selection change event
        self.comboBox.currentIndexChanged.connect(self.print_selected_item)
        
        # Connect the send button click event
        self.send_button.clicked.connect(self.send_data)
        
        # Add items to the combobox
        self.add_to_combo()

    def browsefiles(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.', 'PNG files (*.png)')
        if filename:
            self.filename.setText(filename)
            self.itemname = filename

    def browsefolder(self):
        foldername = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder', '.')
        if foldername:
            self.packname.setText(foldername)
            self.foldername = foldername

    def add_to_combo(self):
        # Open item-list.txt and add every item to the combobox, separated with a ; in the file
        with open(os.path.join(os.path.dirname(__file__), "item-list.txt"), 'r') as file:
            items = file.read().split(';')
            for item in items:
                self.comboBox.addItem(item)

    # Print the selected item in the combobox
    def print_selected_item(self):
        self.selected_item = self.comboBox.currentText()
        first(self.selected_item)  # Assuming first() does some processing

    def send_data(self):
        if self.itemname and self.foldername and self.selected_item:
            move_texture(self.itemname, self.foldername)
            create_model(self.itemname, self.foldername)
            edit_or_create(self.selected_item, self.itemname, self.foldername)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a file, a folder, and an item.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setWindowTitle('Resourcepack Editing')
    icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "pack.png"))
    widget.setWindowIcon(icon)
    widget.setFixedWidth(310)
    widget.setFixedHeight(200)
    widget.show()
    sys.exit(app.exec())
