from okin.base.chem_logger import chem_logger
from re_add_modeler.utils.convert_to_df import load_file_to_df

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication, QPushButton, QDialog, QFileDialog, QFormLayout, QComboBox, QLineEdit, QDialogButtonBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from PySide6.QtWidgets import QAbstractItemView

from PySide6.QtWidgets import QHeaderView
import pandas as pd
import os
import shutil
import json

class CSVWidget(QWidget):
    resized = Signal()
    new_csv_sgn = Signal(str)
    VALID_FILE_EXTENSIONS = [".csv", ".txt"] # add  ".xlsx", "xls"
    MAGIC_TABLE_PADDING = 0
    SELECTION_DICT = {"single": QTableWidget.SingleSelection, "multi":QTableWidget.ExtendedSelection}

    def __init__(self, table_list, csv_folder=None, fixed_height=215, num_row=1, add_buttons=True, allow_edit=True, selection_mode='single', minimum_width=300):
        super().__init__() 
        self.logger = chem_logger.getChild(self.__class__.__name__)
        assert not (allow_edit and not csv_folder), "If you want to add csvs you have to set the csv_folder."
        self.csv_folder = csv_folder 
        self.fixed_height = fixed_height
        self.table_list = table_list
        self.num_row = num_row
        self.selected_row = None
        self.add_buttons = add_buttons
        self.allow_edit = allow_edit
        self.selection_mode = selection_mode
        self.event_index = 0
        self.df_to_name = {} # {base_path: abs_path}
        self.df_dict = {} # "{path: df}"
        self.json_re_adds = None
        self.minimum_width = minimum_width
        self.setup_ui()

    def setup_ui(self):
        # self.resize(600, 800)
        self.content_wgt = QWidget()
        self.content_wgt.setMinimumWidth(self.minimum_width)
        content_layout = QVBoxLayout(self.content_wgt)
        
        # Create the table with an additional column for buttons
        header_nr = len(self.table_list) if not self.add_buttons else len(self.table_list) + 1
        header = [item["name"] for item in self.table_list]
        if self.add_buttons:
            header += ["Set Addition"]
        self.table = QTableWidget(0, header_nr)  # Add 1 column for buttons
        self.table.setHorizontalHeaderLabels(header)  # Add header for button column
        self.table.setRowCount(self.num_row)
        self.table.setFixedHeight(215)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # First column (index 0) will expand
        header.setSectionResizeMode(len(self.table_list), QHeaderView.Fixed)  # Button column will remain fixed

        # Enable drag and drop
        self.table.setAcceptDrops(True)
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.dragEnterEvent = self.dragEnterEvent
        self.table.dragMoveEvent = self.dragMoveEvent
        self.table.dropEvent = self.dropEvent
        self.table.setFixedHeight(self.fixed_height)

        if not self.allow_edit:
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        if self.add_buttons:
            self.re_additions = [] # list of dict
            # Structure of re-adds
            #* ohh my god.
            """
            #* list of all re additions for all files
            [
                #* file one
                    {
                        './src/readdm/output/2025-09-28_15-25-02/time_courses/A08_data_.csv':
                    #* re_additions for that file. which can contain multiple species per re-add
                        [ 
                            [{'species': 'A', 'rct_volume_ml': 100.0, 'added_vol_ml': 5.0, 'mmol': 50.0, 'time': '298.56'}],
                            [{'species': 'cat', 'rct_volume_ml': 110.0, 'added_vol_ml': 10.0, 'mmol': 10.0, 'time': '994.19'}, {'species': 'B', 'rct_volume_ml': 110.0, 'added_vol_ml': 0.0, 'mmol': 70.0, 'time': '994.19'}, {'species': 'A', 'rct_volume_ml': 110.0, 'added_vol_ml': 0.0, 'mmol': 80.0, 'time': '994.19']
                                    ]
                    },
                    
                #* file two
                {name_of_time_course_csv: [ [{re_add1, …}], [{re_add3} …] ]

            ]
            """
            self.add_buttons_to_table()

        # Connect signals
        self.table.itemSelectionChanged.connect(self.handle_item_selection)
        self.table.cellClicked.connect(self.get_clicked_row_content)
        self.table.setSelectionMode(self.SELECTION_DICT[self.selection_mode]) 

        content_layout.addWidget(self.table)
        layout = QVBoxLayout(self)
        layout.addWidget(self.content_wgt)

        header_style = (
            "QHeaderView::section {"
            "    background-color: #333333;"  # Dark grey background color
            "    color: white;"               # White text color
            "}"
        )
        self.table.horizontalHeader().setStyleSheet(header_style)
        self.logger.debug("setup done")
        self.table.cellChanged.connect(self.check_last_row_empty)

    def add_buttons_to_table(self):
        # Add a QPushButton to the last column for each row
        for row in range(self.num_row):
            button = QPushButton("Addition")
            button.clicked.connect(self.add_addition_event)
            button.setFixedWidth(100)
            self.table.setCellWidget(row, len(self.table_list), button)

    def add_addition_event(self):
        # Define what happens when a button in the table is clicked
        button = self.sender()  # Get the clicked button
        row = self.table.indexAt(button.pos()).row()  # Get the row index of the clicked button

        # Get text of the first column
        csv_name = self.table.item(row, 0).text()
        full_path = self.df_to_name[csv_name]
        
        # Open the input dialog window
        re_additions_new = self.open_addition_dialog(full_path)
        self.re_additions.append(re_additions_new)        
        button.setStyleSheet("background-color: rgba(0, 255, 0, 0.3);")  # Red with 40% opacity

    def get_re_additions(self):
        return self.re_additions.copy()
    
    def read_json_read(self):
        file_path, _ = QFileDialog.getOpenFileName(self, # parent
            "Select JSON File",
            "",
            "JSON Files (*.json)"  # filter for .json
        )
        if file_path:
            self.logger.info(f"Selected JSON file: {file_path}")
            with open(file_path, "r") as f:
                re_adds = json.load(f)
            self.json_re_adds = re_adds
        
    def open_addition_dialog(self, full_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("Addition Form")
        # Create layout for the form
        form_layout = QFormLayout()
        rct_volume_input = QLineEdit()
        rct_volume_input.setText("10")
        form_layout.addRow("Rct Volume:", rct_volume_input)

        # Create species dropdown (ComboBox)
        df = self.df_dict[full_path]
        available_species = [s for s in df.columns if s!="time"]
        species_combobox = QComboBox()
        species_combobox.addItems(available_species)  # Add your species options
        form_layout.addRow("Species:", species_combobox)

        # Create volume text input
        volume_input = QLineEdit()
        volume_input.setText("2")
        form_layout.addRow("Added Volume:", volume_input)

        # Create mmol text input
        mmol_input = QLineEdit()
        mmol_input.setText("1")
        form_layout.addRow("mmol:", mmol_input)

        # Create time text input
        time_input = QLineEdit()
        time_input.setText("5000")
        form_layout.addRow("Time:", time_input)

        # Create the dialog buttons (OK, Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        from_json_btn = QPushButton("From JSON")
        from_json_btn.clicked.connect(self.read_json_read)
        button_box.addButton(from_json_btn, QDialogButtonBox.ActionRole)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        if dialog.exec_() == QDialog.Accepted:
            # If JSON was loaded, return it
            if self.json_re_adds is not None:
                re_adds_raw = self.json_re_adds.copy()
                # Fix volureaddm if multiple re-adds at once
                for ra_event in re_adds_raw:
                    if len(ra_event) > 1:
                        total_volume = sum(float(ra["added_vol_ml"]) for ra in ra_event)
                        # First entry gets the sum of all volureaddm
                        ra_event[0]["added_vol_ml"] = total_volume
                        # All others get 0
                        for ra in ra_event[1:]:
                            ra["added_vol_ml"] = 0.0
                    self.event_index += 1 # outside of loop so multi additions have the same index
                    for i in range(len(ra_event)):
                        ra_event[i]["event_index"] = self.event_index
                re_adds = {full_path: re_adds_raw} # list(dict) of every info for one file
            else:
                # Otherwise, process form input
                rct_volume = float(rct_volume_input.text())
                species = species_combobox.currentText()
                volume = float(volume_input.text())
                mmol = float(mmol_input.text())
                time = float(time_input.text())
                dilution_factor = round(rct_volume / (rct_volume + volume), 2)

                self.event_index += 1
                re_add_raw = [{
                    "species": species,
                    "rct_volume": rct_volume,
                    "add_volume": volume,
                    "mmol": mmol,
                    "time": time,
                    "dilution_factor": dilution_factor,
                    "event_index": self.event_index
                }]
                re_adds = {full_path: re_add_raw} 
            return re_adds
        else:
            self.logger.info("Dialog was canceled.")

    def check_last_row_empty(self):
        if not self.is_last_row_empty():
            self.table.setRowCount(self.table.rowCount() + 1)
        self.num_row = self.table.rowCount()

    def get_row_as_dict(self, row):
        row_dict = {}
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col)
            key = header.text() if header is not None else f"Column {col}"
            item = self.table.item(row, col)
            value = item.text() if item is not None else ""
            row_dict[key] = value
        return row_dict

    def handle_item_selection(self):
        selected_items = self.table.selectedItems()
        self.selected_items = pd.DataFrame([self.get_row_as_dict(item.row()) for item in selected_items])
        self.logger.info(f"selected items = {self.selected_items}")

    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(1)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
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
            if self.is_row_empty(row):
                rows_to_remove.add(row)
            else:
                item.setText("")  # Clear the content of the selected cell

        # Remove entire rows that are empty after deleting cells
        for row in sorted(rows_to_remove, reverse=True):
            self.table.removeRow(row)
            # remove the csv from the dfs
            csv_path_to_remove = self.table.item(row, 0).text() if self.table.item(row, 0) else None
            del self.df_dict[csv_path_to_remove]

    def is_row_empty(self, row):
        num_columns = self.table.columnCount()
        for col in range(num_columns):
            item = self.table.item(row, col)
            if item is not None and item.text():
                return False
        return True

    def is_last_row_empty(self):
        last_row = self.table.rowCount() - 1
        for col in range(self.table.columnCount()):
            item = self.table.item(last_row, col)
            if item and item.text():
                return False
        return True

    def get_clicked_row_content(self, row, column) -> list:
        # Retrieve the content of the clicked row
        row_content = []
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item is not None:
                row_content.append(item.text())
            else:
                row_content.append(None)
        self.selected_row = row_content
        true_path = self.df_to_name[row_content[0]]
        self.new_csv_sgn.emit(true_path)
        self.logger.debug(f"selected_row = {self.selected_row}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()
        total_width = self.content_wgt.size().width() - self.MAGIC_TABLE_PADDING
        for i, col in enumerate(self.table_list):
            col_width = col["width_%"] * total_width
            self.table.setColumnWidth(i, col_width)
            
    def dragMoveEvent(self, event: QDragMoveEvent):
        return

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_extension = os.path.splitext(file_path)[1]
            
            if file_extension not in self.VALID_FILE_EXTENSIONS:
                continue
            self.add_file(file_path=file_path)

    def add_file(self, file_path):
        file_name = os.path.basename(file_path)
        column = 0
        # Check if the file path is already present in the column
        already_present = any(
            self.table.item(row, column).text() == file_name
            for row in range(self.table.rowCount())
            if self.table.item(row, column) is not None
        )
        if already_present:
            self.logger.error(f"File already exists: {file_path}")
            return

        try:
            # ignore already processed files relevant for window_model.test/train_csv
            if not file_name.endswith("data_.csv"):
                csv_path = f"{self.csv_folder}/{file_name[:-4]}_data_.csv"
                shutil.copy(src=file_path, dst=csv_path)
                print(f"copied:\n{file_path}\n{csv_path}")
            else:
                csv_path = f"{self.csv_folder}/{file_name[:-4]}.csv"
           
            # remove file again if not same header (excluding 'event*' columns)
            df = load_file_to_df(file_path=csv_path)
            if self.df_dict:
                existing_columns = [col for col in list(self.df_dict.values())[0].columns if not col.startswith('event')]
                new_columns = [col for col in df.columns if not col.startswith('event')]
                if existing_columns != new_columns:
                    os.remove(csv_path)
                    self.logger.error("NO. Not same header (excluding event columns)")
                    return
            self.df_to_name[file_name] = csv_path
            self.df_dict[csv_path] = df

        except Exception as e:
            self.logger.error(f"Data could not be read because: {e}")
        
        # Find the first empty cell in the column
        for row in range(self.table.rowCount()):
            if self.table.item(row, column) is None:
                self.table.setItem(row, column, QTableWidgetItem(file_name))
                break
    
        # select a file if nothing is selected
        if not self.selected_row and self.selection_mode=="single":
            last_added_item = self.table.item(row, column)
            self.get_clicked_row_content(row=row, column=column)
            self.table.setCurrentItem(last_added_item)
    
    def get_df(self):
        # thank you chatGPT
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
        df = pd.DataFrame(columns=headers)
        self.logger.debug(f"created df with headers: {headers}")

        for row in range(self.table.rowCount()):
            row_data = []

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append(None)
            if not any(row_data):
                continue
            df.loc[len(df)] = row_data
        self.logger.debug(f"df has {len(df)} rows of valid data")
        return df  

    def set_dfs(self, csv_list):
        # clear layout
        self.table.clearContents()
        self.table.setRowCount(len(csv_list))

        # populate layout
        for row_idx, csv_path in enumerate(csv_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(csv_path))
            try:
                df = load_file_to_df(file_path=csv_path)
                self.df_dict[csv_path] = df
            except Exception as e:
                self.logger.warning(f"Data could not be read because: {e}")
    
    def add_event_index_to_all(self):
        all_filenareaddm = [os.path.basename(p) for p in self.df_dict.keys()]
        data_csv_index = 0
        # Add a column for each file
        for csv_path, df in self.df_dict.items():
            data_csv_index += 1
            filename = os.path.basename(csv_path)
            for other_filename in all_filenareaddm:
                col_name = f"event_{data_csv_index}"
                df[col_name] = 1 if filename == other_filename else 0
            df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    table_list = [{"name": "csv_file", "width_%": 0.7, "enable_dragdrop": True}]
    widget = CSVWidget(table_list)
    widget.show()
    sys.exit(app.exec())
