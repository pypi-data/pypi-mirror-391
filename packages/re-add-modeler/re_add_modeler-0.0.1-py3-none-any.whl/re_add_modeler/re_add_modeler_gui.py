from re_add_modeler.gui_files.window_data import DataWindow
from re_add_modeler.gui_files.window_model import ModelWindow
from re_add_modeler.gui_files.window_results import ResultsWindow
from okin.base.chem_logger import chem_logger

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedLayout, QWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

import sys

class ReAddModelerGUI(QMainWindow):
    data_to_model_sgn = Signal()
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mechanistic Solver")
        self.toolbar = self.addToolBar("Selection")
        self.stacked_layout = QStackedLayout()
        central_widget = QWidget()
        central_widget.setMinimumSize(400, 600)
        central_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(central_widget)
        self.setup_menu()
        self.create_actions()
        self.setup_tabs()
        self.setup_connections()

    def create_actions(self):
        self.actions = {
            "Data": self.show_data_layout,
            "Model": self.show_model_layout,
            "Results": self.show_results_layout,
            # "Planning": self.show_planning_layout,
            # "Math": self.show_math_layout
        }

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        # Create actions for the "File" menu
        save_action = QAction("Save", self)
        load_action = QAction("Load", self)
        quit_action = QAction("Quit", self)

        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        file_menu.addAction(quit_action)

    def setup_tabs(self):
        data_tab = DataWindow()
        model_tab = ModelWindow()
        result_tab = ResultsWindow()
        
        data_tab.setup_ui()
        model_tab.setup_ui()

        self.stacked_layout.addWidget(data_tab)       
        self.stacked_layout.addWidget(model_tab)
        self.stacked_layout.addWidget(result_tab)

        data_tab.added_model_sgn.connect(model_tab.populate_lyt)
        model_tab.copasi_complete_sgn.connect(result_tab.setup_ui)


    def setup_connections(self):
        for action_text, action_method in self.actions.items():
            action = QAction(action_text, self)
            action.triggered.connect(action_method)
            self.toolbar.addAction(action)

    def show_data_layout(self):
        self.setWindowTitle("Data")
        self.stacked_layout.setCurrentIndex(0)

    def show_model_layout(self):
        self.setWindowTitle("Model")
        self.stacked_layout.setCurrentIndex(1)

    def show_results_layout(self):
        self.setWindowTitle("Results")
        self.stacked_layout.setCurrentIndex(2)

    def show_planning_layout(self):
        self.setWindowTitle("Planning")
        self.stacked_layout.setCurrentIndex(3)

    def show_math_layout(self):
        self.setWindowTitle("Math")
        self.stacked_layout.setCurrentIndex(5)

    def quit_app(self):
        self.app.quit()
 
    def save_current_layout(self):
        print("I should save here but i dont")
        pass

    def load_current_layout(self):
        print("I should load here but i dont")



# this should go into the main.py
app = QApplication(sys.argv)
window = ReAddModelerGUI(app)
window.resize(1200, 850)
window.show()
sys.exit(app.exec())