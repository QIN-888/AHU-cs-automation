# 安徽大学计科作业自动化工具集

## OJ 自动答题

基于 Playwright + 千问视觉的芒课 OJ 平台全自动答题工具。验证码识别自动登录，逐题读题→C++ 解题→提交→验证 100 分，评判卡死自动刷新重试。

### 安装

```bash
cp -r AHU-cs-automation/oj-auto-submit ~/.claude/skills/
```

安装后在 Claude Code 中输入 `/oj-auto-submit` 或说"做芒课OJ的题"即可调用。

详见 [oj-auto-submit/SKILL.md](oj-auto-submit/SKILL.md)

---

## Data Studio SQL 自动化

基于 pyautogui + pyperclip 的 Data Studio（GaussDB 客户端）自动化 SQL 执行+截图工具。

### 安装

```bash
cp -r AHU-cs-automation/datastudio-sql-automation ~/.claude/skills/
```

安装后在 Claude Code 中输入 `/datastudio-sql-automation` 即可调用。

### 依赖

```bash
pip install pyautogui pyperclip
```

- Data Studio 客户端 + GaussDB 数据库连接
- 千问视觉模型（DashScope）用于查空校验（需 `DASHSCOPE_API_KEY` 环境变量）

### 执行流程

1. 激活 Data Studio 窗口
2. 设置 `search_path`
3. 读取 .sql 文件
4. 粘贴到编辑器 → 点击执行
5. 截图保存到桌面文件夹
6. 千问视觉检查是否查空（表为空则重查）

### 命令行使用

```bash
python datastudio-sql-automation/scripts/query_runner.py query.sql result_name
```

详见 [datastudio-sql-automation/SKILL.md](datastudio-sql-automation/SKILL.md)
