from okin.base.chem_logger import chem_logger
from okin.base.chem_plot_utils import apply_acs_layout_ax
from okin.base.reaction import str_to_te
from okin.simulation.simulator import Simulator
from re_add_modeler.gui_files.wgt_table import CSVWidget
from re_add_modeler.gui_files.wgt_reactions import ReactionWidget

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtWidgets import QFileDialog, QPushButton
from PySide6.QtCore import Qt, QEvent, Signal

import os
import json
import sys
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import RectangleSelector
from matplotlib.backend_bases import MouseButton
matplotlib.use("QtAgg")  # Ensure a Qt backend
matplotlib.rcParams['backend'] = 'QtAgg'


class DataWindow(QMainWindow):
    added_model_sgn = Signal(str)

    def __init__(self):
        super().__init__()
        self.logger = chem_logger.getChild(self.__class__.__name__)
        self.total_state = {} # tracks everything to reload it later
        self.setup_folders()
        
        self.data = None
        self.selected_index = None
        self.deleted_points = []
        self.species_to_checkbox = {}
        self.models = {}

    def setup_folders(self):
        """
        Sets up the folder where all relevant information is saved for other windows to use.
        - ./time_courses/*.csv
        - ./models/model.json
        - ./models/sb_string.txt
        - ./reload_file.m
        """
        folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # self.work_folder = f"./src/readdm/output/{folder_name}"
        self.work_folder = f"./output/{folder_name}"
        os.mkdir(self.work_folder)
        self.model_folder = f"{self.work_folder}/models"
        self.time_course_folder = f"{self.work_folder}/time_courses"
        os.mkdir(self.model_folder)
        os.mkdir(self.time_course_folder)
    
    def setup_plot(self):
        self.canvas = FigureCanvas(plt.Figure())
        self.ax = self.canvas.figure.add_subplot(111)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.canvas.installEventFilter(self)

        # RectangleSelector for zoom
        self.selector = RectangleSelector(
            self.ax, self.on_select, useblit=True,
            button=[MouseButton.RIGHT],  # Left-click only
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True,
            props=dict(
                facecolor='none',   # <-- This disables fill
                edgecolor='black',
                linestyle='--',
                linewidth=1,
                alpha=1.0
            )
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Connect resize event to handle resizing
        self.canvas.figure.tight_layout()
        self.resizeEvent = self.canvas_resize

    def canvas_resize(self, event):
        """
        Handles resizing of the window and updates the plot accordingly.
        """
        # Get the figure dpi
        dpi = self.canvas.figure.dpi
        
        # Get current size of the canvas and update figure size
        width, height = self.canvas.size().width(), self.canvas.size().height()
        self.canvas.figure.set_size_inches(width / dpi, height / dpi)

        # Redraw the plot with updated size
        self.canvas.draw()

    def setup_ui(self):
        container = QWidget()
        main_lyt = QVBoxLayout(container)
        
        self.setup_plot()

        input_lyt = QHBoxLayout()
        input_height = 270

        table_list = [{"name": "csv_file", "width_%": -1, "enable_dragdrop": True}]
        self.csv_wgt = CSVWidget(table_list=table_list, num_row=8, fixed_height=input_height, csv_folder=self.time_course_folder)
        self.csv_wgt.new_csv_sgn.connect(self.load_csv)
        input_lyt.addWidget(self.csv_wgt, stretch=3.5)

        self.rct_wgt = ReactionWidget(num_rct=5, fixed_height=input_height)
        rct_list = ["A + cat -> cat1", "cat1 + B -> P + cat", 
                    # "cat + I -> cat2",
                    "cat + A -> cat2",
                    "cat + B -> cat2",
                    "cat + P -> cat2",
                    "cat -> cat2"
                    
                    ]
        self.rct_wgt.set_reactions(rct_list=rct_list)
        self.rct_wgt.add_m_sig.connect(self.track_models)
        input_lyt.addWidget(self.rct_wgt, stretch=3.5)
        
        self.selection_lyt = QHBoxLayout()

        undo_btn = QPushButton("Undo\nDelete")
        undo_btn.setFixedSize(75, 50)
        undo_btn.clicked.connect(self.undo_delete)
        self.selection_lyt.addWidget(undo_btn)
        self.selection_lyt.setAlignment(undo_btn, Qt.AlignCenter | Qt.AlignLeft)

        # Add buttons and canvas to the layout
        main_lyt.addLayout(input_lyt)
        main_lyt.addLayout(self.selection_lyt)
        # main_lyt.addWidget(btn_reset_zoom)
        main_lyt.addWidget(self.canvas)

        # Set the layout for the main window
        self.setCentralWidget(container)  # Set container widget as central widget of the window

        self.logger.debug("setup data tab")
        
        self.setCentralWidget(container)

        return container

    def eventFilter(self, obj, event):
        if obj == self.canvas:
            # Check if it's a right-click (button press event)
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
                self.right_click_pressed = True
            else:
                self.right_click_pressed = False

            # Handle key press only if right-click was detected
            if event.type() == QEvent.KeyPress and not self.right_click_pressed:
                if event.key() == Qt.Key_Delete and self.selected_index is not None and self.selected_trace is not None:
                    # Store the deleted point for undo
                    deleted_point = {
                        self.data.columns[0]: self.data.iloc[self.selected_index, 0],  # time
                        self.selected_trace: self.data.loc[self.selected_index, self.selected_trace]
                    }
                    self.deleted_points.append(deleted_point)

                    # Set the selected trace value to NaN instead of removing the entire row
                    self.data.loc[self.selected_index, self.selected_trace] = float('nan')
                    self.data.to_csv(self.active_csv, index=False)


                    self.plot_data()
                    return True

        # Allow event to propagate if not handled
        return False

    def undo_delete(self):
        if not self.deleted_points:
            return
        last_deleted = self.deleted_points.pop()

        time_val = last_deleted[self.data.columns[0]]
        species = list(last_deleted.keys())[1]  # Assuming time is first, species is second
        value = last_deleted[species]

        # Find the row with the matching time
        row_index = self.data[self.data[self.data.columns[0]] == time_val].index
        if not row_index.empty:
            self.data.at[row_index[0], species] = value
            self.data.to_csv(self.active_csv, index=False)
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
        
        # self.x_lim = (min(x0, x1), max(x0, x1))
        # self.y_lim = (min(y0, y1), max(y0, y1))
        self.ax.set_xlim(min(x0, x1), max(x0, x1))
        self.ax.set_ylim(min(y0, y1), max(y0, y1))

        self.canvas.draw()

    def load_csv(self, csv_path):
        
        # if isinstance(csv_path, list):
        #     csv_path = csv_path[0]

        self.data = pd.read_csv(csv_path)
        if not self.species_to_checkbox:
            
            for col in self.data.columns:
                if col == "time" or col.startswith("cat") or col.startswith("event"):
                    continue
                species_cbox = QCheckBox(col)
                species_cbox.setChecked(True)
                species_cbox.stateChanged.connect(self.plot_data)
                self.selection_lyt.addWidget(species_cbox)
                self.species_to_checkbox[col] = species_cbox
        
        self.active_csv = csv_path
        self.logger.info(f"{self.active_csv = }")
        self.plot_data()

    def plot_data(self):
        if self.data is None or self.data.empty:
            return

        # Extract time (x) and other traces (y)
        time_data = self.data['time']
        traces = self.data.drop(columns=['time'])

        # Clear previous plot content (but not the axis itself)
        self.ax.cla()

        # Plot each trace
        # for trace_name, trace_data in traces.items():
        for species, cbox in self.species_to_checkbox.items():
            if cbox.isChecked():
                self.ax.scatter(time_data, traces[species], label=species)

        # Highlight the selected point (red circle)
        if self.selected_index is not None and self.selected_trace is not None:
            self.ax.plot(
                self.data['time'][self.selected_index],
                self.data[self.selected_trace].iloc[self.selected_index],
                'ro', markersize=12, label='Selected Point'
            )

        # Set axis labels and redraw canvas
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.legend()
        apply_acs_layout_ax(self.ax)
        self.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        if self.data is None:
            return

        # Find the closest point from each trace and figure out which trace was clicked
        time_data = self.data['time']
        distances = {}

        # Calculate distances for each trace
        for trace_name in self.data.columns[1:]:
            trace_data = self.data[trace_name].values
            trace_distances = ((time_data - event.xdata)**2 + (trace_data - event.ydata)**2)
            closest_index = trace_distances.argmin()
            distances[trace_name] = (trace_distances[closest_index], closest_index)

        # Find the trace with the minimum distance to the clicked point
        self.selected_trace = min(distances, key=lambda k: distances[k][0])
        self.selected_index = distances[self.selected_trace][1]

        # Highlight the selected point
        self.plot_data()

    def save_new_csv(self):
        output_file = QFileDialog.getSaveFileName(self, "Save Modified CSV", "", "CSV Files (*.csv)")[0]
        if output_file:
            self.data.to_csv(output_file, index=False)

    def reset_zoom(self):
        if self.data is not None:
            self.ax.set_xlim(auto=True)
            self.ax.set_ylim(auto=True)
            self.plot_data()


    def build_sb_string(self, model, re_adds=None):
        # self.logger.info(f"build_sb_string {model = }")
        sim = Simulator()
        m_name = model["name"]
        m_steps = str_to_te(model["m_steps"])

        k_dict = model["k_dict"]
        c_dict = {}
        sb_string = sim._get_antimony_str(reactions=m_steps, k_dict=k_dict, c_dict=c_dict)

        # re_adds = list of all all information for each file. index corresponds to one file
        data_csv_index = 0
        #* re_adds contains everything [{filename: re_add_events}, {filename2}:…]
        for re_add_events in re_adds:
            event_string = ""
            used_chems = self.rct_wgt.get_used_chems()
            
            data_csv_index += 1

            
            event_string += "\n\n"
            event_var_string = f"\nevent_{data_csv_index} = 0"
            sb_string += event_var_string
            

            #* re_add_events is {filename: [[re_add], [re_add1, re_add2]…]}
            for ra_events in re_add_events.values(): # list of re-additions. can be multiple species at once. volume is combined for multiple ones earlier
                #* ra_events is [[re_add], [re_add1, re_add2]…] 

                for ra_event in ra_events:
                    ra = ra_event[0]
                    event_index = ra["event_index"]
                    
                    # print(f"\n\n{re_add_events = }\n\n{ra_events = }\n\n{ra_event = }\n\n{ra = }\n\n____________________")
                    

                    
                    added_species = [ra_["species"] for ra_ in ra_event]
                    added_mmol = [ra_["mmol"] for ra_ in ra_event]
                    

                    # for ra in ra_events: # list of species added during one specific re addition
                    
                    # added_species = roles[ra["species"]]
                    # how it is defined roles[name] = symbol

                    volume_str = f"rct_vol{event_index} = {ra['rct_volume_ml']}\nadd_vol{event_index} = {ra['added_vol_ml']}\nnew_vol{event_index} = rct_vol{event_index} + add_vol{event_index}\n"
                    ratio_str =  f"ratio{event_index} = rct_vol{event_index}/new_vol{event_index}\n"
                    condition_str = f"at(time>={ra['time_re_add']}) && (event_{data_csv_index}==1):\n"
                    
                    add_mmol_str = ""
                    for s, mmol in zip(added_species, added_mmol):
                        # add_mmol_str += f"{roles[s]}_added_mmol = {mmol}\n"
                        add_mmol_str += f"{s}_added_mmol = {mmol}\n"
                        # print(f"{s = }, {mmol = }\n{add_mmol_str = }\n")

                    adjust_conc_str = ""
                    for species in used_chems:
                        if species not in added_species:
                            adjust_conc_str += f"\t{species}={species}*ratio{event_index},\n"
                        
                        else:
                            # calculate mmol in reaction. add new mmol. divide by new volume for new conc
                            adjust_conc_str += f"\t{species}=({species}*rct_vol{event_index} + {species}_added_mmol)/new_vol{event_index},\n"

                    adjust_conc_str = adjust_conc_str[:-2] # remove last ,
                    adjust_conc_str += "\n"

                    event_string += volume_str
                    event_string += ratio_str
                    event_string += add_mmol_str
                    event_string += condition_str
                    event_string += adjust_conc_str
                    event_string

            sb_string += event_string

 
        sb_string_path = f"{self.model_folder}/{m_name}/sb_string.txt"
        with open(sb_string_path, "w") as f:
            f.write(sb_string)

        return sb_string_path

    def track_models(self, model):
        print(f"{model = }")
        # called when wgt_reactions emits add_m_sig(dict)

        self.logger.info("track mechansim")
        m_name = model["name"]

        model["m_steps"] = model["m_steps_user"]
        model["used_species"] = self.rct_wgt.get_used_chems()

        model["k_dict"] = self.rct_wgt.get_k_dict(as_float=False)

        m_path = f"{self.model_folder}/{m_name}"
        m_file = f"{m_path}/model.json"
        os.makedirs(m_path, exist_ok=True)
        with open(m_file, "w") as f:
            json.dump(model, f, indent=4)
        
        self.csv_wgt.add_event_index_to_all()

        re_adds = self.csv_wgt.get_re_additions()
        sb_string_path = self.build_sb_string(model=model, re_adds=re_adds)

        # send signal to model tab to update its layout
        self.logger.info(f"emiting {sb_string_path = }")
        self.added_model_sgn.emit(sb_string_path)

    # A1 + catRu -> Prd + catRu
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataWindow()
    window.setup_ui()
    # window.load_csv(csv_path=r"C:\Users\Finn\HeinLab\hein_modules\readdm\A08.csv")
    window.resize(1200, 850)
    window.show()

    sys.exit(app.exec())

