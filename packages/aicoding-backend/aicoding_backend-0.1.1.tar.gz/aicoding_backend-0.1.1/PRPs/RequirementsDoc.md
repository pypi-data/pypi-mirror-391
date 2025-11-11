# init_requirements_doc 功能完整实现与集成 PRP

## 目标
完成 Python 版本的 `init_requirements_doc` 功能模块的完整实现、集成和验证，确保该功能能够通过 MCP 协议正确暴露和调用，为 AI Agent 提供需求描述文档生成能力。

## 为什么
- **业务价值**: 为 AI Agent 提供标准化的需求描述文档生成功能，提高开发效率
- **与现有功能的集成**: 与 `init_project_rules` 功能形成完整的项目初始化工具链
- **解决的问题**: 统一需求文档格式，为 AI Agent 提供结构化的项目需求描述模板

## 什么
实现一个完整的 MCP 工具，能够生成标准化的需求描述文档模板，包括功能特性、参考示例、参考文档和注意事项四个核心部分。

### 成功标准
- [ ] `init_requirements_doc` 工具能够通过 MCP 协议正确调用
- [ ] 生成的文档模板包含所有必需的结构化内容
- [ ] 支持通过环境变量 `INIT_REQUIREMENTS_DOC` 自定义模板
- [ ] 所有测试通过，无语法和类型错误
- [ ] 功能集成到 MCP 服务器配置中

## 所有必需的上下文

### 文档和参考资料
```yaml
# 必读 - 将这些包含在您的上下文窗口中
- file: src/prompts/init_project_rules.py
  why: 参考现有 prompt 生成器的实现模式，dataclass 使用方式
  
- file: src/tools/init_project_rules.py
  why: 参考现有 MCP 工具的实现模式，Pydantic 验证和响应格式
  
- file: src/utils/loader.py
  why: 了解 load_prompt 函数的使用方式和环境变量处理机制
  
- file: .joycode/docs/RequirementsDoc.md
  why: 理解需求规范和功能特性定义
  
- file: src/main.py
  why: 了解 MCP 服务器工具注册机制和服务器配置
```

### 当前代码库结构
```bash
src/
├── prompts/
│   ├── __init__.py
│   ├── init_project_rules.py          # 现有 prompt 生成器模式
│   └── init_requirements_doc.py       # 已实现，需验证
├── tools/
│   ├── __init__.py
│   ├── init_project_rules.py          # 现有 MCP 工具模式
│   └── init_requirements_doc.py       # 已实现，需验证
├── utils/
│   ├── loader.py                      # prompt 加载工具
│   └── ...
└── main.py                            # MCP 服务器入口
```

### 期望的代码库结构（需要添加的集成点）
```bash
src/main.py                            # 需要注册新工具
PRPs/RequirementsDoc.md               # 本文档
test/test_init_requirements_doc.py    # 测试文件（如需要）
```

### 已知的代码库模式和约定
```python
# 关键: Python MCP 工具需要遵循的模式
# 1. Prompt 生成器模式 (src/prompts/)
@dataclass
class PromptParams:
    pass

async def get_prompt(params: Optional[PromptParams] = None) -> str:
    template = "..."
    return load_prompt(template, "ENV_VAR_NAME")

# 2. MCP 工具模式 (src/tools/)
class ToolSchema(BaseModel):
    pass

TOOL_CONFIG = {
    "name": "tool_name",
    "description": "工具描述",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
}

async def handle_tool(arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # 验证参数、调用 prompt 生成器、返回标准响应格式
    pass

# 3. 错误处理模式
# 使用 try-catch 包装，返回标准错误响应格式
```

## 实施蓝图

### 数据模型和结构
已实现的核心数据模型：
```python
# src/prompts/init_requirements_doc.py
@dataclass
class InitRequirementsDocPromptParams:
    pass  # 当前无额外参数，未来可扩展

# src/tools/init_requirements_doc.py  
class InitRequirementsDocSchema(BaseModel):
    pass  # 空模式，无输入参数
```

### 按顺序完成 PRP 所需完成的任务列表

```yaml
任务 1: 验证现有实现的完整性
检查文件:
  - src/prompts/init_requirements_doc.py
  - src/tools/init_requirements_doc.py
验证内容:
  - 导入路径正确性
  - 函数签名和返回类型
  - 模板内容完整性
  - 环境变量配置正确

任务 2: 集成到 MCP 服务器
修改 src/main.py:
  - 导入新工具: from .tools.init_requirements_doc import INIT_REQUIREMENTS_DOC_TOOL, handle_init_requirements_doc
  - 注册工具到 server.list_tools()
  - 添加工具处理到 server.call_tool()
  - 确保工具名称匹配

任务 3: 创建测试验证
创建测试文件（如果需要）:
  - 测试 prompt 生成功能
  - 测试 MCP 工具调用
  - 测试环境变量覆盖机制
  - 测试错误处理

任务 4: 功能验证
运行验证命令:
  - 语法检查: python -m py_compile src/prompts/init_requirements_doc.py
  - 类型检查: mypy src/prompts/init_requirements_doc.py src/tools/init_requirements_doc.py
  - MCP 服务器启动测试
  - 工具调用测试

任务 5: 文档更新
更新相关文档:
  - README.md 中添加新工具说明
  - 工具使用示例
  - API 文档更新
```

### 关键实现细节

