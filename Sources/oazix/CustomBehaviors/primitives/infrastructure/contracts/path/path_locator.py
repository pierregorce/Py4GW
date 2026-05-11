from abc import abstractmethod

class PathLocator:

    @abstractmethod
    def get_custom_behaviors_root_directory(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def get_project_root_directory(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_texture_fallback(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_skillbars_package_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_skill_packages(self) -> list[str]:
        raise NotImplementedError