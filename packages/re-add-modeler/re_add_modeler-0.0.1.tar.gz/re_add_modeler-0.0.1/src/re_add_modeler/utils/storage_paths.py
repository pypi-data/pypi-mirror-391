import os

re_add_modeler_path = __file__[:-23]
temp_file_path = os.path.join(re_add_modeler_path, "temp")
# copasi_file_path = os.path.join(readdm_path, "copasi")
copasi_path = "copasi_path.txt"
# print(copasi_path)
with open(copasi_path, "r") as f:
    copasi_file_path = f.read()

print(f"{re_add_modeler_path = }\n{temp_file_path = }\n{copasi_file_path = }")


# D:\code\modules\hein_modules\MEx\src\readdm\copasi