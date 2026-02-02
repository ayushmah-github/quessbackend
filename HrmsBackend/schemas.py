from pydantic import BaseModel, EmailStr, Field
from datetime import date as DateType
from typing import List, Optional, Literal
from enum import Enum


# Attendance Status Enum
class AttendanceStatus(str, Enum):
    """Attendance status enumeration"""
    PRESENT = "Present"
    ABSENT = "Absent"


# Employee Schemas
class EmployeeBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    model_config = {"from_attributes": True}


# Attendance Schemas - Simple, no inheritance issues
class AttendanceRecord(BaseModel):
    id: str
    employee_id: str
    date: DateType
    status: Literal["Present", "Absent"]
    
    model_config = {"from_attributes": True}


class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., min_length=1)
    date: DateType
    status: Literal["Present", "Absent"]


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    date: DateType
    status: Literal["Present", "Absent"]
    
    model_config = {"from_attributes": True}


class AttendanceWithEmployee(BaseModel):
    id: str
    employee_id: str
    date: DateType
    status: Literal["Present", "Absent"]
    employee_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


# Employee with Attendance - uses direct List typing
class EmployeeWithAttendance(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    attendance_records: List[AttendanceRecord] = []
    total_present: int = 0
    total_absent: int = 0
    
    model_config = {"from_attributes": True}


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_employees: int
    total_departments: int
    today_present: int
    today_absent: int
    attendance_rate: float


# Error Response
class ErrorResponse(BaseModel):
    detail: str