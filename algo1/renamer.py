import os


os.rename(file := 'my_array.cp39-win_amd64.pyd', new_name := ".".join(file.split(".")[::2]))

print()
