from sqlalchemy import Column, String, Date, ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date

Base = declarative_base()


class Employee(Base):
    """Employee model"""
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)

    # Relationship with Attendance
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.full_name}>"


class Attendance(Base):
    """Attendance model"""
    __tablename__ = "attendance"

    id = Column(String(50), primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True, default=date.today)
    status = Column(String(20), nullable=False)  # "Present" or "Absent"

    # Relationship with Employee
    employee = relationship("Employee", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance {self.employee_id} on {self.date}: {self.status}>"


class AttendanceStatus:
    """Constants for attendance status"""
    PRESENT = "Present"
    ABSENT = "Absent"
