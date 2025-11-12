"""
RLab CLI - Digital Twins for Educational Robotics

A comprehensive platform for managing educational robotics using digital twin technology,
powered by the Nueroid framework with abstract factory pattern implementation.
"""

__version__ = "1.0.0"
__author__ = "RLab Team"
__email__ = "rlab@rosversity.com"

# Core framework imports
from .core import (
    DigitalTwinType,
    HierarchyLevel,
    Model,
    Shadow,
    Twin,
    DigitalTwin,
    ProcessDigitalTwin,
    NueroidFactory,
    ComponentFactory,
    AssetFactory,
    SystemFactory,
    ProductFactory,
    FacilityFactory
)

# RLab platform imports
from .platform import (
    UserType,
    RLabPlatform
)

# CLI interface
from .cli import RLabCLI

# Main entry point
from .main import main

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Core framework
    "DigitalTwinType",
    "HierarchyLevel",
    "Model",
    "Shadow", 
    "Twin",
    "DigitalTwin",
    "ProcessDigitalTwin",
    "NueroidFactory",
    "ComponentFactory",
    "AssetFactory",
    "SystemFactory", 
    "ProductFactory",
    "FacilityFactory",
    
    # Platform
    "UserType",
    "RLabPlatform",
    
    # CLI
    "RLabCLI",
    "main"
]