#### 任务 1: 验证现有实现
```python
# 验证 src/prompts/init_requirements_doc.py
# 检查点:
# 1. 导入路径: from ..utils.loader import load_prompt
# 2. 函数签名: async def get_init_requirements_doc_prompt(params: Optional[InitRequirementsDocPromptParams] = None) -> str
# 3. 环境变量: load_prompt(index_template, "INIT_REQUIREMENTS_DOC")
# 4. 模板内容: 包含完整的需求文档结构

# 验证 src/tools/init_requirements_doc.py  
# 检查点:
# 1. 导入路径: from ..prompts.init_requirements_doc import get_init_requirements_doc_prompt
# 2. 工具配置: INIT_REQUIREMENTS_DOC_TOOL 字典结构
# 3. 处理函数: async def handle_init_requirements_doc(arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
# 4. 错误处理: 标准 MCP 响应格式
```

#### 任务 2: MCP 服务器集成
```python
# 在 src/main.py 中添加
from .tools.init_requirements_doc import (
    INIT_REQUIREMENTS_DOC_TOOL, 
    handle_init_requirements_doc
)

# 在 list_tools 处理中添加
tools.append(INIT_REQUIREMENTS_DOC_TOOL)

# 在 call_tool 处理中添加
elif name == "init_requirements_doc":
    return await handle_init_requirements_doc(arguments)
```

### 集成点
```yaml
MCP 服务器配置:
  - 文件: src/main.py
  - 模式: "导入工具配置和处理函数，注册到服务器"
  
工具注册:
  - 位置: server.list_tools() 方法
  - 模式: "tools.append(INIT_REQUIREMENTS_DOC_TOOL)"
  
工具调用:
  - 位置: server.call_tool() 方法  
  - 模式: "elif name == 'init_requirements_doc': return await handle_init_requirements_doc(arguments)"
```

## 验证循环

### 级别 1: 语法和类型检查
```bash
# 首先运行这些 - 在继续之前修复任何错误
python -m py_compile src/prompts/init_requirements_doc.py
python -m py_compile src/tools/init_requirements_doc.py

# 类型检查（如果有 mypy）
mypy src/prompts/init_requirements_doc.py
mypy src/tools/init_requirements_doc.py

# 预期: 无错误。如果有错误，阅读错误并修复。
```

### 级别 2: 单元测试
```python
# 创建 test_init_requirements_doc.py 包含以下测试用例:
import asyncio
from src.prompts.init_requirements_doc import get_init_requirements_doc_prompt
from src.tools.init_requirements_doc import handle_init_requirements_doc

async def test_prompt_generation():
    """测试 prompt 生成功能"""
    result = await get_init_requirements_doc_prompt()
    assert isinstance(result, str)
    assert "需求描述文档" in result
    assert "功能特性" in result
    assert "参考示例" in result
    assert "参考文档" in result
    assert "注意事项" in result

async def test_tool_handler():
    """测试 MCP 工具处理"""
    result = await handle_init_requirements_doc({})
    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"

async def test_error_handling():
    """测试错误处理"""
    # 测试异常情况下的响应格式
    pass

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_prompt_generation())
    asyncio.run(test_tool_handler())
    print("所有测试通过")
```

```bash
# 运行并迭代直到通过:
python test_init_requirements_doc.py
# 如果失败: 阅读错误，理解根本原因，修复代码，重新运行
```

### 级别 3: MCP 服务器集成测试
```bash
# 启动 MCP 服务器
uv run main.py

# 测试工具列表（通过 MCP 客户端或日志验证）
# 预期: init_requirements_doc 出现在工具列表中

# 测试工具调用
# 预期: 返回完整的需求文档模板内容
```

### 级别 4: 环境变量测试
```bash
# 测试环境变量覆盖
export INIT_REQUIREMENTS_DOC="自定义模板内容"
uv run main.py
# 验证返回的是自定义内容而不是默认模板

# 清理环境变量
unset INIT_REQUIREMENTS_DOC
```

## 最终验证清单
- [ ] 所有 Python 文件语法正确: `python -m py_compile src/prompts/init_requirements_doc.py src/tools/init_requirements_doc.py`
- [ ] 无类型错误（如果使用 mypy）: `mypy src/prompts/ src/tools/`
- [ ] MCP 服务器成功启动: `uv run main.py`
- [ ] 工具在工具列表中可见
- [ ] 工具调用返回正确格式的响应
- [ ] 环境变量覆盖机制正常工作
- [ ] 错误情况得到优雅处理
- [ ] 日志信息清晰有用

## 要避免的反模式
- ❌ 不要修改现有的成功模式 - 复用 init_project_rules 的实现方式
- ❌ 不要跳过 MCP 服务器集成 - 功能必须通过 MCP 协议暴露
- ❌ 不要忽略环境变量支持 - 这是项目的标准特性
- ❌ 不要硬编码模板内容路径 - 使用 load_prompt 函数
- ❌ 不要忽略错误处理 - 返回标准 MCP 响应格式

## 质量评分
**PRP 信心评分: 9/10**

高信心的原因:
- 功能已部分实现，主要是验证和集成工作
- 有清晰的现有模式可以遵循
- 验证步骤具体且可执行
- 集成点明确定义

降分原因:
- 需要验证现有实现的完整性
- MCP 服务器集成可能需要调试

## 注意事项
1. **现有实现验证**: 优先验证已存在的 `src/prompts/init_requirements_doc.py` 和 `src/tools/init_requirements_doc.py` 文件是否完整正确
2. **模式一致性**: 严格遵循 `init_project_rules` 的实现模式，确保架构一致性
3. **MCP 协议**: 确保工具正确注册到 MCP 服务器，能够通过标准 MCP 客户端调用
4. **环境变量**: 验证 `INIT_REQUIREMENTS_DOC` 环境变量能够正确覆盖默认模板
5. **错误处理**: 所有异常都应该被捕获并返回标准的 MCP 错误响应格式