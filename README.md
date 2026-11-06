# 全國都審綠化檢核工具（Taiwan Urban Design Review – Greening Checker）

單一 HTML、零安裝、離線可用。流程：① 選地區（22 縣市）→ ② 案件類型 → ③ 細節 → ④ 檢討。
依所選縣市與案件類型只顯示需要的欄位；每項判定附法規名稱、條號、版本與官方連結。

## 執行方式（Windows／Mac 皆可）
| 方式 | 適合 | 做法 |
|---|---|---|
| **A. 網頁版（GitHub Pages）** | 大多數使用者、跨平台、免安裝 | 開啟 `https://<帳號>.github.io/udr-greening-checker/`；Edge／Chrome 網址列右側「安裝應用程式」、Safari「加入 Dock」即可像桌面程式一樣開啟，離線也能用（PWA） |
| **B. 單檔離線版** | 無網路、內網、要傳檔案給別人 | 下載 `全國都審綠化檢核工具.html` 雙擊開啟（Windows 用 Edge／Chrome，Mac 用 Safari／Chrome） |
| C. 系統原生 App（Electron／Tauri） | 需要安裝檔、程式簽章者 | 目前不提供；Mac 需 Apple 公證、Windows 需程式碼簽章，維護成本高且功能無差異 |

`template_v2.html` 是模板，**不含資料，直接開啟會顯示提示**；請開啟 `全國都審綠化檢核工具.html` 或 `docs/index.html`。

## 檔案
| 檔案 | 用途 |
|---|---|
| `全國都審綠化檢核工具.html` | 交付給使用者的工具（內嵌法規資料） |
| `data.json` | 法規資料庫（維護者編輯的唯一來源） |
| `template_v2.html` | 工具模板（不可直接使用），`/*__DATA__*/` 由 build 注入 data.json |
| `update_laws.py` | `check` 檢查官方來源修正日期／`publish` 產出 laws-latest.json／`build` 重建 HTML |
| `laws-latest.json` | 發布給使用者的遠端更新檔（放 GitHub Raw / NAS） |
| `update-report.md` | check 的產出報告 |
| `docs/` | GitHub Pages 發布目錄：`index.html`（工具）、`laws-latest.json`、PWA 的 `manifest.webmanifest`／`sw.js`／圖示 |
| `pwa/` | PWA 來源檔 |

## 法規更新流程
1. `python update_laws.py check` → 看 `update-report.md` 中「疑似異動」「無法連線」項目。
2. 人工到官方頁面核對，修改 `data.json`（數值、條文、`ver`、`verified`）。
3. `python update_laws.py publish --version 2.1` → 產出 `laws-latest.json`，上傳到可公開存取且允許 CORS 的位置。
4. 使用者於工具「⚙ 法規資料／更新」填入網址 →「檢查並下載更新」；或直接「匯入法規 JSON 檔」。
5. 需要發新版 HTML 時：`python update_laws.py build`。

GitHub 範例：把 `laws-latest.json` 放在 repo 根目錄，網址為
`https://raw.githubusercontent.com/<org>/<repo>/main/laws-latest.json`（GitHub Raw 預設允許 CORS）。
也可在 `data.json` 的 `meta.updateUrl` 預填網址，build 後工具會自動帶入。

## data.json 結構
- `meta`：version、date、updateUrl、disclaimer
- `national`：建築技術規則 §298–305、綠化設計技術規範（Gi、Ai）、保水設計技術規範（Q 公式）
- `caseTypes`：案件類型清單
- `cities[]`：`id/name/region/level(full|partial|minimal)/mainLaw/laws[]/p`
  - `laws[]`：`title/ver/src/items[{art,text,verified}]` — 判定出處即由此查得
  - `p`：計算參數（coverClasses、treeCover、treeCountRule、soilGround、soilArtificial、折算係數、roofGreen、permeable、waterLambdaFactor、rain、udrThreshold…）；`null` 表示該縣市未訂，工具會改為要求使用者輸入細部計畫規定值
- `checklist`：都審檢核清單

## 限制
- 瀏覽器無法直接抓取政府法規網站（CORS／robots），因此更新採「維護者發布 JSON → 工具下載」模式。
- 標示「未查證」「假設值」者請以官方條文為準；本工具不構成法律意見。
