from okin.base.chem_logger import chem_logger
from re_add_modeler.utils.utils import get_newest_timestamp_folder
from re_add_modeler.gui_files.wgt_qtext_window import AdvancedSettingsWidget

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication, QAbstractItemView, QMessageBox, QHeaderView, QPushButton
from PySide6.QtCore import Qt, Signal

import json
import shutil
import os
import glob

#? This could be an abstract table class but this is so much easier.
class ModelTableWidget(QWidget):
    resized = Signal()
    new_sb_sgn = Signal(str)
    new_model_sgn = Signal(str)
    changed_m = Signal() # unused for now

    def __init__(self, fixed_height=215, button_width=None):
        super().__init__()
        self.logger = chem_logger.getChild(self.__class__.__name__)
        #! make this usalble self.cell_alignment = cell_alignment
        self.fixed_height = fixed_height
        self.selected_row = None
        self.num_row = 1
        self.mechs = {}
        self.v_button_width = button_width
        self.setup_folder()
        self.setup_ui()

    def setup_folder(self):
        self.work_folder = get_newest_timestamp_folder("./output")
        self.model_folder = os.path.join(self.work_folder, "models")
        self.logger.info(f"model folder = {self.model_folder}")
        self.time_course_folder = os.path.join(self.work_folder, "time_courses")

    def setup_ui(self):
        self.content_wgt = QWidget()
        content_layout = QVBoxLayout(self.content_wgt)

        # Create the table with an additional column for buttons
        self.table = QTableWidget(0, 2)  # "Mechansim name | button_edit"
        self.table.setHorizontalHeaderLabels(["model","View"])  # Add header for button column
        self.table.setRowCount(1)
        self.table.setFixedHeight(self.fixed_height)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)         # "model" expands
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # "View" as narrow as possible
        self.table.setAcceptDrops(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Connect signals
        self.table.itemSelectionChanged.connect(self.handle_item_selection)
        self.table.cellClicked.connect(self.update_clicked_row_content)
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # Set single selection mode
        content_layout.addWidget(self.table)
        layout = QVBoxLayout(self)
        layout.addWidget(self.content_wgt)
        self.populate_table()

        header_style = (
            "QHeaderView::section {"
            "    background-color: #333333;"  # Dark grey background color
            "    color: white;"               # White text color
            "}"
        )
        self.table.horizontalHeader().setStyleSheet(header_style)
        self.logger.debug("setup done")

    def handle_edit_event(self):
        # Define what happens when a button in the table is clicked
        button = self.sender()  # Get the clicked button
        row = self.table.indexAt(button.pos()).row()  # Get the row index of the clicked button
        m_name = self.table.item(row, 0).text()
        self.logger.info(f"{m_name = }")
        m_path = f"{self.model_folder}\\{m_name}\\model.json"
        self.m_edit_wgt = AdvancedSettingsWidget(settings_file=m_path, custom_file=m_path, title=f"model: {m_name}")
        self.open_edit_win(m_name)
        button.setStyleSheet("background-color: rgba(0, 255, 0, 0.3);")  # Red with 40% opacity

    def open_edit_win(self, m_name):
        #! only shows. Does not update sb string yet
        # prev_file_content = self._get_model_file_content(model_name=m_name, as_json=False)
        self.m_edit_wgt.open()
        # curr_file_content = self._get_model_file_content(model_name=m_name, as_json=False)

        # if prev_file_content != curr_file_content:
        #     self.changed_m.emit() #! unused

    def _get_model_file_content(self, model_name, as_json=False):
        m_path = f"{self.model_folder}\\{model_name}\\model.json"
        with open(m_path, "r") as f:
            if as_json:
                m_dict = json.load(f)
                return m_dict
            else:
                m_txt = f.read()
                return m_txt

    def _add_mech(self, m_name, m_steps):
        self.mechs[m_name] = m_steps
        self.logger.info(f"Updated {self.mechs = }")

    def populate_table(self):
        m_nareaddm = [path.split("\\")[-1] for path in glob.glob(f"{self.model_folder}\\*")]
        self.logger.info(f"{m_nareaddm = }")
        self.num_row = len(m_nareaddm)
        self.m_nareaddm = m_nareaddm
        self.row_dict = {}

        self.table.setRowCount(len(m_nareaddm))  # Ensure the correct number of rows
        for row, m_name in enumerate(m_nareaddm):
            # Set the model name in the first column
            item = QTableWidgetItem(m_name)
            self.table.setItem(row, 0, item)

            # Create and configure the Edit button
            button = QPushButton("View")
            if self.v_button_width:
                button.setFixedWidth(self.v_button_width)
            button.clicked.connect(self.handle_edit_event)

            # Place the button in the second column
            self.table.setCellWidget(row, 1, button)

            # add mech to self.mechs
            m_dict = self._get_model_file_content(model_name=m_name, as_json=True)
            self._add_mech(m_name=m_dict['name'], m_steps=m_dict['m_steps'])
            
    def handle_item_selection(self):
        selected_items = self.table.selectedItems()
        if len(selected_items) == 0:
            return

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                "Are you sure you want to delete the selected cell?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.delete_selected_cell()
        else:
            super().keyPressEvent(event)

    def delete_selected_cell(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        rows_to_remove = set()
        for item in selected_items:
            row = item.row()
            self.update_clicked_row_content(row)
            self.logger.info(f"selected row = {self.selected_row}")
            shutil.rmtree(f"{self.model_folder}\\{self.selected_row[0]}")
            rows_to_remove.add(row)
            # item.setText("")  # Clear the content of the selected cell

        # Remove entire rows that are empty after deleting cells
        for row in sorted(rows_to_remove, reverse=True):
            self.table.removeRow(row)
            
    def is_row_empty(self, row):
        num_columns = self.table.columnCount()
        for col in range(num_columns):
            item = self.table.item(row, col)
            if item is not None and item.text():
                return False
        return True

    def update_clicked_row_content(self, row) -> list:
        # send sb_string from model
        row_content = []
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item is not None:
                row_content.append(item.text())
            else:
                row_content.append(None)
        self.selected_row = row_content
        sb_string_path = f"{self.model_folder}\\{self.selected_row[0]}\\sb_string.txt"
        self.new_sb_sgn.emit(sb_string_path)
        # send model name´
        self.new_model_sgn.emit(self.selected_row[0])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()
        total_width = self.content_wgt.size().width() 
        self.table.setColumnWidth(0, total_width*0.74)  # 60%
        self.table.setColumnWidth(1, total_width*0.2)  # 40%
            
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = ModelTableWidget()
    widget.show()
    sys.exit(app.exec())
