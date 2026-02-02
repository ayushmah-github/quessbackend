from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime

from HrmsBackend.database import get_db, init_db
from HrmsBackend.models import Employee, Attendance, AttendanceStatus as ModelAttendanceStatus
from HrmsBackend.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeWithAttendance,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceWithEmployee,
    DashboardStats,
    AttendanceStatus,
)

# Initialize FastAPI app
app = FastAPI(
    title="HRMS Lite API",
    description="A lightweight Human Resource Management System API",
    version="1.0.0",
)

# CORS middleware for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


# ============== Health Check ==============
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ============== Employee Routes ==============
@app.post(
    "/api/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"],
)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    # Check for duplicate employee_id
    existing_by_id = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
    if existing_by_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{employee.employee_id}' already exists",
        )

    # Check for duplicate email
    existing_by_email = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with email '{employee.email}' already exists",
        )

    db_employee = Employee(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        email=employee.email,
        department=employee.department,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.get("/api/employees", response_model=List[EmployeeResponse], tags=["Employees"])
def get_employees(
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
):
    """Get all employees with optional filters"""
    query = db.query(Employee)

    if department:
        query = query.filter(Employee.department == department)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Employee.full_name.ilike(search_term)) | (Employee.email.ilike(search_term))
        )

    return query.order_by(Employee.full_name).all()


@app.get("/api/employees/{employee_id}", response_model=EmployeeWithAttendance, tags=["Employees"])
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    """Get a single employee with their attendance records"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found",
        )

    # Calculate attendance stats
    total_present = sum(
        1 for a in employee.attendance_records if a.status == ModelAttendanceStatus.PRESENT
    )
    total_absent = sum(
        1 for a in employee.attendance_records if a.status == ModelAttendanceStatus.ABSENT
    )

    return EmployeeWithAttendance(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        email=employee.email,
        department=employee.department,
        attendance_records=[
            AttendanceResponse(
                id=a.id,
                employee_id=a.employee_id,
                date=a.date,
                status=a.status,
            )
            for a in sorted(employee.attendance_records, key=lambda x: x.date, reverse=True)
        ],
        total_present=total_present,
        total_absent=total_absent,
    )


@app.delete("/api/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Employees"])
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """Delete an employee and their attendance records"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found",
        )

    db.delete(employee)
    db.commit()
    return None


@app.get("/api/departments", response_model=List[str], tags=["Employees"])
def get_departments(db: Session = Depends(get_db)):
    """Get list of unique departments"""
    departments = db.query(Employee.department).distinct().all()
    return sorted([d[0] for d in departments])


# ============== Attendance Routes ==============
@app.post(
    "/api/attendance",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Attendance"],
)
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark attendance for an employee"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == attendance.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{attendance.employee_id}' not found",
        )

    # Create composite ID for attendance
    attendance_id = f"{attendance.employee_id}_{attendance.date.isoformat()}"

    # Check for existing attendance
    existing = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if existing:
        # Update existing attendance
        existing.status = attendance.status
        db.commit()
        db.refresh(existing)
        return AttendanceResponse(
            id=existing.id,
            employee_id=existing.employee_id,
            date=existing.date,
            status=existing.status,
        )

    # Create new attendance record
    db_attendance = Attendance(
        id=attendance_id,
        employee_id=attendance.employee_id,
        date=attendance.date,
        status=attendance.status,
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)

    return AttendanceResponse(
        id=db_attendance.id,
        employee_id=db_attendance.employee_id,
        date=db_attendance.date,
        status=db_attendance.status,
    )


@app.get("/api/attendance", response_model=List[AttendanceWithEmployee], tags=["Attendance"])
def get_attendance(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    status: Optional[AttendanceStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Get attendance records with optional filters"""
    query = db.query(Attendance).join(Employee)

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    if date_from:
        query = query.filter(Attendance.date >= date_from)

    if date_to:
        query = query.filter(Attendance.date <= date_to)

    if status:
        query = query.filter(Attendance.status == status)

    records = query.order_by(Attendance.date.desc()).all()

    return [
        AttendanceWithEmployee(
            id=a.id,
            employee_id=a.employee_id,
            date=a.date,
            status=a.status,
            employee_name=a.employee.full_name,
        )
        for a in records
    ]


@app.delete("/api/attendance/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Attendance"])
def delete_attendance(attendance_id: str, db: Session = Depends(get_db)):
    """Delete an attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record '{attendance_id}' not found",
        )

    db.delete(attendance)
    db.commit()
    return None


# ============== Dashboard Routes ==============
@app.get("/api/dashboard", response_model=DashboardStats, tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_employees = db.query(Employee).count()
    total_departments = db.query(Employee.department).distinct().count()

    today = date.today()
    today_attendance = db.query(Attendance).filter(Attendance.date == today).all()

    today_present = sum(1 for a in today_attendance if a.status == ModelAttendanceStatus.PRESENT)
    today_absent = sum(1 for a in today_attendance if a.status == ModelAttendanceStatus.ABSENT)

    # Calculate attendance rate
    if total_employees > 0:
        attendance_rate = (today_present / total_employees) * 100
    else:
        attendance_rate = 0.0

    return DashboardStats(
        total_employees=total_employees,
        total_departments=total_departments,
        today_present=today_present,
        today_absent=today_absent,
        attendance_rate=round(attendance_rate, 1),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)