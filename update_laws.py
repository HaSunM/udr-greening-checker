#!/usr/bin/env python3
"""
update_laws.py — 全國都審綠化檢核工具 法規異動檢查與資料發布腳本

用法：
  python update_laws.py check            # 逐一連線各法規來源，比對修正日期，輸出 update-report.md
  python update_laws.py publish          # 將 data.json 複製為 laws-latest.json（meta.date 更新為今天，version 可帶 --version 2.1）
  python update_laws.py build            # 以 template_v2.html + data.json 重建 全國都審綠化檢核工具.html

流程建議：
  1. 定期執行 check，閱讀 update-report.md 內標示「疑似異動」「無法連線」的法規。
  2. 人工至官方頁面核對條文，修改 data.json 內對應數值／條文／版本日期（verified 旗標）。
  3. 執行 publish 產出 laws-latest.json，放到可公開存取且允許 CORS 的位置（GitHub Raw、公司 NAS 網站）。
  4. 使用者在工具的「⚙ 法規資料／更新」填入該網址即可下載套用；或執行 build 重新產出內建新版 HTML。

注意：政府網站多數禁止機器抓取或需 JS 渲染，check 僅做「修正日期是否與記錄不同」的粗略提醒，不會自動改寫任何數值。
"""
import json, re, sys, datetime, urllib.request, urllib.error, shutil, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data.json')
DATE_RE = re.compile(r'(?:修正|發布|公[（(]?發[）)]?布|訂定|生效)日期[：:\s]*(?:民國)?\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日')
VER_RE = re.compile(r'(\d{2,3})\.(\d{2})\.(\d{2})')

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (law-update-check)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(400000)
    for enc in ('utf-8', 'big5', 'cp950'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', 'ignore')

def latest_date_in(html):
    ds = [(int(y), int(m), int(d)) for y, m, d in DATE_RE.findall(html)]
    return max(ds) if ds else None

def recorded_dates(ver):
    return [(int(y), int(m), int(d)) for y, m, d in VER_RE.findall(ver or '')]

def check():
    D = json.load(open(DATA, encoding='utf-8'))
    rows = []
    targets = [('中央', D['national']['scope']['src'], '建築技術規則 §298', ''), ('中央', D['national']['greenSpec']['src'], D['national']['greenSpec']['title'], '108.12.19'), ('中央', D['national']['waterSpec']['src'], D['national']['waterSpec']['title'], '108.12.19')]
    for c in D['cities']:
        for l in c['laws']:
            targets.append((c['name'], l['src'], l['title'], l.get('ver', '')))
    for name, url, title, ver in targets:
        status, found = '', None
        try:
            html = fetch(url)
            found = latest_date_in(html)
            if found is None: status = '無法辨識日期（可能為 PDF／JS 頁面）'
            else:
                rec = recorded_dates(ver)
                if rec and found > max(rec): status = '⚠ 疑似異動：來源日期 %d.%02d.%02d 晚於記錄 %s' % (found[0], found[1], found[2], ver)
                elif rec: status = '一致'
                else: status = '記錄無版本日期；來源 %d.%02d.%02d' % found
        except urllib.error.HTTPError as e: status = '無法連線 HTTP %s' % e.code
        except Exception as e: status = '無法連線：%s' % type(e).__name__
        rows.append((name, title, ver, url, status)); print(f'[{name}] {title} — {status}')
    out = os.path.join(HERE, 'update-report.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'# 法規異動檢查報告 {datetime.date.today()}\n\n| 縣市 | 法規 | 記錄版本 | 狀態 | 來源 |\n|---|---|---|---|---|\n')
        for name, title, ver, url, status in rows: f.write(f'| {name} | {title} | {ver} | {status} | {url} |\n')
    print('→', out)

def publish(version=None):
    D = json.load(open(DATA, encoding='utf-8'))
    D['meta']['date'] = datetime.date.today().isoformat()
    if version: D['meta']['version'] = version
    json.dump(D, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = os.path.join(HERE, 'laws-latest.json')
    json.dump(D, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('→', out, D['meta']['version'], D['meta']['date'])

def build():
    D = json.load(open(DATA, encoding='utf-8'))
    t = open(os.path.join(HERE, 'template_v2.html'), encoding='utf-8').read()
    out = os.path.join(HERE, '全國都審綠化檢核工具.html')
    open(out, 'w', encoding='utf-8').write(t.replace('/*__DATA__*/null', json.dumps(D, ensure_ascii=False)))
    print('→', out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'check': check()
    elif cmd == 'publish':
        v = None
        if '--version' in sys.argv: v = sys.argv[sys.argv.index('--version') + 1]
        publish(v)
    else: build()
