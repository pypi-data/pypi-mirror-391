from okin.base.chem_logger import chem_logger
from okin.base.chem_plot_utils import apply_acs_layout_ax
from re_add_modeler.utils.utils import get_newest_timestamp_folder
from okin.simulation.simulator import Simulator
from re_add_modeler.gui_files.wgt_reactions import ReactionWidget
from re_add_modeler.gui_files.wgt_table import CSVWidget
from re_add_modeler.gui_files.wgt_m_table import ModelTableWidget

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox

import json
import os
import sys
import pandas as pd
import glob
import re
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
matplotlib.use("QtAgg")  # Ensure a Qt backend
matplotlib.rcParams['backend'] = 'QtAgg'

class ResultsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = chem_logger.getChild(self.__class__.__name__)
        self.data = None
        self.species_to_checkbox = {}
        self.setup_folders()
        self.setWindowTitle("Results")
        
    def setup_folders(self):
        # self.work_folder = get_newest_timestamp_folder("./src/readdm/output")
        self.work_folder = get_newest_timestamp_folder("./output")
        self.model_folder = os.path.join(self.work_folder, "models")
        self.time_course_folder = os.path.join(self.work_folder, "time_courses")

    def fill_file_tbl(self):
        self.logger.info("Filling file table")
        csvs = glob.glob(f"{self.time_course_folder}/*.csv")
        for c in csvs:
            self.file_csv_wgt.add_file(c)
        
        self.file_csv_wgt.table.selectRow(0)
        files = self.file_csv_wgt.get_df()
        first_csv = os.path.join(self.time_course_folder, files.loc[0].iloc[0])
        self.load_csv(first_csv)
        # self.file_csv_wgt.set_dfs(csvs)

    def fill_rct_wgt(self, mech_name):
        mech_file = os.path.join(self.model_folder, mech_name, "model.json")
        with open(mech_file, "r") as mf:
            model = json.load(mf)
        rcts = model["m_steps"]
        self.rct_wgt.set_reactions(rct_list=rcts)
          
    def parse_k_result(self, mech_name):
        k_dict_file = os.path.join(self.model_folder, mech_name, "k_result.csv")
        k_results = pd.read_csv(k_dict_file)
        best_result = k_results.loc[0]
        best_err = best_result["RSS"]
        best_k_dict = best_result.drop(columns=["RSS"])
        return best_k_dict.to_dict(), best_err
        
    def setup_ui(self):
        container = QWidget()
        main_lyt = QVBoxLayout(container)  # vertical: top row, bottom row
        input_height = 270

        #* --- Top row (rct_wgt + model table + file_csv_wgt) ---
        top_row = QHBoxLayout()

        self.ms_tbl = ModelTableWidget(fixed_height=input_height, button_width=50)
        self.ms_tbl.new_model_sgn.connect(self.on_new_model)
        self.ms_tbl.table.selectRow(0)
       
        train_table_list = [{"name": "training files", "width_%": -1, "enable_dragdrop": False}]
        self.file_csv_wgt = CSVWidget(
            table_list=train_table_list,
            add_buttons=False,
            allow_edit=False,
            fixed_height=input_height,
            csv_folder=self.time_course_folder,
            selection_mode="multi",
            minimum_width=200
        )
        self.file_csv_wgt.new_csv_sgn.connect(self.load_csv)
        self.rct_wgt = ReactionWidget(num_rct=5, fixed_height=input_height-40, add_button=False)
        first_model_item = self.ms_tbl.table.item(0, 0)  # assuming column 0 holds the name
        mech_name = first_model_item.text()
        self.ms_tbl.new_model_sgn.emit(mech_name)  # manually emit the signal

        # put top_row into a QWidget to enforce fixed height
        top_row.addWidget(self.ms_tbl, stretch=4)
        top_row.addWidget(self.file_csv_wgt, stretch=1)
        top_row.addWidget(self.rct_wgt, stretch=8)
        top_container = QWidget()
        top_container.setLayout(top_row)
        top_container.setFixedHeight(input_height)  # <-- lock height here
        main_lyt.addWidget(top_container)
        
        #* --- Bottom row (canvas + optional side widgets) ---
        bottom_row = QVBoxLayout()
        self.selection_lyt = QHBoxLayout()
        bottom_row.addLayout(self.selection_lyt)
        self.setup_plot()
        file_input_lyt = QVBoxLayout()
       
        bottom_row.addWidget(self.canvas)  # give canvas more room
        bottom_row.addLayout(file_input_lyt)
        bottom_container = QWidget()
        bottom_container.setLayout(bottom_row)
        main_lyt.addWidget(bottom_container)

        self.setCentralWidget(container)
        self.fill_file_tbl()
        self.logger.debug("setup model ui")
        result_df = self.simulate_model()
        self.plot_data(result_df=result_df)

    def on_new_model(self, mech_name):
        self.fill_rct_wgt(mech_name=mech_name)
        k_dict, err = self.parse_k_result(mech_name=mech_name)
        self.rct_wgt.set_k_dict(k_dict=k_dict)

        result_df = self.simulate_model()
        self.plot_data(result_df=result_df)

    def load_csv(self, csv_path):
        self.data = pd.read_csv(csv_path)
        if not self.species_to_checkbox:
            
            for col in self.data.columns:
                if col in ["time"] or col.startswith("cat") or col.startswith("event"):
                    continue
                species_cbox = QCheckBox(col)
                species_cbox.setChecked(True)
                species_cbox.stateChanged.connect(self.plot_data)
                self.selection_lyt.addWidget(species_cbox)
                self.species_to_checkbox[col] = species_cbox
        
        self.active_csv = csv_path
        self.logger.info(f"{self.active_csv = }")

        result_df = self.simulate_model()
        self.plot_data(result_df=result_df)

    def setup_plot(self):
        self.canvas = FigureCanvas(plt.Figure())
        self.ax = self.canvas.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.canvas.figure.tight_layout()
        self.resizeEvent = self.canvas_resize
    
    def canvas_resize(self, event):
        """
        Handles resizing of the window and updates the plot accordingly.
        """
        dpi = self.canvas.figure.dpi
        width, height = self.canvas.size().width(), self.canvas.size().height()
        self.canvas.figure.set_size_inches(width / dpi, height / dpi)
        self.canvas.draw()

    def on_click(self, event):
        if self.data is None:
            return
        self.plot_data()
    
    def on_select(self, eclick, erelease):
        # Prevent zoom if mouse click was too short (i.e. just a selection)
        dx = abs(eclick.x - erelease.x)
        dy = abs(eclick.y - erelease.y)
        drag_threshold = 10  # pixels

        if dx < drag_threshold and dy < drag_threshold:
            # Treat it like a click, ignore zoom
            return

        # Actual zoom behavior
        x0, y0 = eclick.xdata, eclick.ydata
        x1, y1 = erelease.xdata, erelease.ydata
        if None in [x0, y0, x1, y1]:
            return
        self.ax.set_xlim(min(x0, x1), max(x0, x1))
        self.ax.set_ylim(min(y0, y1), max(y0, y1))
        self.canvas.draw()
    
    def plot_data(self, result_df=None):
        if self.data is None or self.data.empty:
            return
        
        # Plot
        self.ax.cla()
        for species, cbox in self.species_to_checkbox.items():
            if cbox.isChecked():
                self.ax.scatter(self.data['time'], self.data[species], label=species)
                if result_df is not None:
                    if species not in result_df.columns:
                        continue
                    self.ax.plot(result_df["time"], result_df[species], linestyle=":", marker="*", markersize=5, label=f"{species} model")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.legend()
        apply_acs_layout_ax(self.ax)
        self.canvas.draw_idle()

    def set_starting_conc_in_sb_string(self, sb_string, c_dict):
        # Replace species starting concentrations in sb_string using c_dict.
        pattern = r"(J[^\n]*\n)(.*?)(\n\s*k1\s*=)"  # non-greedy match from J line to k1 line

        def replace_assignments(match):
            header = match.group(1)  # J1: ... line
            block = match.group(2)   # lines with species assignments
            footer = match.group(3)  # k1 = line

            def repl_line(line):
                m = re.match(r"(\w+)\s*=\s*.*", line)
                if m:
                    var = m.group(1)
                    if var in c_dict:
                        return f"{var} = {c_dict[var]}"
                return line

            new_block = "\n".join(repl_line(l) for l in block.splitlines())
            return header + new_block + footer
        return re.sub(pattern, replace_assignments, sb_string, flags=re.DOTALL)

    def set_k_values_in_sb_string(self, sb_string, k_dict):
        """
        Replace all kinetic constant assignments (k1, kN1, etc.) in the string
        with the values provided in k_values dictionary.
        
        Example:
            k_values = {"k1": 0.5, "kN1": 1.0}
        """
        # regex to match assignments like "k1 = 0" (possibly spaces around '=')
        pattern = r"\b(" + "|".join(re.escape(k) for k in k_dict.keys()) + r")\s*=\s*[^ \n,]+"

        # replacement function
        def repl(match):
            key = match.group(1)
            return f"{key} = {k_dict[key]}"

        # apply the replacement
        return re.sub(pattern, repl, sb_string)

    def simulate_model(self):
        # get entry of selected row as string
        model_index = self.ms_tbl.table.currentRow()
        if model_index < 0:
            self.ms_tbl.table.setCurrentCell(0, 0)
            model_index = 0
        mech_name = self.ms_tbl.table.item(model_index, 0).text()

        sb_file = os.path.join(self.model_folder, mech_name, "sb_string.txt")
        with open(sb_file, "r") as sbf:
            sb_string = sbf.read()

        csv_index = self.file_csv_wgt.table.currentRow()
        try:
            csv_file_name = self.file_csv_wgt.table.item(csv_index, 0).text()
        except AttributeError:
            self.logger.info("No csv selected yet.")
            return

        csv_file = os.path.join(self.time_course_folder, csv_file_name)
        df = pd.read_csv(csv_file)
        time_selection = df["time"]
        k_dict = self.rct_wgt.get_k_dict()
        c_dict = df.loc[0].to_dict()
        sb_string = self.set_starting_conc_in_sb_string(sb_string, c_dict)
        sb_string = self.set_k_values_in_sb_string(sb_string, k_dict)

        try:
            event_cols = df.filter(like="event").columns.tolist()
            event_index_of_ra = df.loc[0, event_cols].idxmax()
            sb_string = sb_string.replace(f"{event_index_of_ra} = 0", f"{event_index_of_ra} = 1")
        except ValueError:
            # means there is no event index aka no re-additions
            pass
        
        sim = Simulator()
        sim.simulate(sb_string=sb_string, times=time_selection)
        df_result = sim.result
        return df_result



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResultsWindow()
    window.setup_ui()
    window.resize(1000, 900)
    window.show()

    sys.exit(app.exec())