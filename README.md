# YYJio 任务包仓库

这里放的是 **YYJio（痒痒鸡）** 的自定义任务包 —— 一份 `.yyjio-task` 就是一个「自定义点击」方案（含参考画面、目标图案、点击区域与各层参数），别人下载后可以直接加到自己的编排表里。

## 怎么用（普通用户）

1. 打开 YYJio → 任务编排 → 添加任务 → 分类选 **自定义任务**
2. 点 **在线刷新**，列表里挑一个装；或者点 **从文件导入**，选下载好的 `.yyjio-task`
3. 装好后卡片上点 **加到编排**，就进了当前编排表

## 怎么发布（作者）

```bash
# 1. 在 YYJio 里做好方案并保存
#    方案库 → 选中方案 → 导出 → 填作者 / 版本 / 简介
#    （导出的 .yyjio-task 会下载到本地，清单条目会复制到剪贴板）

# 2. 放进本仓库的 packages/ 目录，然后重建清单
python scripts/build_index.py

# 3. 提交
git add packages index.json && git commit -m "add: 任务名 v1.0.0" && git push
```

`scripts/build_index.py` 会扫描 `packages/*.yyjio-task`，读取每个包里的 `task.json`，算出 `sha256` 与大小，重写 `index.json`。**不要手改 index.json**，它是生成的。

## 目录

| 路径 | 说明 |
| --- | --- |
| `index.json` | 任务清单（YYJio 客户端「在线刷新」读的就是它） |
| `packages/*.yyjio-task` | 任务包本体（zip） |
| `covers/` | 预留：封面图（当前版本客户端不展示） |
| `scripts/build_index.py` | 重建清单的脚本 |

## 包格式

```
xxx.yyjio-task              # 就是一个 zip
├── task.json               # 元数据 + 方案（纯文本，可 diff）
└── assets/0001-*.png       # 参考画面 / 目标图案，JSON 里用 asset:<文件名> 引用
```

`task.json` 关键字段：

```json
{
  "format": "yyjio-task",
  "format_version": 1,
  "id": "author.name",
  "name": "方案名",
  "author": "作者",
  "version": "1.0.0",
  "date": "2026-11-17",
  "description": "一句话说明",
  "plan": { "name": "方案名", "timeout": 30, "steps": [ ... ] }
}
```

约束（客户端导入时会校验）：

- 坐标基于 **1280×720**，别的分辨率上的框选需要作者自己先改好
- 只允许声明式 JSON + PNG，解压后单包 ≤ 8 MB
- `id` 用小写字母数字与 `. _ -`，长度 3~49；同一 `id` 的新版本会覆盖旧版本（客户端会提示）
- `index.json` 里每个包带 `sha256`，客户端下载后会校验

## 说明

- 任务包只是「点击流程」，不含任何游戏数据或账号信息
- 引擎本体基于 [OAS / OnmyojiAutoScript](https://github.com/runhey/OAS)，GPL-3.0
- 本仓库只收录任务包，程序源码在 [TesBot/YYS-OAS-Bot](https://github.com/TesBot/YYS-OAS-Bot)
