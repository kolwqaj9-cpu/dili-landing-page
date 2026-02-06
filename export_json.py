import pandas as pd, struct, json, os, sys

# 设置输出编码为 UTF-8，避免 Windows GBK 编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def export():
    if not os.path.exists('sniper_results.bin'): 
        print("Warning: sniper_results.bin not found")
        return
    df = pd.read_csv('mlb_full_physics_vectors.csv')
    df = df[df['pitch_type'].isin(['FF','SI','SL','CU','CH'])].copy().reset_index(drop=True)
    with open('sniper_results.bin', 'rb') as f:
        n = struct.unpack('i', f.read(4))[0]
        res = [struct.unpack('ifi', f.read(12)) for _ in range(n)]
    df_res = pd.DataFrame(res, columns=['hit','score','reason'])
    final = pd.concat([df, df_res], axis=1)
    targets = final[final['hit']==1]
    chart_data = [[round(r.plate_x,3), round(r.plate_z,3), r.score, r.reason] for _, r in targets.iterrows()]
    total_targets = len(chart_data)
    max_points = 2000
    if len(chart_data) > max_points:
        step = max(1, len(chart_data) // max_points)
        chart_data = chart_data[::step][:max_points]
    payload = {
        "total_analyzed": len(final),
        "target_count": total_targets,
        "sample_count": len(chart_data),
        "top_reason": int(df_res.reason.mode()[0]),
        "data": chart_data
    }
    if not os.path.exists('static'): os.makedirs('static')
    with open('static/tactical_data.json', 'w', encoding='utf-8') as f: json.dump(payload, f)
    print("[OK] JSON conversion completed")
    print(f"Total analyzed: {payload['total_analyzed']}, Targets: {payload['target_count']}, Sampled: {payload['sample_count']}")
if __name__ == "__main__": export()