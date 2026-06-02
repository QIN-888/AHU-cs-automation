---
name: datastudio-sql-automation
description: >
  Data Studio（GaussDB 客户端）自动化 SQL 执行+截图工作流。使用 pyautogui + pyperclip
  控制 Data Studio 窗口，批量执行 .sql 文件并截图保存结果。触发条件：用户提到"Data Studio"、
  "批量执行 SQL"、"自动查询"、"截图保存结果"、"GaussDB"、"AhuDB"等关键词，或需要在
  Data Studio 中自动化运行 SQL 查询时。
---

# Data Studio SQL 自动化查询+截图

通过 pyautogui 桌面自动化和 pyperclip 剪贴板，在 Data Studio（GaussDB 客户端）中
自动执行 SQL 并截图保存查询结果。

## 架构概述

不使用任何插件/API，纯粹通过桌面 GUI 自动化：
- **pyautogui** — 窗口激活、鼠标点击、键盘快捷键
- **pyperclip** — Unicode 安全剪贴板操作（中文不乱码）
- **截图** — `pyautogui.screenshot()` 直接截取屏幕

## 依赖

```bash
pip install pyautogui pyperclip
```

- Data Studio 客户端 + GaussDB 数据库连接
- 千问视觉模型（DashScope）用于截图结果分析（可选）

## 核心脚本

项目中有两个脚本，优先使用 `query_runner.py`（pyperclip 版，中文无乱码）：

| 脚本 | 剪贴板方式 | 中文支持 | 推荐 |
|------|-----------|---------|------|
| `scripts/query_runner.py` | pyperclip | ✅ 完美 | **首选** |
| `scripts/run_query.py` | clip.exe | ❌ GBK 乱码 | 备用 |

## 执行流程

```
步骤1: 激活 Data Studio 窗口
  wins = pyautogui.getWindowsWithTitle('Data Studio : AhuDB2026')
  wins[0].restore() → activate() → maximize()

步骤2: 设置搜索路径（schema）
  在 Data Studio 中先执行：SET search_path = "SPJ1144", public;
  ← 必须先设路径，否则表找不到！每个查询会话开头都要设。
  pyperclip.copy('SET search_path = "SPJ1144", public;')
  → 粘贴 → 点击执行 → 等待完成

步骤3: 读取 .sql 文件（UTF-8 编码）
  with open(sql_file, 'r', encoding='utf-8') as f:
      query = f.read()

步骤4: 复制到剪贴板（必须用 pyperclip！）
  pyperclip.copy(query)

步骤5: 粘贴到 SQL 编辑器
  click(编辑器区) → Ctrl+A → Delete → Ctrl+V
  ← 三步缺一不可，不能省略 Delete！

步骤6: 点击执行按钮（Data Studio 不支持 F5！）
  pyautogui.click(execute_btn_x, execute_btn_y)

步骤7: 处理错误弹窗
  time.sleep(2) → pyautogui.press('enter')

步骤8: 在桌面创建截图文件夹 → 截图保存
  文件夹命名：C:\Users\23692\Desktop\<查询批次名>_screenshots\
  如果文件夹不存在则创建，然后截图保存到该文件夹

步骤9: 检查截图是否查空（表为空）
  截图后用 read_image 分析结果，如果表里没有数据（空表、0行）
  → 说明查错表了、表不存在或表未导入数据 → 确认正确的表名 → 修改 SQL → 重新执行步骤3-8
  ← 查空不跳过，必须查到正确的表有数据为止！
```

## 关键踩坑（必读）

### 0. 设置搜索路径 — 查询前必做
每次查询前必须先在 Data Studio 中执行：
```sql
SET search_path = "SPJ1144", public;
```
如果不设 search_path，表名不带 schema 前缀会报"关系不存在"错误。
即使 SQL 文件中写了完整前缀 `"SPJ1144"."j1144"`，也建议先设 search_path 保底。

### 1. 中文编码 — 最坑的坑
`clip.exe` 使用 **GBK** 编码，"螺丝刀" 会变成 "铻轰笣鍒"。
**必须使用 `pyperclip.copy()`**，它正确处理 Unicode。

### 2. 执行按钮坐标
Data Studio **不支持 F5 快捷键**执行查询，必须鼠标点击执行按钮。
获取坐标的方法：让用户将鼠标悬停在执行按钮上，运行：
```python
import pyautogui
print(pyautogui.position())  # 记录坐标作为 EXECUTE_BTN
```

### 3. 窗口激活
每次查询前**必须**重新激活 Data Studio 窗口，否则粘贴操作会落到
VS Code 或其他活跃窗口。处理窗口最小化状态：
```python
def activate_datastudio():
    for attempt in range(3):
        wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio : AhuDB2026')]
        if wins:
            w = wins[0]
            if w.left <= -32000 or w.top <= -32000:  # 最小化检测
                w.restore()
                time.sleep(0.5)
            w.activate()
            time.sleep(0.3)
            return True
        time.sleep(0.5)
    return False
```

### 4. 清空编辑器三步曲
`Ctrl+A` → `Delete` → `Ctrl+V` 三步不可省略 Delete 步骤。
如果不清空直接粘贴，新 SQL 会追加到旧内容后面导致语法错误。

### 5. 错误弹窗
查询执行失败时会弹出错误对话框，按 `Enter` 键关闭。
建议执行后等 2 秒按一次 Enter，再等 3 秒按一次（双重保险）。

### 6. pname 空格问题
数据库 `pname` 字段的值可能包含空格（如 `"螺丝 刀"`），
SQL 比较时用 `REPLACE(pname, ' ', '')` 去除空格再比较。

