#!/usr/bin/env python3
"""
RLab Platform Implementation using Nueroid Digital Twins
"""

from enum import Enum
from typing import Dict, List, Any
from datetime import datetime
from .core import (
    DigitalTwin, DigitalTwinType, ProcessDigitalTwin,
    ComponentFactory, AssetFactory, SystemFactory, 
    ProductFactory, FacilityFactory
)

class UserType(Enum):
    SCHOOL_ADMIN = "school_admin"
    MANAGEMENT = "management"
    PROFESSOR = "professor"
    STUDENT = "student"
    INDUSTRY = "industry"
    RESEARCH_PARTNER = "research_partner"
    VENDOR = "vendor"
    DEVELOPER = "developer"

class RLabPlatform:
    """RLab Platform implementation using Nueroid Digital Twins"""
    
    def __init__(self):
        self.factories = {
            DigitalTwinType.COMPONENT: ComponentFactory(),
            DigitalTwinType.ASSET: AssetFactory(),
            DigitalTwinType.SYSTEM: SystemFactory(),
            DigitalTwinType.PRODUCT: ProductFactory(),
            DigitalTwinType.FACILITY: FacilityFactory()
        }
        self.root_twin = None
        self.users: Dict[str, UserType] = {}
        self.robotics_labs: List[DigitalTwin] = []
    
    def initialize_rlab_facility(self, name: str) -> DigitalTwin:
        """Initialize RLab facility with complete hierarchy"""
        facility_factory = self.factories[DigitalTwinType.FACILITY]
        self.root_twin = facility_factory.create_digital_twin(name)
        
        # Create product level
        product_factory = self.factories[DigitalTwinType.PRODUCT]
        rlab_software = product_factory.create_digital_twin("RLab Software Platform")
        rlab_hardware = product_factory.create_digital_twin("RLab Robotics Hardware")
        
        self.root_twin.add_child(rlab_software)
        self.root_twin.add_child(rlab_hardware)
        
        # Create system level under hardware
        system_factory = self.factories[DigitalTwinType.SYSTEM]
        user_management = system_factory.create_digital_twin("User Management System")
        course_management = system_factory.create_digital_twin("Course Management System")
        lab_management = system_factory.create_digital_twin("Lab Management System")
        
        rlab_software.add_child(user_management)
        rlab_software.add_child(course_management)
        rlab_software.add_child(lab_management)
        
        # Create robotics lab system
        robotics_lab = system_factory.create_digital_twin("Robotics Learning Lab")
        rlab_hardware.add_child(robotics_lab)
        self.robotics_labs.append(robotics_lab)
        
        print(f"✅ RLab Platform '{name}' initialized with complete hierarchy")
        return self.root_twin
    
    def add_robotics_asset(self, lab_name: str, asset_name: str, asset_type: str) -> DigitalTwin:
        """Add robotics asset to lab"""
        asset_factory = self.factories[DigitalTwinType.ASSET]
        asset_twin = asset_factory.create_digital_twin(asset_name)
        
        # Find the lab
        lab = self.root_twin.find_twin(lab_name) if self.root_twin else None
        if not lab:
            # Create new lab if not found
            system_factory = self.factories[DigitalTwinType.SYSTEM]
            lab = system_factory.create_digital_twin(lab_name)
            self.robotics_labs.append(lab)
        
        lab.add_child(asset_twin)
        
        # Add asset-specific configuration
        asset_twin.model.static_data.update({
            "asset_type": asset_type,
            "status": "active",
            "purchase_date": datetime.now().isoformat()
        })
        
        # Create process twin for the asset
        process_twin = ProcessDigitalTwin(f"{asset_name}_Process", asset_twin)
        asset_twin.process_twin = process_twin
        
        print(f"✅ Robotics asset '{asset_name}' added to lab '{lab_name}'")
        return asset_twin
    
    def register_user(self, username: str, user_type: UserType) -> None:
        """Register user in RLab platform"""
        self.users[username] = user_type
        print(f"✅ User '{username}' registered as {user_type.value}")
    
    def user_interaction(self, username: str, twin_id: str, action: str, data: Dict) -> None:
        """Handle user interaction with digital twin"""
        if username not in self.users:
            print(f"❌ User '{username}' not registered")
            return
        
        twin = self.root_twin.find_twin(twin_id) if self.root_twin else None
        if not twin:
            print(f"❌ Digital twin '{twin_id}' not found")
            return
        
        user_type = self.users[username]
        twin.twin.log_interaction(user_type.value, action, data)
        
        print(f"✅ {user_type.value} '{username}' performed '{action}' on '{twin.name}'")
    
    def add_learning_module(self, lab_name: str, module_name: str, content: Dict) -> None:
        """Add learning module to robotics lab"""
        lab = self.root_twin.find_twin(lab_name) if self.root_twin else None
        if not lab:
            print(f"❌ Lab '{lab_name}' not found")
            return
        
        # Add learning module as a component
        component_factory = self.factories[DigitalTwinType.COMPONENT]
        module_twin = component_factory.create_digital_twin(module_name)
        
        lab.add_child(module_twin)
        module_twin.model.static_data.update(content)
        
        print(f"✅ Learning module '{module_name}' added to lab '{lab_name}'")
    
    def create_research_project(self, project_name: str, researchers: List[str]) -> DigitalTwin:
        """Create research project digital twin"""
        product_factory = self.factories[DigitalTwinType.PRODUCT]
        project_twin = product_factory.create_digital_twin(project_name)
        
        project_twin.model.static_data.update({
            "type": "research_project",
            "researchers": researchers,
            "start_date": datetime.now().isoformat(),
            "status": "active"
        })
        
        if self.root_twin:
            self.root_twin.add_child(project_twin)
        
        print(f"✅ Research project '{project_name}' created with researchers: {researchers}")
        return project_twin
    
    def generate_coe_report(self) -> Dict:
        """Generate COE compliance report"""
        if not self.root_twin:
            return {"error": "RLab platform not initialized"}
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "scheme": "COE",
            "components": [],
            "total_allocation": 0,
            "utilization": {}
        }
        
        def collect_components(twin: DigitalTwin):
            if twin.type == DigitalTwinType.ASSET:
                component_data = {
                    "name": twin.name,
                    "type": twin.model.static_data.get("asset_type", "unknown"),
                    "cost": twin.model.static_data.get("cost", 0),
                    "coe_component": twin.model.static_data.get("coe_component", "ATL Consumables")
                }
                report["components"].append(component_data)
                report["total_allocation"] += component_data["cost"]
            
            for child in twin.children:
                collect_components(child)
        
        collect_components(self.root_twin)
        
        # Calculate utilization
        total_users = len(self.users)
        active_assets = len([c for c in report["components"] if c.get("cost", 0) > 0])
        
        report["utilization"] = {
            "total_users": total_users,
            "active_assets": active_assets,
            "user_distribution": {ut.value: 0 for ut in UserType}
        }
        
        for user_type in self.users.values():
            report["utilization"]["user_distribution"][user_type.value] += 1
        
        return report