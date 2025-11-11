# AI Agent 开发守则

## 项目概述

- **项目类型**: MCP (Model Context Protocol) 服务器实现
- **核心功能**: 为AI编码助手提供后端工具和提示词管理
- **技术栈**: Python 3.x, MCP协议, 异步编程
- **架构模式**: 模块化工具系统 + 提示词模板管理

## 项目架构规范

### 核心目录结构
- `src/` - 主要源代码目录
- `src/tools/` - MCP工具实现模块
- `src/prompts/` - 提示词模板存储
- `src/utils/` - 通用工具类库
- `src/mcp_server.py` - MCP服务器主入口
- `src/code.py` - 核心业务逻辑

### 文件组织规则
- **必须遵循**: 所有Python文件使用snake_case命名
- **必须遵循**: 每个目录包含`__init__.py`文件
- **必须遵循**: 工具模块文件名与工具名称一致

## MCP工具开发规范

### 新增工具流程
1. **必须**: 在`src/tools/`目录创建新工具模块文件
2. **必须**: 在`src/tools/__init__.py`中导入并注册新工具
3. **必须**: 在`src/mcp_server.py`中添加工具到服务器注册列表
4. **必须**: 为工具创建对应的提示词模板(如需要)

### 工具实现要求
- **必须**: 每个工具函数包含完整的类型注解
- **必须**: 提供详细的docstring说明工具功能和参数
- **必须**: 使用异步函数定义(`async def`)
- **必须**: 返回符合MCP协议的响应格式
- **禁止**: 在工具函数中直接处理文件I/O，使用utils模块

### 工具命名规范
- **必须**: 使用动词+名词的命名模式(如`init_project_rules`)
- **必须**: 工具名称与文件名保持一致
- **禁止**: 使用缩写或模糊的命名

## 提示词管理规范

### 提示词文件组织
- **必须**: 所有提示词模板存放在`src/prompts/`目录
- **必须**: 使用`.md`格式存储Markdown模板
- **必须**: 使用`.py`格式存储Python字符串模板
- **必须**: 文件名与对应工具名称保持一致

### 提示词内容要求
- **必须**: 包含明确的AI Agent操作指令
- **必须**: 使用命令式语言，避免描述性内容
- **必须**: 提供具体的"应该做"和"不应该做"示例
- **禁止**: 包含通用开发知识，仅包含项目特定规则

## 工具类开发规范

### Utils模块组织
- **必须**: 通用功能放在`src/utils/`目录
- **必须**: 按功能分类创建不同的工具类文件
- **必须**: 在`src/utils/__init__.py`中导出公共接口

### 工具类实现要求
- **必须**: 使用类方法或静态方法封装功能
- **必须**: 提供异常处理和错误日志
- **必须**: 支持异步操作(如涉及I/O)
- **禁止**: 在工具类中硬编码文件路径

## 配置管理规范

### MCP配置文件
- **必须**: 修改`mcp-config.json`时保持JSON格式正确性
- **必须**: 新增服务器配置时包含完整的command和args
- **禁止**: 直接修改配置文件，应通过代码生成

### Python配置
- **必须**: 项目依赖管理使用`pyproject.toml`
- **必须**: 新增依赖时更新version约束
- **禁止**: 使用requirements.txt管理依赖

## 代码质量规范

### 代码风格
- **必须**: 遵循PEP 8编码规范
- **必须**: 使用type hints进行类型标注
- **必须**: 函数和类包含完整的docstring
- **必须**: 异步函数使用`async/await`语法

### 错误处理
- **必须**: 使用try-except捕获可能的异常
- **必须**: 记录错误日志便于调试
- **必须**: 返回有意义的错误信息给MCP客户端
- **禁止**: 忽略异常或使用空的except块

## 测试和示例规范

### 测试文件组织
- **必须**: 测试文件以`test_`前缀命名
- **必须**: 测试文件放在项目根目录
- **必须**: 每个工具提供基本的功能测试
- **禁止**: 在生产代码中包含测试逻辑

### 示例代码要求
- **必须**: 提供完整的使用示例
- **必须**: 示例代码能够独立运行
- **必须**: 包含错误处理演示
- **禁止**: 示例中使用硬编码的敏感信息

## 文件交互规范

### 关键文件联动
- **修改`src/tools/`中的工具时**: 必须同步更新`src/tools/__init__.py`和`src/mcp_server.py`
- **修改`src/mcp_server.py`时**: 必须确保所有工具正确注册到MCP服务器
- **新增提示词模板时**: 必须在对应工具中正确引用模板路径
- **修改`pyproject.toml`时**: 必须验证依赖版本兼容性

### 配置文件同步
- **修改MCP服务器配置时**: 必须同步更新`mcp-config.json`
- **更改项目结构时**: 必须更新README.md中的说明
- **添加新功能时**: 必须更新MCP_CLIENT_SETUP.md的使用指南

## AI决策规范

### 工具选择优先级
1. **优先**: 使用现有工具扩展功能
2. **次选**: 创建新的专用工具
3. **最后**: 修改核心服务器逻辑

### 模糊需求处理
- **必须**: 先分析现有代码库理解上下文
- **必须**: 基于项目架构推断最佳实现方案
- **必须**: 优先保持现有代码结构的一致性
- **禁止**: 在不确定时随意修改核心文件

## 严格禁止事项

### 代码修改禁忌
- **禁止**: 直接修改`src/mcp_server.py`的核心MCP协议实现
- **禁止**: 破坏现有工具的接口兼容性
- **禁止**: 在工具函数中执行阻塞操作
- **禁止**: 硬编码文件路径或配置信息

### 文件操作禁忌
- **禁止**: 删除或重命名核心配置文件
- **禁止**: 修改`__init__.py`文件的导入结构(除非添加新模块)
- **禁止**: 在非utils目录中实现通用功能
- **禁止**: 创建循环依赖的模块引用

### 架构设计禁忌
- **禁止**: 绕过MCP协议直接实现功能
- **禁止**: 在工具层实现复杂的业务逻辑
- **禁止**: 混合同步和异步编程模式
- **禁止**: 忽略错误处理和日志记录

## 开发示例

### ✅ 正确的工具实现
```python
# src/tools/example_tool.py
async def example_tool(param: str) -> dict:
    """
    示例工具的正确实现方式
    
    Args:
        param: 输入参数
    
    Returns:
        MCP协议格式的响应
    """
    try:
        # 使用utils模块处理逻辑
        result = await utils.process_data(param)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {"success": False, "error": str(e)}
```

### ❌ 错误的工具实现
```python
# 错误示例：缺少类型注解、异常处理
def bad_tool(param):
    result = open("file.txt").read()  # 阻塞I/O
    return result  # 不符合MCP响应格式
```

### ✅ 正确的工具注册
```python
# src/tools/__init__.py
from .example_tool import example_tool
from .another_tool import another_tool

__all__ = ["example_tool", "another_tool"]
```

### ✅ 正确的服务器配置
```python
# src/mcp_server.py中的工具注册
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="example_tool",
            description="工具描述",
            inputSchema={
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"]
            }
        )
    ]