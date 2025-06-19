import sys
import os

# Ensures the root directory (project/) is added to sys.path
current_file = os.path.join(os.getcwd(), "main.py")
print(f"__file__ is not defined, using fallback: {current_file}")

root_dir = os.path.dirname(os.path.abspath(current_file))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Import other modules/files from the project
import __HeroAI_outside

def main():
    __HeroAI_outside.main()
    pass

if __name__ == "__main__":
    main()


