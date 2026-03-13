# cli-anything-godzilla

[English](README.md) | 简体中文

CLI 命令行工具包，用于哥斯拉（Godzilla）WebShell 管理器的安全测试。

## 功能特性

- **完整的项目管理** - 创建、打开、保存和管理哥斯拉项目
- **Shell 管理** - 添加、查看、更新、删除和测试 webshell 连接
- **C2 Profile 管理** - 加载和验证 C2 流量伪装配置
- **交互式 REPL 模式** - 提供友好的命令行交互界面
- **JSON 输出模式** - 支持 `--json` 标志，便于 AI 代理和脚本集成
- **短 ID 支持** - 所有 shell 命令支持使用短 ID 进行操作
- **兼容原版哥斯拉** - 可直接打开原版哥斯拉的项目数据库

## 安装

### 前置要求

- Python 3.12+ (已测试 Python 3.12.8)
- Java Runtime Environment (JRE) 11+
- 哥斯拉 JAR 文件 (Godzilla15.jar)

### 安装 CLI

```bash
# 从 PyPI 安装 (发布后)
pip install cli-anything-godzilla

# 或本地开发安装
cd /path/to/agent-harness
pip install -e .
```

### 验证安装

```bash
which cli-anything-godzilla
cli-anything-godzilla --help
```

## 使用方法

### 启动交互式 REPL 模式

```bash
# 无参数启动（进入 REPL 模式）
cli-anything-godzilla

# 指定项目启动
cli-anything-godzilla -p /path/to/project
```

### 项目管理

```bash
# 创建新项目
cli-anything-godzilla project new -n "我的项目" -d "项目描述"

# 打开已有项目
cli-anything-godzilla project open /path/to/project

# 查看项目信息
cli-anything-godzilla project info

# 列出所有项目
cli-anything-godzilla project list

# 关闭当前项目
cli-anything-godzilla project close
```

### Shell 管理

```bash
# 添加 shell
cli-anything-godzilla shell add -u http://target.com/shell.jsp -p password

# 列出所有 shell
cli-anything-godzilla shell list

# 获取 shell 详情（支持短 ID）
cli-anything-godzilla shell get 31f09e27

# 测试 shell 连接（支持短 ID）
cli-anything-godzilla shell test 31f09e27

# 更新 shell 配置
cli-anything-godzilla shell update 31f09e27 --remark "更新备注"

# 删除 shell（支持短 ID）
cli-anything-godzilla shell remove 31f09e27

# 导出 shell
cli-anything-godzilla shell export shells.json

# 导入 shell
cli-anything-godzilla shell import shells.json
```

### C2 Profile 管理

```bash
# 列出可用的 profiles
cli-anything-godzilla profile list

# 加载 profile
cli-anything-godzilla profile load /path/to/profile.yml

# 验证 profile
cli-anything-godzilla profile validate /path/to/profile.yml
```

### JSON 输出模式

所有命令支持 `--json` 标志，输出机器可读格式：

```bash
cli-anything-godzilla --json shell list
cli-anything-godzilla --json shell get 31f09e27
cli-anything-godzilla --json project info
```

## REPL 交互命令

在交互模式下，可使用以下命令：

| 命令 | 描述 |
|------|------|
| `help` | 显示可用命令 |
| `exit` | 退出 REPL 模式 |
| `project info` | 显示项目信息 |
| `project list` | 列出所有项目 |
| `shell list` | 列出所有 shell |
| `shell get <id>` | 获取 shell 详情 |
| `shell add <url> <password>` | 添加新 shell |
| `shell test <id>` | 测试 shell 连接 |
| `shell update <id> --remark "xxx"` | 更新 shell 备注 |
| `shell remove <id>` | 删除 shell |
| `profile list` | 列出 C2 profiles |

## 配置

### 项目配置

项目存储为 JSON 文件，结构如下：
```json
{
    "name": "项目名称",
    "description": "项目描述",
    "version": "1.0.0",
    "created": "2024-01-01T00:00:00",
    "modified": "2024-01-01T00:00:00",
    "default_payload": "JavaDynamicPayload",
    "default_cryption": "xor",
    "default_encoding": "UTF-8"
}
```

### Shell 配置

Shell 存储在 SQLite 数据库中，包含以下字段：
- **id** - 唯一标识符
- **url** - Shell URL
- **password** - Shell 密码
- **secret_key** - 加密密钥
- **payload** - 载荷类型
- **cryption** - 加密方式
- **encoding** - 字符编码
- **headers** - HTTP 请求头
- **proxy_type** - 代理类型
- **proxy_host** - 代理主机
- **proxy_port** - 代理端口

### 支持的载荷类型

- `JavaDynamicPayload` - Java 动态载荷
- `CSharpDynamicPayload` - C# 动态载荷
- `PhpDynamicPayload` - PHP 动态载荷

### 支持的加密方式

- `xor` - XOR 加密
- `aes128` - AES-128 加密
- `aes256` - AES-256 加密
- `base64` - Base64 编码
- `hex` - 十六进制编码
- `raw` - 原始数据
- `rsa` - RSA 加密

### C2 Profile 配置

C2 profiles 是 YAML 格式的流量伪装规则文件：
```yaml
supportPayload:
  - JavaDynamicPayload
  - CSharpDynamicPayload
  - PhpDynamicPayload
basicConfig:
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  urlParamName: "pass"
coreConfig:
  requestBodyType: "multipart/form-data"
  responseCharset: "UTF-8"
requestEncryptionChain: "hex"
responseDecryptionChain: "hex"
```

## 运行测试

```bash
# 运行单元测试
cd /path/to/agent-harness
python3.12 -m pytest cli_anything/godzilla/tests/test_core.py -v

# 运行 E2E 测试
python3.12 -m pytest cli_anything/godzilla/tests/test_full_e2e.py -v -s

# 使用强制安装模式运行测试
CLI_ANYTHING_FORCE_INSTALLED=1 python3.12 -m pytest cli_anything/godzilla/tests/ -v -s
```

## 项目结构

```
cli_anything/godzilla/
├── __init__.py
├── godzilla_cli.py      # CLI 主入口
├── core/
│   ├── __init__.py
│   ├── project.py       # 项目管理
│   ├── shell.py         # Shell 管理
│   ├── profile.py       # C2 Profile 管理
│   └── database.py      # 数据库操作
├── utils/
│   ├── __init__.py
│   ├── godzilla_backend.py  # 哥斯拉 JAR 集成
│   └── repl_skin.py         # REPL 界面
└── tests/
    ├── TEST.md          # 测试计划和结果
    ├── test_core.py     # 单元测试
    └── test_full_e2e.py # E2E 测试
```

## 兼容性

- 可直接打开原版哥斯拉创建的项目（自动生成配置文件）
- 数据库列名使用 camelCase（与原版哥斯拉保持一致）
- 支持 HTTP 请求头的 JSON 和纯文本两种格式

## 许可证

MIT License

## 免责声明

本工具仅供安全研究和授权测试使用。使用本工具进行未经授权的测试是非法的。用户需自行承担使用本工具的所有责任。
