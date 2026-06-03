---
name: oj-auto-submit
description: >
  芒课(MOKIT)平台OJ自动答题。Playwright控制Edge浏览器，千问视觉识别验证码自动登录，
  从Homework/myCompetition入口查找进行中竞赛，编写C++解法（无注释）并自动提交验证满分。
  触发条件：用户提到"芒课"、"OJ"、"答题"、"提交"、"自动提交"、"mokit"、"做几道题"等。
---

# OJ Auto-Submit — 芒课 MOKIT 平台

自动完成芒课 OJ 平台 (www.mokit.top) 的编程题：自动登录 → 查找进行中作业 → 读题 → 写 C++ 解法 → 提交 → 验证满分。

## 技术栈

| 组件 | 用途 |
|------|------|
| **Python 3.12** | 脚本运行环境（Playwright 安装在此版本） |
| **Playwright** | 控制 Edge 浏览器，模拟用户操作 |
| **千问视觉 (DashScope)** | 识别登录验证码图片 |
| **C++** | 题目解答语言（无注释提交） |

## 环境路径

- **Python**: `C:\Users\23692\AppData\Local\Programs\Python\Python312\python.exe`
  - Git Bash: `/c/Users/23692/AppData/Local/Programs/Python/Python312/python.exe`
- **千问读图**: `C:\Users\23692\.claude\skills\.venv\Scripts\python.exe`
  - 脚本: `C:\Users\23692\.claude\skills\media-tools\scripts\read_image.py`

## 核心 URL

| 页面 | URL |
|------|-----|
| 登录 | `http://www.mokit.top/login` |
| **流程入口** | `http://www.mokit.top/Homework/myCompetition` |
| 竞赛题目列表 | `http://www.mokit.top/competition/competitionList/{competitionId}` |
| 单题详情 | `http://www.mokit.top/problem/program/{competitionId}/{problemId}` |

**注意**: 平台只支持 HTTP，非 HTTPS。

---

## 完整流程（7 步）

### 步骤 1：自动登录（含验证码识别）

导航到 `/login`，填写表单并识别验证码。

**表单元素选择器**:
| 字段 | 选择器 |
|------|--------|
| 账号 | `input[placeholder="账号"]` |
| 密码 | `input[placeholder="密码"]` |
| 验证码 | `input[placeholder="验证码"]` |
| 验证码图片 | `img.login-code-img`（截图后用千问识别） |
| 登录按钮 | `button:has-text("登 录")`（注意"登"和"录"之间有空格） |

**验证码识别流程**:
```python
# 1. 截图
captcha_el = page.query_selector(".login-code-img")
captcha_el.screenshot(path=tmpfile)

# 2. 千问识别
subprocess.run([read_image_py, read_image_script, "--path", tmpfile,
    "--prompt", "只输出验证码中的数字，不要其他任何内容。",
    "--max-tokens", "20", "--provider", "dashscope"],
    encoding='utf-8', errors='replace')

# 3. 填写 + 点击登录
u.fill(USERNAME); pwd.fill(PASSWORD); cap.fill(code)
page.query_selector('button:has-text("登 录")').click()
```

**关键注意事项**:
- `subprocess.run` 必须加 `encoding='utf-8', errors='replace'`，否则中文 Windows GBK 编码会崩溃
- 验证码实时生成，每次必须重新截图识别
- **重试机制**: 登录失败时重新 `page.goto("/login")` 获取新的验证码，最多重试 5 次
- 每次重试必须重新 `query_selector` 所有元素（页面刷新后旧引用失效）

### 步骤 2：查找进行中的作业

导航到 `Homework/myCompetition`，**等待 Vue 表格渲染完成**，然后点击活动名单的"查看"按钮。

```python
page.goto("http://www.mokit.top/Homework/myCompetition")
page.wait_for_selector("table tr td", timeout=10000)  # 等待 Vue 动态表格渲染
```

**⚠️ 关键坑："查看"是 `<button>` 不是 `<a>`！**
```python
# 错误写法 — 永远找不到！
view_btn = row.query_selector('a:has-text("查看")')

# 正确写法 — Element UI 按钮
view_btn = row.query_selector('button:has-text("查看")')
# HTML: <button class="el-button el-button--success el-button--small"><span>查看 </span></button>
```

点击后页面通过 Vue Router 切换到竞赛列表（URL 不变，DOM 更新）。

**只做进行中的竞赛**: 解析表格，操作栏显示"查看题目"的是进行中，"结束"的是已截止，跳过已截止。

```python
rows = page.query_selector_all("table tr")
for row in rows:
    cells = row.query_selector_all("td")
    if cells[0].inner_text().strip().isdigit():
        ops = cells[6].inner_text().strip()  # 操作栏
        if "查看题目" in ops:
            # 进行中！
        elif "结束" in ops:
            # 已截止，跳过
```

