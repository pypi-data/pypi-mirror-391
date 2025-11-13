# AI Agent 开发守则 - AICoding Backend

## 项目核心定位

- **项目类型**: MCP (Model Context Protocol) 服务器实现
- **核心功能**: 为AI编码助手提供后端工具集和提示词管理
- **技术栈**: Python 3.13+, MCP协议, 异步编程, Pydantic数据验证
- **架构模式**: 模块化工具系统 + 提示词模板管理

## MCP协议开发规范

### 工具实现标准
- **必须**: 所有工具函数使用 `async def` 定义
- **必须**: 使用 Pydantic BaseModel 定义工具参数结构
- **必须**: 工具函数包含完整的类型注解和docstring
- **必须**: 返回符合MCP协议格式的响应数据
- **必须**: 在 `main.py` 中使用 `@mcp.tool()` 装饰器注册工具

### 工具参数模型定义
- **必须**: 为每个工具创建对应的参数类，继承自 `BaseModel`
- **必须**: 使用 Field() 定义参数描述和验证规则
- **必须**: 参数类命名遵循 `{ToolName}Args` 模式
- **禁止**: 在工具函数中直接操作文件I/O，使用utils模块

### 工具注册流程
1. **定义参数模型** → 创建 `class ToolArgs(BaseModel)`
2. **实现工具函数** → 使用 `async def tool_name(args: ToolArgs)`
3. **注册到MCP服务器** → 添加 `@mcp.tool("tool_name")` 装饰器
4. **错误处理** → 返回 `{"success": False, "error": "message"}`

## 异步编程强制规范

### 异步操作要求
- **必须**: 所有I/O操作使用异步版本 (`aiofiles`, `asyncio`)
- **必须**: 文件读取使用 `await read_file()` 工具函数
- **必须**: 网络请求使用 `httpx.AsyncClient`
- **禁止**: 在异步函数中使用阻塞操作 (`time.sleep`, `open()`)

### 并发控制标准
- **必须**: 使用 `asyncio.Semaphore` 控制并发数量
- **必须**: 为长时间运行操作设置超时机制
- **必须**: 使用 `asyncio.gather()` 处理多个异步任务
- **禁止**: 创建过多的并发任务导致资源耗尽

## 模块化架构规范

### 目录结构标准
```
aicoding_backend/
├── main.py          # MCP服务器入口和工具注册
├── tools/           # MCP工具实现模块
│   ├── __init__.py  # 工具导出
│   └── *.py         # 具体工具实现
├── prompts/         # 提示词模板存储
│   ├── __init__.py  # 模板加载函数
│   ├── *.md         # Markdown格式模板
│   └── *.py         # Python字符串模板
└── utils/           # 通用工具类库
    ├── __init__.py  # 工具函数导出
    ├── file_reader.py   # 文件读取工具
    └── log.py       # 日志记录工具
```

### 模块导入规范
- **必须**: 使用相对导入 (`from .tools import tool_name`)
- **必须**: 在 `__init__.py` 中定义 `__all__` 列表
- **必须**: 按依赖顺序导入模块
- **禁止**: 创建循环导入依赖

## 数据验证和类型安全

### Pydantic模型使用
- **必须**: 所有外部输入使用Pydantic模型验证
- **必须**: 使用 Field() 提供参数描述和示例
- **必须**: 定义模型的 `__doc__` 字符串说明用途
- **必须**: 使用 `Optional[T] = None` 处理可选参数

### 类型注解标准
- **必须**: 函数参数和返回值添加类型注解
- **必须**: 使用 `List[T]`, `Dict[K,V]`, `Optional[T]` 等泛型
- **必须**: 异步函数返回类型使用 `async def func() -> T`
- **禁止**: 使用 `Any` 类型，必须明确指定具体类型

## 错误处理和日志规范

### 异常处理标准
- **必须**: 使用 try-except 捕获具体异常类型
- **必须**: 记录异常堆栈信息便于调试
- **必须**: 返回用户友好的错误信息
- **禁止**: 使用空的 except: 块捕获所有异常

### 日志记录要求
- **必须**: 使用 `log_data()` 函数记录工具调用日志
- **必须**: 包含工具名称和操作结果
- **必须**: 错误日志包含异常类型和消息
- **禁止**: 在生产环境中使用 print() 输出调试信息

## 文件操作安全规范

### 文件路径处理
- **必须**: 使用 `pathlib.Path` 处理文件路径
- **必须**: 验证文件路径在项目允许范围内
- **必须**: 使用 `current_dir` 获取当前模块目录
- **禁止**: 使用字符串拼接构建文件路径

