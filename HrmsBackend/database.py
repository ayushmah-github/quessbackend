"""
Database configuration and management for HRMS
Supports SQLite (development) and PostgreSQL (production)
"""
import os
from typing import Generator
from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from HrmsBackend.models import Base

# ============== Database Configuration ==============

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hrms.db")

# Determine if using SQLite or PostgreSQL
IS_SQLITE = "sqlite" in DATABASE_URL.lower()
IS_POSTGRESQL = "postgresql" in DATABASE_URL.lower()

# ============== Engine Configuration ==============

if IS_SQLITE:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "False").lower() == "true",
    )
elif IS_POSTGRESQL:
    # PostgreSQL configuration (production)
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using
        echo=os.getenv("DEBUG", "False").lower() == "true",
    )
else:
    # Default to SQLite if not recognized
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "False").lower() == "true",
    )

# ============== Session Configuration ==============

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


# ============== Event Handlers ==============

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite"""
    if IS_SQLITE:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ============== Database Functions ==============

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables
    Call this on application startup
    """
    try:
        print("🔍 Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"✅ Database initialized successfully!")
            print(f"   Tables created: {', '.join(tables)}")
        else:
            print("⚠️  No tables created. Check configuration.")
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise


def create_all_tables() -> None:
    """Create all database tables"""
    try:
        print("📝 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        raise


def drop_all_tables() -> None:
    """Drop all database tables (USE WITH CAUTION)"""
    try:
        print("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {str(e)}")
        raise


def reset_database() -> None:
    """Reset database by dropping and recreating all tables"""
    try:
        print("🔄 Resetting database...")
        drop_all_tables()
        create_all_tables()
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        raise


def get_database_info() -> dict:
    """Get database information and statistics"""
    try:
        inspector = inspect(engine)
        
        db_info = {
            "database_url": DATABASE_URL,
            "database_type": "PostgreSQL" if IS_POSTGRESQL else "SQLite" if IS_SQLITE else "Unknown",
            "tables": inspector.get_table_names(),
            "table_count": len(inspector.get_table_names()),
        }
        
        # Get column information for each table
        tables_info = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            
            tables_info[table_name] = {
                "columns": len(columns),
                "column_names": [col["name"] for col in columns],
                "primary_keys": primary_keys.get("constrained_columns", []),
                "indexes": len(inspector.get_indexes(table_name)),
            }
        
        db_info["tables_info"] = tables_info
        
        return db_info
    except Exception as e:
        print(f"❌ Error getting database info: {str(e)}")
        return {"error": str(e)}


def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            if IS_POSTGRESQL:
                connection.execute(text("SELECT 1"))
            else:
                connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False


def get_session() -> Session:
    """Get a database session (alternative to Depends)"""
    return SessionLocal()


# ============== Database Health Check ==============

def health_check() -> dict:
    """Perform database health check"""
    try:
        is_connected = check_database_connection()
        info = get_database_info() if is_connected else None
        
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connected": is_connected,
            "database_type": "PostgreSQL" if IS_POSTGRESQL else "SQLite",
            "database_info": info,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


if __name__ == "__main__":
    """
    Utility script for database management
    Can be run directly: python -m HrmsBackend.database
    """
    print("HRMS Database Management Utility")
    print("=" * 50)
    print("\nAvailable functions:")
    print("  - init_db()              : Initialize database")
    print("  - create_all_tables()    : Create all tables")
    print("  - drop_all_tables()      : Drop all tables")
    print("  - reset_database()       : Reset database")
    print("  - get_database_info()    : Get database info")
    print("  - check_database_connection() : Check connection")
    print("  - health_check()         : Perform health check")
    print("\nDatabase URL:", DATABASE_URL)
    print("Database Type:", "PostgreSQL" if IS_POSTGRESQL else "SQLite")
    print("=" * 50)
