
import os
module_name = "Oasix"
import sys
import importlib
# from Py4GWCoreLib import *

import os
print(os.getcwd())  # Prints the current working directory

# Iterate through all modules in sys.modules (already imported modules)
# Iterate over all imported modules and reload them
for module_name in list(sys.modules.keys()):
    if module_name not in ("sys", "importlib", "cache_data", "oasix"):
        try:
            if "hero" in module_name.lower() or "py4gw" in module_name.lower() or "custom" in module_name.lower() or "ritu" in module_name.lower():
                print(f"Reloading module: {module_name}")
                del sys.modules[module_name]
                # importlib.reload(module_name)
                pass
        except Exception as e:
            print(f"Error reloading module {module_name}: {e}")


def configure():
    pass

def main():
    pass

if __name__ == "__main__":
    main()
