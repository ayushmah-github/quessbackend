"""
Exception handling and custom exceptions for HRMS API
"""
from fastapi import HTTPException, status


class EmployeeNotFound(HTTPException):
    """Exception raised when employee is not found"""
    def __init__(self, employee_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )


class DuplicateEmployee(HTTPException):
    """Exception raised for duplicate employee"""
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with {field} '{value}' already exists"
        )


class AttendanceNotFound(HTTPException):
    """Exception raised when attendance record is not found"""
    def __init__(self, attendance_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record '{attendance_id}' not found"
        )


class InvalidDataError(HTTPException):
    """Exception raised for invalid data"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
