from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date, datetime, timedelta
from collections import defaultdict
from database import supabase
from models import BloodPressureRecord, BloodPressureCreate, BloodPressureUpdate, Statistics
import statistics

app = FastAPI(title="血压记录系统", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/records", response_model=BloodPressureRecord)
async def create_record(record: BloodPressureCreate):
    """创建血压记录"""
    try:
        data = {
            "record_date": record.record_date,
            "measurement_time": record.measurement_time,
            "systolic": record.systolic,
            "diastolic": record.diastolic,
            "pulse": record.pulse,
            "notes": record.notes
        }
        result = supabase.table("blood_pressure_records").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/records", response_model=List[dict])
async def get_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """获取血压记录列表"""
    try:
        query = supabase.table("blood_pressure_records").select("*")
        
        if start_date:
            query = query.gte("record_date", start_date)
        if end_date:
            query = query.lte("record_date", end_date)
        
        result = query.order("record_date", desc=True).order("measurement_time").limit(limit).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/records/{record_id}", response_model=dict)
async def get_record(record_id: int):
    """获取单条记录"""
    try:
        result = supabase.table("blood_pressure_records").select("*").eq("id", record_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="记录不存在")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/records/{record_id}", response_model=dict)
async def update_record(record_id: int, record: BloodPressureUpdate):
    """更新血压记录"""
    try:
        # 检查记录是否存在
        existing = supabase.table("blood_pressure_records").select("*").eq("id", record_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 只更新提供的字段
        update_data = record.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="没有要更新的字段")
        
        result = supabase.table("blood_pressure_records").update(update_data).eq("id", record_id).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int):
    """删除血压记录"""
    try:
        result = supabase.table("blood_pressure_records").delete().eq("id", record_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="记录不存在")
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/statistics", response_model=dict)
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取统计分析数据"""
    try:
        query = supabase.table("blood_pressure_records").select("*")
        
        if start_date:
            query = query.gte("record_date", start_date)
        if end_date:
            query = query.lte("record_date", end_date)
        
        result = query.execute()
        records = result.data
        
        if not records:
            return {
                "total_records": 0,
                "avg_systolic": 0,
                "avg_diastolic": 0,
                "avg_pulse": 0,
                "max_systolic": 0,
                "min_systolic": 0,
                "max_diastolic": 0,
                "min_diastolic": 0,
                "by_time": {}
            }
        
        systolic_list = [r["systolic"] for r in records]
        diastolic_list = [r["diastolic"] for r in records]
        pulse_list = [r["pulse"] for r in records]
        
        # 按时段统计
        by_time = defaultdict(lambda: {"count": 0, "systolic": [], "diastolic": [], "pulse": []})
        for r in records:
            time_key = r["measurement_time"]
            by_time[time_key]["count"] += 1
            by_time[time_key]["systolic"].append(r["systolic"])
            by_time[time_key]["diastolic"].append(r["diastolic"])
            by_time[time_key]["pulse"].append(r["pulse"])
        
        # 计算各时段平均值
        time_stats = {}
        time_labels = {"morning": "早晨", "noon": "中午", "evening": "晚上"}
        for time_key, data in by_time.items():
            time_stats[time_labels.get(time_key, time_key)] = {
                "count": data["count"],
                "avg_systolic": round(statistics.mean(data["systolic"]), 1),
                "avg_diastolic": round(statistics.mean(data["diastolic"]), 1),
                "avg_pulse": round(statistics.mean(data["pulse"]), 1)
            }
        
        return {
            "total_records": len(records),
            "avg_systolic": round(statistics.mean(systolic_list), 1),
            "avg_diastolic": round(statistics.mean(diastolic_list), 1),
            "avg_pulse": round(statistics.mean(pulse_list), 1),
            "max_systolic": max(systolic_list),
            "min_systolic": min(systolic_list),
            "max_diastolic": max(diastolic_list),
            "min_diastolic": min(diastolic_list),
            "by_time": time_stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trend")
async def get_trend(days: int = Query(30, le=365)):
    """获取趋势数据（最近N天）"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        result = supabase.table("blood_pressure_records")\
            .select("*")\
            .gte("record_date", start_date.isoformat())\
            .lte("record_date", end_date.isoformat())\
            .order("record_date")\
            .execute()
        
        # 按日期聚合
        daily_data = defaultdict(lambda: {"systolic": [], "diastolic": [], "pulse": []})
        for r in result.data:
            daily_data[r["record_date"]]["systolic"].append(r["systolic"])
            daily_data[r["record_date"]]["diastolic"].append(r["diastolic"])
            daily_data[r["record_date"]]["pulse"].append(r["pulse"])
        
        trend = []
        for d in sorted(daily_data.keys()):
            data = daily_data[d]
            trend.append({
                "date": d,
                "avg_systolic": round(statistics.mean(data["systolic"]), 1),
                "avg_diastolic": round(statistics.mean(data["diastolic"]), 1),
                "avg_pulse": round(statistics.mean(data["pulse"]), 1)
            })
        
        return trend
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