### 步骤 3：解析题目列表

导航到竞赛列表页，读取题目表格：

| 列索引 | 内容 | 示例 |
|--------|------|------|
| 1 | 题号 | `2228` |
| 2 | 名称 | `例17.11 01背包问题` |
| 4 | 满分 | `100` |
| 5 | 实际得分 | `100`（空表示未提交） |

```python
for row in rows:
    cells = row.query_selector_all("td")
    pid = cells[1].inner_text().strip()
    name = cells[2].inner_text().strip()
    max_score = cells[4].inner_text().strip()
    actual_score = cells[5].inner_text().strip()
```

### 步骤 4-6：逐题处理（读题 → 解题 → 提交 → 验证100分 → 下一题）

**这是最核心的流程。每道题必须串行处理：读到题目后才能编写解法，提交后必须验证拿到 100 分才能做下一题。不能批量读题或批量提交。**

```python
for prob in unsolved_problems:
    # 4a. 导航到题目页，读取题目描述
    prob_url = f"http://www.mokit.top/problem/program/{competitionId}/{prob['id']}"
    page.goto(prob_url)
    body = page.inner_text("body")

    # 4b. Claude 根据题目描述编写 C++ 解法（无注释，直接提交用）

    # 5. 提交代码
    page.select_option('#language', label='C++')
    page.evaluate('''(code) => {
        const cm = document.querySelector(".CodeMirror");
        if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(code); }
    }''', code)

    # 提交 + 等待 + 卡死重试（最多3次）
    for retry in range(3):
        page.query_selector("button.submit-allow").click()
        try:
            page.wait_for_function('''() => {
                const t = document.body.innerText;
                return t.includes("Judge End") || t.includes("TotalScore");
            }''', timeout=30000)
            break  # 评测完成
        except:
            body = page.inner_text("body")
            if "评判中" in body or "等待中" in body:
                page.reload()  # 刷新重试
                time.sleep(3)
                page.select_option('#language', label='C++')
                page.evaluate('''(code) => { ... }''', code)

    # 6. 验证得分：必须100分才能做下一题
    page.goto(comp_url)
    actual_score = 读取表格第6列
    if actual_score != "100":
        分析错误原因 → 修改代码 → 回到步骤5重新提交
        # 如果多次尝试仍非100分，暂停询问用户
    else:
        continue  # 满分，下一题
```

**关键约束**：
- **禁止批量读题**：每次只能看到当前题目，因为题目各不相同
- **禁止批量提交**：必须当前题拿到 100 分才能开启下一题
- **如非满分**：分析原因（编译错误/答案错误/运行错误），修改代码重新提交，多次失败则询问用户

---

## 平台技术要点汇总

| 要点 | 说明 |
|------|------|
| **协议** | HTTP（非 HTTPS） |
| **前端框架** | Vue.js + Element UI |
| **导航方式** | Vue Router SPA（URL 不变，DOM 替换） |
| **代码编辑器** | CodeMirror (`document.querySelector(".CodeMirror").CodeMirror`) |
| **语言选择** | `<select id="language">` |
| **提交按钮** | `button.submit-allow` |
| **登录方式** | 账号 + 密码 + 图片验证码 |
| **"查看"按钮** | `<button class="el-button--success el-button--small">`（不是 `<a>`！） |
| **编码** | 脚本需 `PYTHONIOENCODING=utf-8`，subprocess 需 `encoding='utf-8'` |

---

## 历史解答记录

### 竞赛 6863（7-动态规划）
| 题号 | 名称 | 算法 | 得分 |
|------|------|------|------|
| 2228 | 01背包问题 | 01背包 DP | 100 |
| 2242 | 合并石子 | 区间 DP（石子合并） | 100 |
| 2216 | 合唱队形 | 双向 LIS | 100 |
| 2219 | 最长上升子序列 | LIS O(N²) | 100 |
| 2214 | 挖地雷 | DAG 最长路 + 路径还原 | 100 |
| 2215 | 友好城市 | 排序 + LIS O(N log N) | 100 |

### 常见贪心题型（竞赛 6842 等）
| 题型 | 解法 |
|------|------|
| 书架 | 降序排列，累加至阈值 |
| 买笔最优方案 | 尽量买 4 元笔，调整余数 |
| Ride to Office | `t + 16200/v`，取 min + ceil |
| 删数问题 | 单调栈，注意 `while s>0 && !stack.empty()` |
| 均分纸牌 | 算平均，多余右移，计数非零移动 |
| 装箱问题 | 从大到小装箱，6×6 箱装各类盒子 |
