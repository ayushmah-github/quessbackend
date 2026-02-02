#!/usr/bin/env python3
"""
HRMS Database Management CLI
Provides utilities for database initialization, migration, and management
"""
import argparse
import sys
import os

# Add the backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from HrmsBackend.database import (
    init_db,
    create_all_tables,
    drop_all_tables,
    reset_database,
    get_database_info,
    check_database_connection,
    health_check,
    DATABASE_URL,
    IS_SQLITE,
    IS_POSTGRESQL,
)


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def cmd_init(args):
    """Initialize database"""
    print_header("Database Initialization")
    print_info(f"Database URL: {DATABASE_URL}")
    print_info(f"Database Type: {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}")
    
    try:
        init_db()
        print_success("Database initialized successfully!")
    except Exception as e:
        print_error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)


def cmd_create(args):
    """Create all tables"""
    print_header("Create Database Tables")
    print_info(f"Database URL: {DATABASE_URL}")
    
    try:
        create_all_tables()
        print_success("All tables created successfully!")
    except Exception as e:
        print_error(f"Failed to create tables: {str(e)}")
        sys.exit(1)


def cmd_drop(args):
    """Drop all tables"""
    print_header("Drop Database Tables")
    print_error("WARNING: This will delete all data from the database!")
    
    if not args.force:
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print_info("Operation cancelled.")
            return
    
    try:
        drop_all_tables()
        print_success("All tables dropped successfully!")
    except Exception as e:
        print_error(f"Failed to drop tables: {str(e)}")
        sys.exit(1)


def cmd_reset(args):
    """Reset database"""
    print_header("Reset Database")
    print_error("WARNING: This will delete all data and recreate the database!")
    
    if not args.force:
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print_info("Operation cancelled.")
            return
    
    try:
        reset_database()
        print_success("Database reset successfully!")
    except Exception as e:
        print_error(f"Failed to reset database: {str(e)}")
        sys.exit(1)


def cmd_info(args):
    """Get database information"""
    print_header("Database Information")
    
    try:
        info = get_database_info()
        
        if "error" in info:
            print_error(f"Error getting database info: {info['error']}")
            return
        
        print_info(f"Database URL: {info['database_url']}")
        print_info(f"Database Type: {info['database_type']}")
        print_info(f"Total Tables: {info['table_count']}")
        
        if info.get('tables'):
            print(f"\n📋 Tables ({len(info['tables'])}):")
            for table in info['tables']:
                print(f"   • {table}")
        
        if info.get('tables_info'):
            print("\n📊 Table Details:")
            for table_name, table_info in info['tables_info'].items():
                print(f"\n   Table: {table_name}")
                print(f"     Columns: {table_info['columns']}")
                print(f"     Column Names: {', '.join(table_info['column_names'])}")
                if table_info['primary_keys']:
                    print(f"     Primary Keys: {', '.join(table_info['primary_keys'])}")
                print(f"     Indexes: {table_info['indexes']}")
        
        print_success("Database information retrieved successfully!")
        
    except Exception as e:
        print_error(f"Failed to get database info: {str(e)}")
        sys.exit(1)


def cmd_check(args):
    """Check database connection"""
    print_header("Database Connection Check")
    
    try:
        is_connected = check_database_connection()
        
        print_info(f"Database URL: {DATABASE_URL}")
        print_info(f"Database Type: {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}")
        
        if is_connected:
            print_success("Database connection is working!")
        else:
            print_error("Database connection failed!")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Connection check failed: {str(e)}")
        sys.exit(1)


def cmd_health(args):
    """Perform database health check"""
    print_header("Database Health Check")
    
    try:
        result = health_check()
        
        status = result.get('status', 'unknown')
        connected = result.get('connected', False)
        db_type = result.get('database_type', 'Unknown')
        
        print_info(f"Database Type: {db_type}")
        print_info(f"Database URL: {DATABASE_URL}")
        
        if connected:
            print_success(f"Status: {status.upper()}")
            
            if result.get('database_info'):
                info = result['database_info']
                if 'table_count' in info:
                    print_info(f"Tables: {info['table_count']}")
                if 'tables' in info:
                    print_info(f"Table Names: {', '.join(info['tables'])}")
        else:
            print_error(f"Status: {status.upper()}")
            if 'error' in result:
                print_error(f"Error: {result['error']}")
                
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HRMS Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_db.py init              # Initialize database
  python manage_db.py create            # Create all tables
  python manage_db.py info              # Get database info
  python manage_db.py check             # Check connection
  python manage_db.py health            # Health check
  python manage_db.py drop --force      # Drop all tables (force)
  python manage_db.py reset --force     # Reset database (force)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    # Create command
    subparsers.add_parser('create', help='Create all tables')
    
    # Drop command
    drop_parser = subparsers.add_parser('drop', help='Drop all tables')
    drop_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database')
    reset_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Info command
    subparsers.add_parser('info', help='Get database information')
    
    # Check command
    subparsers.add_parser('check', help='Check database connection')
    
    # Health command
    subparsers.add_parser('health', help='Perform health check')
    
    args = parser.parse_args()
    
    # Route commands
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'create':
        cmd_create(args)
    elif args.command == 'drop':
        cmd_drop(args)
    elif args.command == 'reset':
        cmd_reset(args)
    elif args.command == 'info':
        cmd_info(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'health':
        cmd_health(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
