import os
import re

version = os.getenv("CHECKER_VERSION")
path = os.path.dirname(os.path.abspath(__file__))
items = os.listdir(path)
files = [item for item in items if os.path.isfile(os.path.join(path, item))]
for file in files:
    pattern = f"(prune_old_version.py|ceker-{version}.py)"
    path_file = path + "/" + file
    if not re.match(rf"{pattern}", file):
        os.remove(path_file)
