from Py4GWCoreLib import PyImGui, ImGui, GLOBAL_CACHE
from Py4GWCoreLib import ProfessionTextureMap

MODULE_NAME = "tester for everything"
count = 0

class Qzd:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Qzd, cls).__new__(cls)
            cls._instance._initialized = False
            print("Qzd created __new__")
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.custom_combat_behavior:Qzd | None = None
            self._initialized = True
            print("Qzd created __init__")

    def print_hello(self):
        print("Hello World!")
        global count
        count += 1

def main():
    window_flags=PyImGui.WindowFlags.AlwaysAutoResize 
    PyImGui.begin("Tester for Everything", window_flags)
    PyImGui.text("Hello World!")
    qzd = Qzd()
    qzd.print_hello()
    print(count)
    PyImGui.end()



    
if __name__ == "__main__":
    main()