### 7. 查空（表为空）必须重查
截图后用千问视觉模型分析结果。如果表里没有数据（空表、0 rows、列头下面没有行），
说明查错表了或表未导入数据，**必须找到正确的表名，修正 SQL 重新执行**。
只有查到表里有数据才算通过，不能跳过。

## 截图结果分析

使用千问视觉模型（DashScope）分析截图：
```bash
C:\Users\23692\.claude\skills\.venv\Scripts\python.exe \
  C:\Users\23692\.claude\skills\media-tools\scripts\read_image.py \
  --path <截图路径> \
  --prompt "请详细描述这张截图中的查询结果，包括所有数据、行数等细节。" \
  --max-tokens 2048 \
  --provider dashscope
```

**注意**：图片分析使用 `--prompt` 直接传参，不要用 `--prompt-file`（有 bug）。

## 完整脚本模板

```python
import pyautogui
import pyperclip
import time
import sys
import os
import subprocess
from datetime import datetime

# 执行按钮坐标 — 用 pyautogui.position() 实际测量
EXECUTE_BTN = (436, 143)

# 编辑器点击位置
EDITOR_CLICK = (900, 450)

# 截图保存目录（桌面上的批次文件夹，自动创建）
BATCH_NAME = 'batch1'  # 每次查询批次修改名称
SCREENSHOT_DIR = f'c:/Users/23692/Desktop/{BATCH_NAME}_screenshots/'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 数据库搜索路径
SEARCH_PATH = 'SET search_path = "SPJ1144", public;'

# 千问读图工具路径（用于查空分析）
READ_IMAGE_PYTHON = r'C:\Users\23692\.claude\skills\.venv\Scripts\python.exe'
READ_IMAGE_SCRIPT = r'C:\Users\23692\.claude\skills\media-tools\scripts\read_image.py'


def activate_datastudio():
    """激活 Data Studio 窗口，处理最小化状态"""
    for attempt in range(3):
        wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio : AhuDB2026')]
        if wins:
            w = wins[0]
            if w.left <= -32000 or w.top <= -32000:
                w.restore()
                time.sleep(0.5)
            w.activate()
            time.sleep(0.3)
            return True
        time.sleep(0.5)
    print("  WARNING: Data Studio not found!")
    return False


def check_if_empty(screenshot_path):
    """用千问视觉模型检查截图中的表是否为空（表里没数据）"""
    result = subprocess.run(
        [READ_IMAGE_PYTHON, READ_IMAGE_SCRIPT,
         '--path', screenshot_path,
         '--prompt', '这张截图中的查询结果表是空的吗？表里有数据行吗？只回答"空"或"有数据"。',
         '--max-tokens', '50',
         '--provider', 'dashscope'],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    # 提取最后一行非标记行
    lines = [l for l in output.split('\n') if l.strip() and not l.startswith('[')]
    reply = lines[-1] if lines else ''
    return '空' in reply and '有数据' not in reply


def run_sql(query_text, screenshot_name, max_retries=3):
    """执行 SQL 并截图，查空则重查"""
    for attempt in range(max_retries):
        if not activate_datastudio():
            print("ERROR: Data Studio not found")
            return None
        time.sleep(0.5)

        # 先设置搜索路径
        pyperclip.copy(SEARCH_PATH)
        time.sleep(0.2)
        pyautogui.click(*EDITOR_CLICK)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.click(*EXECUTE_BTN)
        print("  Set search_path")
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(0.3)

        # 粘贴查询 SQL
        pyperclip.copy(query_text)
        time.sleep(0.2)
        pyautogui.click(*EDITOR_CLICK)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        # 执行
        pyautogui.click(*EXECUTE_BTN)
        print(f"  Exec: {screenshot_name} (attempt {attempt+1}/{max_retries})")

        # 关闭错误弹窗
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(0.5)
        time.sleep(3)
        pyautogui.press('enter')
        time.sleep(0.5)

        # 截图
        fname = f'{SCREENSHOT_DIR}{screenshot_name}.png'
        pyautogui.screenshot(fname)
        print(f"  Screenshot: {fname}")

        # 检查是否查空（表为空）
        if check_if_empty(fname):
            print(f"  ⚠ 表为空，查错表了！重试...")
            continue  # 修改 SQL 后重试
        else:
            print(f"  ✅ 有数据，通过")
            return fname

    print(f"  ❌ 重试{max_retries}次后仍为空，放弃")
    return None


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        run_sql(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python query_runner.py <sql_file> <screenshot_name>")
```

## 使用方式

### 单文件执行
```bash
python scripts/query_runner.py query.sql result_screenshot_name
```

### 批量执行
遍历 .sql 文件目录，逐个调用 `run_sql_file()`，每次执行后 `time.sleep(2)` 等待
Data Studio 响应。

### 交互式获取执行按钮坐标
```bash
python -c "import pyautogui; print('3秒后将获取鼠标位置...'); import time; time.sleep(3); print(pyautogui.position())"
```
在 3 秒内将鼠标悬停在 Data Studio 执行按钮上。

## Windows 终端编码注意

Git Bash 下 Python 输出中文可能乱码，设置环境变量：
```bash
export PYTHONIOENCODING=utf-8
```
或在代码中：
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 粘贴到 VS Code 而非 Data Studio | 窗口未激活 | 调用 `activate_datastudio()` |
| 中文变成乱码 | 用了 clip.exe | 改用 pyperclip |
| 旧 SQL 未清除 | 省略了 Delete 步骤 | Ctrl+A → Delete → Ctrl+V |
| 执行无反应 | 坐标不对 | 重新用 pyautogui.position() 测量 |
| F5 无效 | Data Studio 不支持 | 必须鼠标点击执行按钮 |
| 截图全黑/空白 | 窗口最小化 | restore() + activate() |
