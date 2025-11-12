#!/usr/bin/env python3
"""
Nueroid Digital Twin Framework - Core Components
RLab Implementation for Educational Robotics
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime

# =============================================================================
# Nueroid Core Framework - Abstract Factory Pattern
# =============================================================================

class DigitalTwinType(Enum):
    COMPONENT = "component"
    ASSET = "asset"
    SYSTEM = "system"
    PRODUCT = "product"
    FACILITY = "facility"
    PROCESS = "process"

class HierarchyLevel(Enum):
    COMPONENTS = 0
    ASSETS = 1
    SYSTEMS = 2
    PRODUCTS = 3
    FACILITIES = 4

class Model(ABC):
    """Abstract Model class containing static data and assets"""
    
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.now()
        self.static_data: Dict[str, Any] = {}
        self.widgets: List[Dict] = []
        self.assets_3d: List[str] = []
        self.tables: List[Dict] = []
    
    def add_widget(self, widget_type: str, config: Dict) -> None:
        """Add a widget to the model"""
        widget = {
            "id": str(uuid.uuid4()),
            "type": widget_type,
            "config": config,
            "created_at": datetime.now()
        }
        self.widgets.append(widget)
    
    def add_3d_asset(self, asset_path: str) -> None:
        """Add a 3D asset to the model"""
        self.assets_3d.append(asset_path)
    
    def add_table(self, table_name: str, schema: Dict) -> None:
        """Add a data table to the model"""
        table = {
            "name": table_name,
            "schema": schema,
            "data": []
        }
        self.tables.append(table)

class Shadow(ABC):
    """Abstract Shadow class handling workflows and runtime"""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.user_workflows: List[Dict] = []
        self.debug_workflows: List[Dict] = []
        self.hardware_interfaces: List[Dict] = []
        self.processes: List[Dict] = []
    
    def add_workflow(self, workflow_type: str, steps: List[Dict], is_debug: bool = False) -> None:
        """Add a workflow to shadow"""
        workflow = {
            "id": str(uuid.uuid4()),
            "type": workflow_type,
            "steps": steps,
            "created_at": datetime.now(),
            "is_active": True
        }
        
        if is_debug:
            self.debug_workflows.append(workflow)
        else:
            self.user_workflows.append(workflow)
    
    def add_hardware_interface(self, interface_type: str, config: Dict) -> None:
        """Add hardware interface configuration"""
        interface = {
            "type": interface_type,
            "config": config,
            "status": "inactive"
        }
        self.hardware_interfaces.append(interface)

class Twin(ABC):
    """Abstract Twin class handling interactions and dashboard"""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.dashboard_widgets: List[Dict] = []
        self.user_interactions: List[Dict] = []
        self.ai_interactions: List[Dict] = []
        self.real_time_data: Dict[str, Any] = {}
    
    def add_dashboard_widget(self, widget_type: str, position: Dict, config: Dict) -> None:
        """Add widget to dashboard"""
        widget = {
            "id": str(uuid.uuid4()),
            "type": widget_type,
            "position": position,
            "config": config,
            "created_at": datetime.now()
        }
        self.dashboard_widgets.append(widget)
    
    def log_interaction(self, user_type: str, action: str, data: Dict, is_ai: bool = False) -> None:
        """Log user or AI interaction"""
        interaction = {
            "id": str(uuid.uuid4()),
            "user_type": user_type,
            "action": action,
            "data": data,
            "timestamp": datetime.now(),
            "is_ai": is_ai
        }
        
        if is_ai:
            self.ai_interactions.append(interaction)
        else:
            self.user_interactions.append(interaction)

class DigitalTwin(ABC):
    """Abstract Digital Twin class"""
    
    def __init__(self, name: str, twin_type: DigitalTwinType):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = twin_type
        self.created_at = datetime.now()
        self.children: List['DigitalTwin'] = []
        self.parent: Optional['DigitalTwin'] = None
        self.process_twin: Optional['ProcessDigitalTwin'] = None
        
        # Core components
        self.model: Model
        self.shadow: Shadow
        self.twin: Twin
    
    def add_child(self, child: 'DigitalTwin') -> None:
        """Add child digital twin"""
        child.parent = self
        self.children.append(child)
    
    def find_twin(self, twin_id: str) -> Optional['DigitalTwin']:
        """Find twin by ID in hierarchy"""
        if self.id == twin_id:
            return self
        
        for child in self.children:
            found = child.find_twin(twin_id)
            if found:
                return found
        
        return None
    
    def get_hierarchy_path(self) -> List[str]:
        """Get hierarchy path from root"""
        path = [self.name]
        current = self.parent
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return path

class ProcessDigitalTwin(DigitalTwin):
    """Process-specific digital twin for executable workflows"""
    
    def __init__(self, name: str, target_twin: DigitalTwin):
        super().__init__(name, DigitalTwinType.PROCESS)
        self.target_twin = target_twin
        self.executable_workflows: List[Dict] = []
        self.execution_history: List[Dict] = []
    
    def add_executable_workflow(self, workflow: Dict) -> None:
        """Add executable workflow to process twin"""
        self.executable_workflows.append(workflow)
    
    def execute_workflow(self, workflow_id: str, parameters: Dict) -> Dict:
        """Execute a workflow"""
        execution_record = {
            "workflow_id": workflow_id,
            "parameters": parameters,
            "start_time": datetime.now(),
            "status": "running"
        }
        
        # Simulate workflow execution
        execution_record["status"] = "completed"
        execution_record["end_time"] = datetime.now()
        execution_record["result"] = {"message": f"Workflow {workflow_id} executed successfully"}
        
        self.execution_history.append(execution_record)
        return execution_record

# =============================================================================
# Abstract Factory Implementation
# =============================================================================

class NueroidFactory(ABC):
    """Abstract Factory for creating digital twin families"""
    
    @abstractmethod
    def create_model(self, name: str) -> Model:
        pass
    
    @abstractmethod
    def create_shadow(self) -> Shadow:
        pass
    
    @abstractmethod
    def create_twin(self) -> Twin:
        pass
    
    @abstractmethod
    def create_digital_twin(self, name: str) -> DigitalTwin:
        pass

class ComponentFactory(NueroidFactory):
    """Factory for Component-level digital twins"""
    
    def create_model(self, name: str) -> Model:
        model = Model(name)
        model.static_data = {"level": "component", "version": "1.0"}
        return model
    
    def create_shadow(self) -> Shadow:
        shadow = Shadow()
        # Component-specific shadow configuration
        return shadow
    
    def create_twin(self) -> Twin:
        twin = Twin()
        # Component-specific twin configuration
        return twin
    
    def create_digital_twin(self, name: str) -> DigitalTwin:
        twin = DigitalTwin(name, DigitalTwinType.COMPONENT)
        twin.model = self.create_model(name)
        twin.shadow = self.create_shadow()
        twin.twin = self.create_twin()
        return twin

class AssetFactory(NueroidFactory):
    """Factory for Asset-level digital twins"""
    
    def create_model(self, name: str) -> Model:
        model = Model(name)
        model.static_data = {"level": "asset", "version": "1.0"}
        return model
    
    def create_shadow(self) -> Shadow:
        shadow = Shadow()
        # Asset-specific shadow configuration
        return shadow
    
    def create_twin(self) -> Twin:
        twin = Twin()
        # Asset-specific twin configuration
        return twin
    
    def create_digital_twin(self, name: str) -> DigitalTwin:
        twin = DigitalTwin(name, DigitalTwinType.ASSET)
        twin.model = self.create_model(name)
        twin.shadow = self.create_shadow()
        twin.twin = self.create_twin()
        return twin

class SystemFactory(NueroidFactory):
    """Factory for System-level digital twins"""
    
    def create_model(self, name: str) -> Model:
        model = Model(name)
        model.static_data = {"level": "system", "version": "1.0"}
        return model
    
    def create_shadow(self) -> Shadow:
        shadow = Shadow()
        # System-specific shadow configuration
        return shadow
    
    def create_twin(self) -> Twin:
        twin = Twin()
        # System-specific twin configuration
        return twin
    
    def create_digital_twin(self, name: str) -> DigitalTwin:
        twin = DigitalTwin(name, DigitalTwinType.SYSTEM)
        twin.model = self.create_model(name)
        twin.shadow = self.create_shadow()
        twin.twin = self.create_twin()
        return twin

class ProductFactory(NueroidFactory):
    """Factory for Product-level digital twins"""
    
    def create_model(self, name: str) -> Model:
        model = Model(name)
        model.static_data = {"level": "product", "version": "1.0"}
        return model
    
    def create_shadow(self) -> Shadow:
        shadow = Shadow()
        # Product-specific shadow configuration
        return shadow
    
    def create_twin(self) -> Twin:
        twin = Twin()
        # Product-specific twin configuration
        return twin
    
    def create_digital_twin(self, name: str) -> DigitalTwin:
        twin = DigitalTwin(name, DigitalTwinType.PRODUCT)
        twin.model = self.create_model(name)
        twin.shadow = self.create_shadow()
        twin.twin = self.create_twin()
        return twin

class FacilityFactory(NueroidFactory):
    """Factory for Facility-level digital twins"""
    
    def create_model(self, name: str) -> Model:
        model = Model(name)
        model.static_data = {"level": "facility", "version": "1.0"}
        return model
    
    def create_shadow(self) -> Shadow:
        shadow = Shadow()
        # Facility-specific shadow configuration
        return shadow
    
    def create_twin(self) -> Twin:
        twin = Twin()
        # Facility-specific twin configuration
        return twin
    
    def create_digital_twin(self, name: str) -> DigitalTwin:
        twin = DigitalTwin(name, DigitalTwinType.FACILITY)
        twin.model = self.create_model(name)
        twin.shadow = self.create_shadow()
        twin.twin = self.create_twin()
        return twin