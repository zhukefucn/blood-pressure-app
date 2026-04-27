from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class BloodPressureRecord(BaseModel):
    id: Optional[int] = None
    record_date: date  # 记录日期
    measurement_time: str  # 测量时段: morning, noon, evening
    systolic: int  # 收缩压（高压）
    diastolic: int  # 舒张压（低压）
    pulse: int  # 脉搏
    notes: Optional[str] = None  # 备注

class BloodPressureCreate(BaseModel):
    record_date: str
    measurement_time: str
    systolic: int
    diastolic: int
    pulse: int
    notes: Optional[str] = None

class BloodPressureUpdate(BaseModel):
    record_date: Optional[str] = None
    measurement_time: Optional[str] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    pulse: Optional[int] = None
    notes: Optional[str] = None

class Statistics(BaseModel):
    total_records: int
    avg_systolic: float
    avg_diastolic: float
    avg_pulse: float
    max_systolic: int
    min_systolic: int
    max_diastolic: int
    min_diastolic: int
