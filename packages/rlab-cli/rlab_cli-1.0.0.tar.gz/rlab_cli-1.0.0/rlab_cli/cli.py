#!/usr/bin/env python3
"""
RLab Platform Command Line Interface
"""

import json
from typing import Dict
from .platform import RLabPlatform, UserType

class RLabCLI:
    """Command Line Interface for RLab Platform"""
    
    def __init__(self):
        self.rlab = RLabPlatform()
        self.current_user = None
    
    def print_banner(self):
        """Print RLab banner"""
        banner = """
        ╔══════════════════════════════════════════════════╗
        ║                 RLab Platform CLI                ║
        ║      Digital Twins for Educational Robotics      ║
        ║              Powered by Nueroid                  ║
        ╚══════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_menu(self):
        """Show main menu"""
        menu = """
        Main Menu:
        1. Initialize RLab Facility
        2. User Management
        3. Robotics Lab Management
        4. Digital Twin Operations
        5. Learning & Research
        6. COE Reports
        7. System Information
        8. Exit
        
        Enter your choice (1-8): """
        return input(menu).strip()
    
    def handle_initialization(self):
        """Handle platform initialization"""
        name = input("Enter RLab facility name: ").strip()
        if not name:
            print("❌ Facility name cannot be empty")
            return
        
        self.rlab.initialize_rlab_facility(name)
    
    def handle_user_management(self):
        """Handle user registration and management"""
        print("\nUser Management:")
        print("1. Register User")
        print("2. List Users")
        print("3. Set Current User")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            username = input("Enter username: ").strip()
            print("Available user types:")
            for i, user_type in enumerate(UserType, 1):
                print(f"{i}. {user_type.value}")
            
            type_choice = input("Select user type (1-8): ").strip()
            try:
                user_type = list(UserType)[int(type_choice) - 1]
                self.rlab.register_user(username, user_type)
            except (ValueError, IndexError):
                print("❌ Invalid user type selection")
        
        elif choice == "2":
            print("\nRegistered Users:")
            for username, user_type in self.rlab.users.items():
                print(f"  - {username} ({user_type.value})")
        
        elif choice == "3":
            username = input("Enter username to set as current: ").strip()
            if username in self.rlab.users:
                self.current_user = username
                print(f"✅ Current user set to: {username}")
            else:
                print("❌ User not found")
    
    def handle_lab_management(self):
        """Handle robotics lab management"""
        print("\nLab Management:")
        print("1. Add Robotics Asset")
        print("2. List Labs and Assets")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            lab_name = input("Enter lab name: ").strip()
            asset_name = input("Enter asset name: ").strip()
            asset_type = input("Enter asset type (e.g., 'Vacuum Robot', 'ABB Cobot'): ").strip()
            cost = input("Enter asset cost (for COE): ").strip()
            
            asset_twin = self.rlab.add_robotics_asset(lab_name, asset_name, asset_type)
            if asset_twin and cost.isdigit():
                asset_twin.model.static_data["cost"] = int(cost)
                coe_component = input("Enter COE component (e.g., 'ATL Consumables', 'Digital Software'): ").strip()
                asset_twin.model.static_data["coe_component"] = coe_component
        
        elif choice == "2":
            if self.rlab.root_twin:
                self._print_hierarchy(self.rlab.root_twin)
            else:
                print("❌ RLab platform not initialized")
    
    def handle_digital_twin_operations(self):
        """Handle digital twin interactions"""
        if not self.current_user:
            print("❌ Please set current user first")
            return
        
        print("\nDigital Twin Operations:")
        print("1. List Available Twins")
        print("2. Interact with Twin")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1" and self.rlab.root_twin:
            self._print_hierarchy(self.rlab.root_twin)
        
        elif choice == "2":
            twin_id = input("Enter twin ID to interact with: ").strip()
            action = input("Enter action (e.g., 'control', 'monitor', 'configure'): ").strip()
            data_input = input("Enter action data (as JSON or text): ").strip()
            
            try:
                data = json.loads(data_input) if data_input.startswith('{') else {"message": data_input}
            except:
                data = {"message": data_input}
            
            self.rlab.user_interaction(self.current_user, twin_id, action, data)
    
    def handle_learning_research(self):
        """Handle learning modules and research projects"""
        print("\nLearning & Research:")
        print("1. Add Learning Module")
        print("2. Create Research Project")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            lab_name = input("Enter lab name: ").strip()
            module_name = input("Enter module name: ").strip()
            content = input("Enter module content description: ").strip()
            
            self.rlab.add_learning_module(lab_name, module_name, {"description": content})
        
        elif choice == "2":
            project_name = input("Enter project name: ").strip()
            researchers_input = input("Enter researcher usernames (comma-separated): ").strip()
            researchers = [r.strip() for r in researchers_input.split(",")]
            
            self.rlab.create_research_project(project_name, researchers)
    
    def handle_coe_reports(self):
        """Generate COE reports"""
        print("\nCOE Reports:")
        report = self.rlab.generate_coe_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"\n📊 COE Compliance Report")
        print(f"Generated: {report['generated_at']}")
        print(f"Total Allocation: ₹{report['total_allocation']:,}")
        
        print("\nComponents:")
        for component in report['components']:
            print(f"  - {component['name']}: ₹{component.get('cost', 0):,} ({component.get('coe_component', 'N/A')})")
        
        print(f"\nUtilization:")
        print(f"  Total Users: {report['utilization']['total_users']}")
        print(f"  Active Assets: {report['utilization']['active_assets']}")
        print("  User Distribution:")
        for user_type, count in report['utilization']['user_distribution'].items():
            if count > 0:
                print(f"    - {user_type}: {count}")
    
    def handle_system_info(self):
        """Show system information"""
        print("\nSystem Information:")
        print(f"RLab Initialized: {'Yes' if self.rlab.root_twin else 'No'}")
        print(f"Current User: {self.current_user or 'None'}")
        print(f"Total Users: {len(self.rlab.users)}")
        print(f"Total Labs: {len(self.rlab.robotics_labs)}")
        
        if self.rlab.root_twin:
            twin_count = self._count_twins(self.rlab.root_twin)
            print(f"Total Digital Twins: {twin_count}")
    
    def _print_hierarchy(self, twin, level: int = 0):
        """Print digital twin hierarchy"""
        from .core import DigitalTwin
        indent = "  " * level
        print(f"{indent}└── {twin.name} [{twin.type.value}] (ID: {twin.id})")
        
        for child in twin.children:
            self._print_hierarchy(child, level + 1)
    
    def _count_twins(self, twin) -> int:
        """Count all twins in hierarchy"""
        from .core import DigitalTwin
        count = 1  # Count self
        for child in twin.children:
            count += self._count_twins(child)
        return count
    
    def run(self):
        """Run the CLI application"""
        self.print_banner()
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    self.handle_initialization()
                elif choice == "2":
                    self.handle_user_management()
                elif choice == "3":
                    self.handle_lab_management()
                elif choice == "4":
                    self.handle_digital_twin_operations()
                elif choice == "5":
                    self.handle_learning_research()
                elif choice == "6":
                    self.handle_coe_reports()
                elif choice == "7":
                    self.handle_system_info()
                elif choice == "8":
                    print("👋 Thank you for using RLab Platform!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")