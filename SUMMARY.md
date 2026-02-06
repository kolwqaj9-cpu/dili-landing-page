# PropKit Netlify Deploy - Working State Summary

## 鉁?Working Dashboard Version (signals_dashboard.html)
- **Status**: Rendering confirmed
- **Key switches**:
  - `mock=1` URL param forces mock data rendering
  - `trigger=1` URL param triggers webhook compute
  - `debug=1` URL param shows debug info (email, timestamps, isFresh, timeDiff)
- **Freshness window**: 24 hours (86400000 ms)
- **Chart**: Re-inits ECharts instance to avoid cache issues

## 鉁?Current Deploy
- **Site ID**: 336e4b9a-6dd0-4686-8f79-78a8d0eab8be
- **Token**: stored in `.netlify_config.json`
- **Latest Deploy ID**: 6983ef2e8f37a4963cf95987
- **Local ZIP**: `netlify_deploy1_latest.zip`
- **Deploy script**: `deploy_to_netlify.py` (uploads 5 files only)

## 鉁?Minimal Files Uploaded
- `index.html`
- `checkout.html`
- `signals_dashboard.html`
- `privacy.html`
- `terms.html`

## 鉁?How To Test
- **Mock render**:
  - `https://propkitai.tech/signals_dashboard.html?id=YOUR_EMAIL&mock=1`
- **Trigger compute**:
  - `https://propkitai.tech/signals_dashboard.html?id=YOUR_EMAIL&trigger=1`
- **Debug info**:
  - `https://propkitai.tech/signals_dashboard.html?id=YOUR_EMAIL&debug=1`

## 鉁?Backend Notes
- `main.py` now writes `generated_at` into `data_payload`
- `export_json.py` samples chart points to max 2000, but keeps total counts

## 鉁?Local Services
- Start all: `鍚姩鏈嶅姟.bat`
- Manual:
  - Cloudflared: `cloudflared.exe tunnel --config config.yml run 3090-Home`
  - Python: `C:\ProgramData\Anaconda3\python.exe main.py`

## 鉁?Browser Install (Playwright)
- Background install loop active (if still running)
- Command: `C:\ProgramData\Anaconda3\python.exe -m playwright install chromium`
