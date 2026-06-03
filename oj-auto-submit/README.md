# OJ Auto-Submit — 芒课 MOKIT 平台自动答题

[![Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://claude.ai/code)
[![Platform](https://img.shields.io/badge/Platform-mokit.top-orange)](http://www.mokit.top)
[![Language](https://img.shields.io/badge/Solution-C%2B%2B-00599C)](https://isocpp.org)

自动完成[芒课 OJ 平台](http://www.mokit.top)的编程作业：千问视觉识别验证码自动登录 → 查找进行中作业 → 逐题读题 → C++ 解题 → 提交 → 验证 100 分。

## 工作流

```
登录(验证码识别)
  ↓
Homework/myCompetition → 点击"查看"按钮
  ↓
查找进行中竞赛（跳过已截止）
  ↓
┌─────────────────────────────────┐
│  逐题循环（必须100分才能下一题）   │
│                                 │
│  读题 → 编写C++ → 提交          │
│    ↓                           │
│  等待评测(30s超时)              │
│    ├─ 100分 → 下一题            │
│    ├─ 非满分 → 修改重试          │
│    └─ 评判卡死 → 刷新重试(最多3次) │
└─────────────────────────────────┘
  ↓
全部满分 → 关闭浏览器
```

## 功能特性

- 🤖 **千问视觉验证码识别**：自动截图 → AI 识别 → 填写登录
- 🔄 **登录失败自动重试**：最多 5 次，每次重新获取验证码
- ⏱️ **评判卡死检测**：30 秒无响应自动刷新页面重新提交
- 📊 **满分验证**：提交后回到列表页对比实际得分，非 100 分自动修复
- 🎯 **只做进行中作业**：自动跳过已截止的竞赛

## 技术栈

| 组件 | 用途 |
|------|------|
| Python 3.12 + Playwright | 控制 Edge 浏览器 |
| 千问 DashScope (qwen3-vl) | 验证码 OCR 识别 |
| C++ | 题目解答语言 |
| Vue.js + Element UI | 目标平台前端框架 |
| CodeMirror | 平台代码编辑器 |

## 平台关键选择器

| 目标 | 选择器 |
|------|--------|
| 账号输入框 | `input[placeholder="账号"]` |
| 密码输入框 | `input[placeholder="密码"]` |
| 验证码输入框 | `input[placeholder="验证码"]` |
| 验证码图片 | `img.login-code-img` |
| 登录按钮 | `button:has-text("登 录")` |
| 名单"查看"按钮 | `button:has-text("查看")` ⚠️ 是 `<button>` 不是 `<a>` |
| 语言选择 | `select#language` |
| 提交按钮 | `button.submit-allow` |
| CodeMirror | `document.querySelector(".CodeMirror").CodeMirror` |

## 已知竞赛记录

### 6863 — 7-动态规划（600/600）
| 题号 | 名称 | 算法 | 得分 |
|------|------|------|:--:|
| 2228 | 01背包问题 | 01背包 DP | 100 |
| 2242 | 合并石子 | 区间 DP | 100 |
| 2216 | 合唱队形 | 双向 LIS | 100 |
| 2219 | 最长上升子序列 | LIS O(N²) | 100 |
| 2214 | 挖地雷 | DAG 最长路 + 路径还原 | 100 |
| 2215 | 友好城市 | 排序 + LIS O(N log N) | 100 |

## ⚠️ 常见坑

1. **"查看"按钮不是 `<a>` 标签** — 是 Element UI 的 `<button class="el-button--success el-button--small">`
2. **Vue SPA 渲染延迟** — 页面 `domcontentloaded` 后表格可能还没画出来，必须 `wait_for_selector("table tr td")`
3. **验证码实时变化** — 每次登录必须重新截图识别，不能用缓存的图片
4. **subprocess 编码** — 中文 Windows 下必须 `encoding='utf-8', errors='replace'`
5. **HTTP 非 HTTPS** — 平台只支持 HTTP 协议
6. **评判可能卡死** — 页面一直显示"评判中"时刷新页面重新提交

## 安装与使用

1. 确保已安装 Python 3.12 和 Playwright
2. 配置 DashScope API Key 环境变量
3. 在 Claude Code 中触发：`帮我做芒课OJ的题` 或 `/oj-auto-submit`

## 许可

MIT License