### 文件读取标准
- **必须**: 使用 `await read_file()` 异步读取文件
- **必须**: 检查文件存在性后再读取
- **必须**: 处理文件编码问题 (UTF-8)
- **禁止**: 读取过大的文件导致内存溢出

## 配置管理规范

### 依赖版本控制
- **必须**: 在 `pyproject.toml` 中指定精确的版本范围
- **必须**: 关键依赖使用 `>=` 避免破坏性更新
- **必须**: 测试新依赖版本的兼容性
- **禁止**: 使用通配符版本 (`*`) 或过于宽松的版本约束

### MCP服务器配置
- **必须**: 在 `mcp-config.json` 中正确配置服务器启动参数
- **必须**: 使用模块路径 (`-m aicoding_backend.main`) 启动
- **必须**: 确保配置文件的JSON格式正确性
- **禁止**: 硬编码配置信息到源代码中

## 代码质量强制要求

### 文档字符串标准
- **必须**: 所有公共函数包含完整的docstring
- **必须**: 使用三引号格式和多行描述
- **必须**: 包含 Args、Returns、Raises 等章节
- **必须**: 提供参数类型和用途说明

### 代码格式规范
- **必须**: 遵循PEP 8编码规范
- **必须**: 使用4个空格缩进，禁止使用Tab
- **必须**: 行长度不超过88个字符
- **必须**: 在运算符前后添加空格

## 关键文件交互联动规范

### 新增工具时的文件同步
- **修改 `aicoding_backend/tools/`**: 必须同步更新 `tools/__init__.py` 导出列表
- **修改 `main.py`**: 必须确保新工具正确注册到MCP服务器
- **新增提示词模板**: 必须在对应工具中正确引用模板路径
- **修改依赖**: 必须更新 `pyproject.toml` 并测试兼容性

### 配置文件变更联动
- **修改 `mcp-config.json`**: 必须验证服务器能正常启动
- **更新工具参数**: 必须同步更新参数模型和工具实现
- **修改文件结构**: 必须更新所有相关的导入路径

## AI Agent决策优先级标准

### 工具开发优先级
1. **复用现有工具**: 优先扩展已有工具的功能
2. **创建专用工具**: 为特定功能创建新的独立工具
3. **修改核心逻辑**: 最后考虑修改主服务器代码

### 技术选择优先级
1. **异步编程**: 优先使用async/await模式
2. **类型安全**: 优先使用Pydantic进行数据验证
3. **模块化设计**: 优先保持代码的模块化和可维护性
4. **错误处理**: 优先确保健壮的错误处理机制

## 严格禁止事项 ⚠️

### 代码安全禁忌
- **禁止**: 执行用户输入的任意代码
- **禁止**: 在工具中暴露系统敏感信息
- **禁止**: 绕过Pydantic验证直接处理原始输入
- **禁止**: 在日志中记录密码、密钥等敏感数据

### 架构设计禁忌
- **禁止**: 创建循环依赖的模块结构
- **禁止**: 在工具层实现复杂的业务逻辑
- **禁止**: 忽略MCP协议的响应格式要求
- **禁止**: 混合同步和异步编程模式

### 文件操作禁忌
- **禁止**: 访问项目目录外的文件
- **禁止**: 删除或修改关键配置文件
- **禁止**: 在临时目录外创建临时文件
- **禁止**: 硬编码文件路径或系统路径

## 开发示例参考

### ✅ 正确的工具实现模板
```python
from pydantic import BaseModel, Field
from typing import Optional

class ToolArgs(BaseModel):
    """工具参数模型"""
    param: str = Field(..., description="参数描述")
    optional_param: Optional[str] = Field(None, description="可选参数")

@mcp.tool("tool_name")
async def tool_function(args: ToolArgs) -> dict:
    """
    工具函数描述
    
    Args:
        args: 工具参数
        
    Returns:
        MCP协议格式的响应数据
    """
    try:
        # 异步处理逻辑
        result = await process_data(args.param)
        log_data({"tool": "tool_name", "status": "success"})
        return {"success": True, "data": result}
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        log_data({"tool": "tool_name", "status": "error", "message": error_msg})
        return {"success": False, "error": error_msg}
```

### ❌ 错误实现示例
```python
# 错误：缺少类型注解和异步定义
def bad_tool(param):
    result = open("file.txt").read()  # 阻塞I/O
    return result  # 不符合MCP响应格式

# 错误：忽略异常处理
async def another_bad_tool(args):
    data = requests.get("http://example.com")  # 阻塞请求
    return data.text  # 未格式化的原始响应