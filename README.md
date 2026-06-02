# 安徽大学计科作业自动化工具集

## Data Studio SQL 自动化

基于 pyautogui + pyperclip 的 Data Studio（GaussDB 客户端）自动化 SQL 执行+截图工具。

### 流程
1. 激活 Data Studio 窗口
2. 设置 search_path
3. 读取 .sql 文件
4. 粘贴到编辑器 → 执行
5. 截图保存到桌面文件夹
6. 千问视觉模型检查是否查空（表为空则重查）

### 使用方法
```bash
pip install pyautogui pyperclip
python datastudio-sql-automation/scripts/query_runner.py query.sql result_name
```

详见 [datastudio-sql-automation/SKILL.md](datastudio-sql-automation/SKILL.md)
