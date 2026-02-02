"""
Utility functions for the HRMS API
"""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from HrmsBackend.models import Employee, Attendance, AttendanceStatus as ModelAttendanceStatus


def get_employee_by_id(db: Session, employee_id: str) -> Optional[Employee]:
    """Retrieve an employee by ID"""
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    """Retrieve an employee by email"""
    return db.query(Employee).filter(Employee.email == email).first()


def check_duplicate_employee_id(db: Session, employee_id: str) -> bool:
    """Check if employee ID already exists"""
    return db.query(Employee).filter(Employee.employee_id == employee_id).first() is not None


def check_duplicate_email(db: Session, email: str) -> bool:
    """Check if email already exists"""
    return db.query(Employee).filter(Employee.email == email).first() is not None


def get_attendance_record(db: Session, attendance_id: str) -> Optional[Attendance]:
    """Retrieve an attendance record by ID"""
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()


def generate_attendance_id(employee_id: str, attendance_date: date) -> str:
    """Generate a unique attendance ID"""
    return f"{employee_id}_{attendance_date.isoformat()}"


def get_employee_attendance_stats(employee: Employee) -> dict:
    """Calculate attendance statistics for an employee"""
    total_present = sum(
        1 for a in employee.attendance_records 
        if a.status == ModelAttendanceStatus.PRESENT
    )
    total_absent = sum(
        1 for a in employee.attendance_records 
        if a.status == ModelAttendanceStatus.ABSENT
    )
    
    total_records = len(employee.attendance_records)
    attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0
    
    return {
        "total_present": total_present,
        "total_absent": total_absent,
        "total_records": total_records,
        "attendance_rate": round(attendance_rate, 2)
    }


def get_today_attendance_summary(db: Session) -> dict:
    """Get today's attendance summary"""
    today = date.today()
    today_attendance = db.query(Attendance).filter(Attendance.date == today).all()
    
    today_present = sum(1 for a in today_attendance if a.status == ModelAttendanceStatus.PRESENT)
    today_absent = sum(1 for a in today_attendance if a.status == ModelAttendanceStatus.ABSENT)
    
    return {
        "today_present": today_present,
        "today_absent": today_absent,
        "total_today": len(today_attendance)
    }
