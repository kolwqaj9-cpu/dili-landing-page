import pandas as pd
import struct

# 1. 定义球种
PITCH_MAP = {'FF': 0, 'SI': 1, 'SL': 2, 'CU': 3, 'CH': 4}

# 2. 读取数据
print("🚀 读取数据中...")
df = pd.read_csv('mlb_full_physics_vectors.csv')
df = df[df['pitch_type'].isin(PITCH_MAP.keys())].copy()

# 填充缺失值
cols = ['release_speed', 'release_spin_rate', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'plate_x', 'plate_z']
for c in cols:
    df[c] = df[c].fillna(df[c].mean())

# 3. 打包 (VERSION 3.0)
# 格式: int(type) + 10个float + int(label)
# 新增了 plate_x, plate_z
data_bytes = bytearray()
data_bytes.extend(struct.pack('i', len(df)))

print(f"📦 正在打包 {len(df)} 行 (含进垒坐标)...")

count = 0
for index, row in df.iterrows():
    evt = str(row.get('events', ''))
    desc = str(row.get('description', ''))
    
    # 判定 Hit
    is_hit = 1 if evt in ['single', 'double', 'triple', 'home_run'] else 0
    
    p_type = PITCH_MAP.get(row['pitch_type'], 0)
    
    try:
        # 注意：这里是 10 个 'f'
        packed = struct.pack('iffffffffffi', 
                             int(p_type),                  
                             float(row['release_speed']),  
                             float(row['release_spin_rate']), 
                             float(row['vx0']), float(row['vy0']), float(row['vz0']), 
                             float(row['ax']), float(row['ay']), float(row['az']),
                             float(row['plate_x']), float(row['plate_z']), # 新增坐标
                             int(is_hit))                  
        data_bytes.extend(packed)
        count += 1
    except Exception as e:
        continue

with open('mlb_physics_full.bin', 'wb') as f:
    f.write(data_bytes)

print(f"✅ Version 3.0 数据包已生成: mlb_physics_full.bin ({count} 行)")