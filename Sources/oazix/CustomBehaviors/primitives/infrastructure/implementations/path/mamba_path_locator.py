from pathlib import Path
from typing import override

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.path.path_locator import PathLocator
import mamba

class MambaPathLocator(PathLocator):

    def _find_cb_dir(self) -> Path:
        """Locate the vendored CustomBehaviors directory."""
        return mamba.third_party_dir() / "custom_behaviors"

    @override
    def get_custom_behaviors_root_directory(self) -> str:
        return str(self._find_cb_dir())
    
    @override
    def get_project_root_directory(self) -> str:
        return str(self._find_cb_dir().parent)

    @override
    def get_texture_fallback(self) -> str:
        return self.get_custom_behaviors_root_directory() + "\\gui\\textures\\no_bg.png"

    @override
    def get_skillbars_package_name(self) -> str:
        """Returns the package name for the skillbars directory."""
        return "Sources.oazix.CustomBehaviors.skillbars"

    @override   
    def get_skill_packages(self) -> list[str]:
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
