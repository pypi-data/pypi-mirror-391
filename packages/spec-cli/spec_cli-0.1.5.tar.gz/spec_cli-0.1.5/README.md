## spec-cli

AI 规则仓库自动配置工具，用于下载和配置 airules 的规则文件

## 🚀 快速上手

### 前置条件

请确保你的环境满足以下条件：

* ✅  **Python** ：版本 >=3.8
* ✅  **AI 编程工具** ：Cursor 或 ClaudeCode

### 一键安装

在你的项目根目录打开终端，执行以下命令：

```bash
# 使用指定仓库中的规则文件
spec init --template-repository http://git.dev.sh.ctripcorp.com/ibu/airules.git
```

安装过程日志示例：

```
==========================================
  AI 规则仓库自动配置脚本
==========================================

[INFO] 目标安装目录: D:\Users\xxx\workspace\xxx\xxx\spec-dev\xxx
[INFO] 模板仓库地址: http://git.xxx.com/xxxx/airules.git

[INFO] 检查前置条件...
[INFO] 前置条件检查通过

请选择您使用的 AI 客户端工具：
1) Cursor
2) ClaudeCode

请输入选项 [1-2]: 1
[INFO] 您选择了: Cursor
[INFO] 开始下载规则仓库: http://git.xxx/xxx/xxxx.git
[WARNING] 临时目录已存在，正在清理...
[INFO] 仓库下载成功
[INFO] 目标配置目录: D:\Users\xxx\workspace\xxx\xxx\spec-dev\xxx\.cursor
[INFO] 正在拷贝 rules 文件夹...
[INFO] 正在拷贝 commands 文件夹...
[INFO] 文件拷贝完成！

[INFO] 配置文件已安装到: D:\Users\xxx\workspace\xxx\xxx\spec-dev\xxx\.cursor
[INFO]   - rules 目录: D:\Users\xxx\workspace\xxx\xxx\spec-dev\xxx\.cursor\rules
[INFO]   - commands 目录: D:\Users\xxx\workspace\xxx\xxx\spec-dev\xxx\commands
[INFO] 清理临时文件...

==========================================
[INFO] 配置完成！请重启您的 AI 工具以使配置生效
==========================================
```

### 安装结果

安装完成后，项目目录结构如下：

```
your-project/
└── .cursor/           # Cursor 配置目录
    ├── rules/         # 规则文件（上下文库）
    │   ├── common/          # 通用规范
    │   ├── languages/       # 编程语言
    │   ├── frameworks/      # 技术框架
    │   ├── project/         # 项目知识（需生成）
    │   └── workflow/        # 工作流定义
    └── commands/      # 斜杠命令
        ├── req.md           # /req 命令
        ├── tech.md          # /tech 命令
        ├── coding.md        # /coding 命令
        └── dev.md           # /dev 命令

```

### 验证安装

打开 Cursor，在对话框中输入 /，如果看到 /req、/tech、/coding、/dev 等命令，说明安装成功！
