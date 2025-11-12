#!/usr/bin/env python3
"""
RLab Platform - Main Entry Point
"""

import sys
from .cli import RLabCLI
from .platform import RLabPlatform, UserType

def run_demo():
    """Run a demonstration of RLab with Nueroid"""
    print("🚀 Starting RLab with Nueroid Demo...")
    
    rlab = RLabPlatform()
    
    # Initialize platform
    rlab.initialize_rlab_facility("RIT Maharashtra RLab")
    
    # Register users
    rlab.register_user("admin_school", UserType.SCHOOL_ADMIN)
    rlab.register_user("dr_sharma", UserType.PROFESSOR)
    rlab.register_user("student_raj", UserType.STUDENT)
    rlab.register_user("industry_partner", UserType.INDUSTRY)
    
    # Add robotics assets
    vacuum_robot = rlab.add_robotics_asset("Main Robotics Lab", "AutoClean Vacuum Robot", "Cleaning Robot")
    vacuum_robot.model.static_data["cost"] = 200000
    vacuum_robot.model.static_data["coe_component"] = "ATL Consumables"
    
    abb_cobot = rlab.add_robotics_asset("Advanced Lab", "ABB Collaborative Robot", "Industrial Cobot")
    abb_cobot.model.static_data["cost"] = 500000
    abb_cobot.model.static_data["coe_component"] = "Digital Software/Hardware"
    
    # Add learning modules
    rlab.add_learning_module("Main Robotics Lab", "Introduction to Robotics", {
        "level": "beginner",
        "duration": "4 weeks",
        "topics": ["Basic programming", "Sensor integration", "Navigation algorithms"]
    })
    
    # Create research project
    rlab.create_research_project("AI-Powered Educational Robotics", ["dr_sharma", "student_raj"])
    
    # Generate report
    report = rlab.generate_coe_report()
    print("\n" + "="*50)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print(f"Total COE Allocation: ₹{report['total_allocation']:,}")
    print("="*50)

def main():
    """Main entry point for RLab CLI"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--demo', '-d']:
            run_demo()
            return
        elif sys.argv[1] in ['--help', '-h']:
            print_help()
            return
        elif sys.argv[1] in ['--version', '-v']:
            from . import __version__
            print(f"RLab CLI v{__version__}")
            return
    
    # Run interactive CLI
    cli = RLabCLI()
    cli.run()

def print_help():
    """Print help information"""
    help_text = """
RLab CLI - Digital Twins for Educational Robotics

Usage:
    rlab                   Start interactive CLI
    rlab --demo, -d        Run demonstration
    rlab --help, -h        Show this help message
    rlab --version, -v     Show version information

Features:
    • Complete digital twin framework using Nueroid
    • Educational robotics platform management
    • Multi-user support with role-based access
    • COE compliance reporting
    • Interactive command-line interface

For more information, visit:
https://github.com/Rosversity/rlab-cli
    """
    print(help_text)

if __name__ == "__main__":
    main()