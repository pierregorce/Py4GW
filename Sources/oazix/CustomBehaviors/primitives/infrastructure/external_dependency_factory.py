from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.external_event_bus import ExternalEventBus
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger_factory import ExternalLoggerFactory
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.path.path_locator import PathLocator
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.persistence.persistence_locator import PersistenceLocator

class ExternalDependencyFactory:

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExternalDependencyFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        
        if not self._initialized:
            # from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.event_bus.py4gw_external_event_bus import Py4GwExternalEventBus
            # from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.logging.py4gw_external_logger_factory import Py4gwExternalLoggerFactory
            # from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.path.py4gw_path_locator import Py4GwPathLocator
            # from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.persistence.persistence_locator import PersistenceLocator

            # self.external_logger_factory:ExternalLoggerFactory = Py4gwExternalLoggerFactory()
            # self.path_locator:PathLocator = Py4GwPathLocator()
            # self.external_event_bus:ExternalEventBus = Py4GwExternalEventBus()
            # self.persistence_locator = PersistenceLocator() #no custom implem for now

            from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.logging.mamba_external_logger_factory import MambaExternalLoggerFactory
            from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.event_bus.mamba_external_event_bus import MambaExternalEventBus
            from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.path.mamba_path_locator import MambaPathLocator
            self.external_logger_factory:ExternalLoggerFactory = MambaExternalLoggerFactory()
            self.path_locator:PathLocator = MambaPathLocator()
            self.external_event_bus:ExternalEventBus = MambaExternalEventBus()
            self.persistence_locator = PersistenceLocator() #no custom implem for now


            self._initialized = True
