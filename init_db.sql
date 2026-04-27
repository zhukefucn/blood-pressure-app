-- 血压记录表
CREATE TABLE IF NOT EXISTS blood_pressure_records (
    id SERIAL PRIMARY KEY,
    record_date DATE NOT NULL,
    measurement_time VARCHAR(20) NOT NULL,  -- morning, noon, evening
    systolic INTEGER NOT NULL CHECK (systolic > 0 AND systolic < 300),
    diastolic INTEGER NOT NULL CHECK (diastolic > 0 AND diastolic < 200),
    pulse INTEGER NOT NULL CHECK (pulse > 0 AND pulse < 300),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以加速查询
CREATE INDEX IF NOT EXISTS idx_record_date ON blood_pressure_records(record_date);
CREATE INDEX IF NOT EXISTS idx_measurement_time ON blood_pressure_records(measurement_time);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_blood_pressure_updated_at 
    BEFORE UPDATE ON blood_pressure_records 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 添加注释
COMMENT ON TABLE blood_pressure_records IS '血压记录表';
COMMENT ON COLUMN blood_pressure_records.systolic IS '收缩压（高压）';
COMMENT ON COLUMN blood_pressure_records.diastolic IS '舒张压（低压）';
COMMENT ON COLUMN blood_pressure_records.measurement_time IS '测量时段：morning/noon/evening';
