# 需求描述文档

## 功能特性:

**必须实现 Python 版本的 init_requirements_doc 功能模块，包含以下核心特性：**

- **Prompt 参数接口定义**：创建 `InitRequirementsDocPromptParams` 类型定义
- **Prompt 生成函数**：实现 `get_init_requirements_doc_prompt` 异步函数
- **模板加载机制**：集成现有的 `load_prompt` 工具函数
- **环境变量支持**：通过 `INIT_REQUIREMENTS_DOC` 环境变量允许自定义覆盖
- **需求文档模板**：内置完整的需求描述文档结构模板

## 参考示例:

**基于现有项目结构的实现模式：**

- 参考 `src/prompts/init_project_rules.py` 的模块结构和命名约定
- 参考 `src/utils/loader.py` 中的 `load_prompt` 函数使用方式
- 参考 `src/tools/init_project_rules.py` 中的工具函数实现模式

**TypeScript 原版功能对照：**
```typescript
// 原版接口定义
export interface InitRequirementsDocPromptParams {
  // 目前没有额外参数，未来可按需扩展
}

// 原版函数签名
export async function getInitRequirementsDocPrompt(
  params?: InitRequirementsDocPromptParams
): Promise<string>
```

## 参考文档:

- **现有工具模块**：`src/utils/loader.py` - 了解 `load_prompt` 函数的参数和返回值
- **项目结构规范**：`src/prompts/` 目录 - 查看现有 prompt 模块的组织方式
- **类型定义模式**：`src/tools/` 目录 - 参考现有工具函数的实现模式
- **Python 异步编程**：确保函数定义为 `async def` 并返回 `str` 类型

## 注意事项:

**⚠️ 严格遵循项目规范：**

- **文件位置**：必须在 `src/prompts/` 目录下创建 `init_requirements_doc.py`
- **导入路径**：使用相对导入 `from ..utils.loader import load_prompt`
- **函数命名**：使用下划线命名法 `get_init_requirements_doc_prompt`
- **类型注解**：必须添加完整的类型注解，包括 `Optional`, `Dict`, `Any` 等

**⚠️ 模板内容完整性：**

- **必须包含完整的需求文档模板结构**
- **必须保持 markdown 格式的正确转义**
- **必须包含所有四个主要部分**：功能特性、参考示例、参考文档、注意事项

**⚠️ 环境变量处理：**

- **环境变量名称**：必须使用 `INIT_REQUIREMENTS_DOC` 作为环境变量名
- **默认行为**：当环境变量不存在时，返回内置模板
- **覆盖机制**：当环境变量存在时，完全使用环境变量内容

**⚠️ 异步函数实现：**

- **函数签名**：必须定义为 `async def`
- **参数处理**：支持可选的 `InitRequirementsDocPromptParams` 参数
- **返回类型**：必须返回 `str` 类型的 prompt 内容

**⚠️ 避免常见错误：**

- **禁止硬编码路径**：不要在代码中硬编码 `.joycode/docs` 路径
- **禁止直接文件操作**：此模块仅负责生成 prompt，不负责文件创建
- **禁止包含执行逻辑**：保持模块职责单一，仅处理 prompt 生成