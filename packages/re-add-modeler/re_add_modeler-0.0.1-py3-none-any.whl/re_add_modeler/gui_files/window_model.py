from okin.base.chem_logger import chem_logger
from re_add_modeler.utils.utils import get_newest_timestamp_folder
from re_add_modeler.utils.storage_paths import temp_file_path
from re_add_modeler.utils.storage_paths import copasi_file_path
from re_add_modeler.gui_files.wgt_table import CSVWidget
from re_add_modeler.gui_files.wgt_m_table import ModelTableWidget

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QPushButton,QHBoxLayout,QVBoxLayout,QFormLayout
from PySide6.QtCore import Qt
from re_add_modeler.gui_files.wgt_sb_string import SbStringWidget
from re_add_modeler.gui_files.wgt_qtext_window import AdvancedSettingsWidget
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy

import os
import glob
import json
import pandas as pd
import sys

class ModelWindow(QMainWindow):
    copasi_complete_sgn = Signal()

    def __init__(self):
        self.logger = chem_logger.getChild(self.__class__.__name__)
        super().__init__()
        self.setup_folders()
        # self.setup_ui()
        self.setWindowTitle("Model")
    
    def setup_folders(self):
        # self.work_folder = get_newest_timestamp_folder("./src/readdm/output")
        self.work_folder = get_newest_timestamp_folder("./output")
        self.model_folder = os.path.join(self.work_folder, "models")
        self.time_course_folder = os.path.join(self.work_folder, "time_courses")
        # self.copasi_settings_folder = os.path.abspath("./src/readdm/copasi/temp/input")
        
        self.DEFAULT_SETTINGS_FILE = os.path.join(copasi_file_path, "temp", "input", "settings.txt") # this is only loaded / copied if user_settings_file not exsti
        self.USER_SETTINGS_FILE = os.path.join(copasi_file_path, "temp", "input", "user_settings.txt")
        self.copasi_settings_wgt = AdvancedSettingsWidget(settings_file=self.DEFAULT_SETTINGS_FILE, custom_file=self.USER_SETTINGS_FILE)

        self.COPASI_BASE_PATH = f"{copasi_file_path}/temp/"
        self.COPASI_RUN_PATH = f"{copasi_file_path}/"
        self.COPASI_INPUT_PATH = f"{copasi_file_path}/temp/input/"
        self.COPASI_DEFAULT_PATH = f"{copasi_file_path}/default/"      
        self.COPASI_OUTPUT_PATH = f"{copasi_file_path}/temp/kopt/Fit1/results/curr_run/" # copasi demands this structure

    def setup_ui(self):
        container = QWidget()
        main_lyt = QHBoxLayout(container)
        self.sb_wgt = SbStringWidget()
        main_lyt.addWidget(self.sb_wgt)

        modeling_input_lyt = QVBoxLayout()
        modeling_input_container = QWidget()
        modeling_input_container.setLayout(modeling_input_lyt)

        # Prevent vertical stretching
        modeling_input_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        modeling_input_container.setMaximumWidth(600)

        # ! model display
        m_tbl_lyt = QHBoxLayout()
        self.ms_tbl = ModelTableWidget()
        self.ms_tbl.new_sb_sgn.connect(self.update_sb_string)
        m_tbl_lyt.addWidget(self.ms_tbl)
        modeling_input_lyt.addLayout(m_tbl_lyt)

        #* file input
        file_input_lyt = QHBoxLayout()
        train_table_list = [{"name": "training files", "width_%": -1, "enable_dragdrop": False}]
        test_table_list = [{"name": "testing files", "width_%": -1, "enable_dragdrop": False}]
        self.train_csv_wgt = CSVWidget(table_list=train_table_list, add_buttons=False, allow_edit=False, fixed_height=405, csv_folder=self.time_course_folder, selection_mode="multi")
        self.test_csv_wgt = CSVWidget(table_list=test_table_list, add_buttons=False, allow_edit=False, fixed_height=405, csv_folder=self.time_course_folder, selection_mode="multi")

        file_input_lyt.addWidget(self.train_csv_wgt)
        file_input_lyt.addWidget(self.test_csv_wgt)
        modeling_input_lyt.addLayout(file_input_lyt)

        #* settings
        mod_settings_lyt = QHBoxLayout()
        to_match_lyt = QFormLayout()
        self.to_match_qle = QLineEdit()
        self.to_match_qle.setFixedWidth(200)
        to_match_lyt.addRow("Species COPASI uses:", self.to_match_qle)
        mod_settings_lyt.addLayout(to_match_lyt)

        gen_lyt = QFormLayout()
        self.gen_qle = QLineEdit()
        self.gen_qle.setFixedWidth(50)
        self.gen_qle.setText("10")
        self.gen_qle.textChanged.connect(self.update_copasi_settings)
        gen_lyt.addRow("Generations:", self.gen_qle)
        mod_settings_lyt.addLayout(gen_lyt)

        pop_lyt = QFormLayout()
        self.pop_qle = QLineEdit()
        self.pop_qle.setFixedWidth(50)
        self.pop_qle.setText("8")
        self.pop_qle.textChanged.connect(self.update_copasi_settings)
        pop_lyt.addRow("Population:", self.pop_qle)
        mod_settings_lyt.addLayout(pop_lyt)

        modeling_input_lyt.addLayout(mod_settings_lyt)
        advanced_copasi_b = QPushButton("Full COPASI")
        advanced_copasi_b.clicked.connect(self.copasi_settings_wgt.exec)
        mod_settings_lyt.addWidget(advanced_copasi_b)
        run_b = QPushButton("Run Evaluation")
        run_b.setFixedHeight(80)
        run_b.clicked.connect(self.run_copasi)
        modeling_input_lyt.addWidget(run_b)

        main_lyt.addLayout(modeling_input_lyt)
        main_lyt.addWidget(modeling_input_container, Qt.AlignTop)
        self.setCentralWidget(container)
        self.logger.debug("setup model ui")
        return container

    def update_sb_string(self, sb_string_path, sb_string=None):
        self.logger.info(f"{sb_string_path = }, {bool(sb_string) = }")
        if not sb_string:
            with open(sb_string_path, "r") as f:
                sb_string = f.read()
 
        self.sb_wgt.set_sb_string(sb_string=sb_string)

    def populate_lyt(self, sb_string_path):
        self.update_sb_string(sb_string_path)
        

        self.train_csv_wgt.clear_table()
        self.test_csv_wgt.clear_table()

        edited_csv_files = glob.glob(f"{ self.time_course_folder}/*.csv")

        print(f"{edited_csv_files = }")

        for csv_path in edited_csv_files:
            self.train_csv_wgt.add_file(csv_path)
            self.test_csv_wgt.add_file(csv_path)

        #* to_match
        temp_df = pd.read_csv(csv_path)
        to_match = []
        for col in temp_df.columns:
            if col == "time" or col.startswith("event_") or col.startswith("cat"):
                continue
            if temp_df[col].iloc[3]:
                to_match.append(col)

        # self.logger.info(f"{to_match = }")
        self.to_match_qle.setText(", ".join(to_match))
        self.to_match = to_match

        #* models
        self.ms_tbl.populate_table()


    def update_copasi_settings(self):
        # this updates the user_settings.txt file with values from the gui
        settings_str = self.copasi_settings_wgt.get_content()

        nr_gen = int(self.gen_qle.text())
        nr_pop = int(self.pop_qle.text())
        
        settings_dict = eval(settings_str)

        # Update the desired values
        settings_dict['number_of_generations'] = str(nr_gen)
        settings_dict['population_size'] = str(nr_pop)

        new_settings_str = json.dumps(settings_dict, indent=4).replace("true", "True").replace("false", "False").replace("null", "None")

        self.copasi_settings_wgt.save_text(new_settings_str)



    def clear_copasi_inputs(self):
        self.logger.info("in clear")

        files = glob.glob(f"{self.COPASI_INPUT_PATH}/*.csv")
        for f in files:
            os.remove(f)

        files = glob.glob(f"{self.COPASI_INPUT_PATH}/*.txt")
        for f in files:
            if not f.endswith("user_settings.txt"):
                os.remove(f)

    def create_copasi_csvs(self):
        to_match = [s.strip() for s in self.to_match_qle.text().split(",")]
        self.logger.info(f"\n\nThis is in create_copasi_csvs : {to_match = }\n")

        train_files_df = self.train_csv_wgt.get_df()["training files"].tolist()
        test_files_df = self.test_csv_wgt.get_df()["testing files"].tolist()
        
        # write train test split to file for result section
        train_test_split_path = os.path.join(temp_file_path, "train_test.json")
        train_test = {"train": train_files_df, "test": test_files_df}
        with open(train_test_split_path, "w") as ttp:
            json.dump(train_test, ttp, indent=2)


        # df[c].iloc[0] for all that have different concentrations between experiments -> all other from conc input
        for path in train_files_df:
            df = pd.read_csv(os.path.join(self.time_course_folder, path))
            name = os.path.basename(path)
            time_col = [c for c in df.columns if c.startswith("time")][0]

            try:
                df = df.rename(columns={time_col: 'time'})
            except:
                pass

            df = df.reset_index(drop=True)
            df = df.set_index("time")
            new_path = os.path.join(self.COPASI_INPUT_PATH, name)

            # create the _indep column to signal COPASI the starting concentration for that species FROM THE CSV FILE
            for species in df.columns:
                # create starting conc for species in CSV
                if species.lower().startswith("unnamed") or species.lower().startswith("time"):
                    continue
    
                starting_conc = df[species].iloc[0]
                col_name = species + "_indep"
                df[col_name] = None  # Initialize the new column with None (or NaN)
                    
                try:
                    self.logger.debug(f"{df[species].iloc[0]=}, {starting_conc=}")
                except KeyError:
                    pass
                # Set the value for the first row in the new column
                df.loc[0, col_name] = starting_conc


            # delete all time course values that should not be used for to match
            for col in df.columns:
                if col == "time" or col.endswith("_indep"):
                    continue
                if col not in to_match:
                    # Set all values except the first one to ""
                    df.iloc[1:, df.columns.get_loc(col)] = ""


            self.logger.info(f"Created csv at {new_path=}")
        
            # remove [] from headers 
            df.columns = [col.replace('[', '').replace(']', '') for col in df.columns]

            df.to_csv(new_path)

    def create_copasi_inputs(self, mech_name):
        # settings is in self.copasi_settings_wgt and gets updated automatically




        model_file = os.path.join(self.model_folder, mech_name, "model.json")
        with open(model_file, "r") as mf:
            model = json.load(mf)

        # fit_items.txt
        fit_item_path = os.path.join(self.COPASI_INPUT_PATH, "fit_items.txt")
        k_dict = model["k_dict"]
        k_to_fit = [k_name for k_name in k_dict.keys() if "$" not in k_dict[k_name]]
        self.k_to_fit = k_to_fit
        self.logger.info(f"{k_to_fit=}")

        with open(fit_item_path, "w") as fif:
            fif.write(str(k_to_fit))

        # sb_string.txt
        # sb_string = self.sb_wgt.get_sb_str()
        sb_path = os.path.join(self.model_folder, mech_name, "sb_string.txt")
        with open(sb_path, "r") as sf:
            sb_string = sf.read()

        copasi_sb_string_path = os.path.join(self.COPASI_INPUT_PATH, "sb_string.txt")
        with open(copasi_sb_string_path, "w") as sbf:
            print(f"COPASI from Sb string:\n{sb_string}")
            sbf.write(sb_string)


        

    def run_copasi(self):
        all_mech_folders = glob.glob(f"{self.model_folder}/*")
        folder_nareaddm = [os.path.basename(f) for f in all_mech_folders]

        for mech_folder, mech_name in zip(all_mech_folders, folder_nareaddm):
            self.logger.info(f"{mech_name = }\n{mech_folder = }")
        
            self.clear_copasi_inputs()
            self.create_copasi_csvs()
            self.create_copasi_inputs(mech_name=mech_name) # generate COPASI settings -> full copasi dict in txt file -> include species to match, file paths, nr_gen, nr_pop, algorithm etc

            cwd = os.path.abspath(self.COPASI_RUN_PATH)

            #! version for calling second environment
            python_exe_path = os.path.join(cwd, "copasi_env", "python.exe")
            python_file_path = os.path.join(cwd, "optimize_k.py")
            cmd = f"{python_exe_path} {python_file_path}"
            os.system(cmd)

            result_df = self.read_results()
            result_path = os.path.join(mech_folder, "k_result.csv")
            result_df.to_csv(result_path, index=False)
        
        self.copasi_complete_sgn.emit()

    def read_results(self):
        paths_to_ks = glob.glob(self.COPASI_OUTPUT_PATH + "\*.txt")
        
        dfs = []
        for path_to_ks  in paths_to_ks:
            temp_df = pd.read_csv(path_to_ks, sep="\t")
            dfs.append(temp_df)
        
        df = pd.concat(dfs, ignore_index=True).sort_values(by='RSS', ascending=True)
        return df

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelWindow()
    window.setup_ui()
    window.resize(1200, 850)
    window.show()

    sys.exit(app.exec())