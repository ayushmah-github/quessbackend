"""
API Tests for HRMS
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date
from HrmsBackend.main import app
from HrmsBackend.database import SessionLocal
from HrmsBackend.models import Base, Employee, Attendance, AttendanceStatus

# Test client
client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Create a test database"""
    Base.metadata.create_all(bind=SessionLocal.kw['bind'])
    yield
    Base.metadata.drop_all(bind=SessionLocal.kw['bind'])


class TestHealth:
    """Health check endpoint tests"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestEmployees:
    """Employee endpoint tests"""
    
    def test_create_employee(self, db):
        """Test creating a new employee"""
        response = client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        assert response.status_code == 201
        assert response.json()["employee_id"] == "EMP001"
    
    def test_create_duplicate_employee_id(self, db):
        """Test creating employee with duplicate ID"""
        client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        
        response = client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "department": "Engineering"
        })
        assert response.status_code == 409
    
    def test_get_employees(self, db):
        """Test getting employees list"""
        client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        
        response = client.get("/api/employees")
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_delete_employee(self, db):
        """Test deleting an employee"""
        client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        
        response = client.delete("/api/employees/EMP001")
        assert response.status_code == 204
        
        # Verify employee is deleted
        response = client.get("/api/employees/EMP001")
        assert response.status_code == 404


class TestAttendance:
    """Attendance endpoint tests"""
    
    def test_mark_attendance(self, db):
        """Test marking attendance"""
        # Create employee first
        client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        
        response = client.post("/api/attendance", json={
            "employee_id": "EMP001",
            "date": "2026-02-02",
            "status": "Present"
        })
        assert response.status_code == 201
        assert response.json()["status"] == "Present"
    
    def test_mark_attendance_nonexistent_employee(self, db):
        """Test marking attendance for non-existent employee"""
        response = client.post("/api/attendance", json={
            "employee_id": "NONEXISTENT",
            "date": "2026-02-02",
            "status": "Present"
        })
        assert response.status_code == 404
    
    def test_get_attendance(self, db):
        """Test getting attendance records"""
        # Create employee and mark attendance
        client.post("/api/employees", json={
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        })
        
        client.post("/api/attendance", json={
            "employee_id": "EMP001",
            "date": "2026-02-02",
            "status": "Present"
        })
        
        response = client.get("/api/attendance")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestDashboard:
    """Dashboard endpoint tests"""
    
    def test_get_dashboard_stats(self, db):
        """Test getting dashboard statistics"""
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_employees" in data
        assert "total_departments" in data
        assert "today_present" in data
        assert "today_absent" in data
        assert "attendance_rate" in data
