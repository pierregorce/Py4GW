import Py4GW

class PathLocator:

    @staticmethod
    def get_custom_behaviors_root_directory() -> str:
        return Py4GW.Console.get_projects_path() + "\\Sources\\oazix\\CustomBehaviors"
    
    @staticmethod
    def get_project_root_directory() -> str:
        return Py4GW.Console.get_projects_path()
    
    @staticmethod
    def get_texture_fallback() -> str:
        return PathLocator.get_custom_behaviors_root_directory() + "\\gui\\textures\\no_bg.png"

    @staticmethod
    def get_skillbars_package_name() -> str:
        """Returns the package name for the skillbars directory."""
        return "Sources.oazix.CustomBehaviors.skillbars"

    @staticmethod
    def get_skill_packages() -> list[str]:
        """Returns the list of skill package names for utility skill discovery."""
        return [
            "Sources.oazix.CustomBehaviors.skills.common",
            "Sources.oazix.CustomBehaviors.skills.generic",
            "Sources.oazix.CustomBehaviors.skills.mesmer",
            "Sources.oazix.CustomBehaviors.skills.elementalist",
            "Sources.oazix.CustomBehaviors.skills.monk",
            "Sources.oazix.CustomBehaviors.skills.necromancer",
            "Sources.oazix.CustomBehaviors.skills.paragon",
            "Sources.oazix.CustomBehaviors.skills.ranger",
            "Sources.oazix.CustomBehaviors.skills.warrior",
            "Sources.oazix.CustomBehaviors.skills.assassin",
            "Sources.oazix.CustomBehaviors.skills.ritualist",
            "Sources.oazix.CustomBehaviors.skills.pve",
        ]
