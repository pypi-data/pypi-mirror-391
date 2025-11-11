# AI Coding Backend

AI Coding Backend - A backend service for AI-assisted coding with MCP (Model Context Protocol) integration

## Description

This project provides a backend service for AI-assisted coding with MCP integration.

## Installation

```bash
uv add aicoding-backend
```

## Usage

After installation, you can run the service using:

```bash
uv run aicoding-backend
```

## Available MCP Tools

This backend provides the following MCP tools:

### init_requirements_doc
- **Description**: 初始化需求描述文档模板 (Initialize requirements document template)
- **Usage**: Generates a standardized requirements document template for AI Agent usage
- **Parameters**: None
- **Returns**: Complete requirements document template with structure guidelines

### init_project_rules
- **Description**: 初始化项目规范 (Initialize project specification)
- **Usage**: Provides project specification guidelines for AI Agent operations
- **Parameters**: None
- **Returns**: Project specification template

### generate_prp
- **Description**: 根据功能需求文件生成全面的产品需求提示（PRP）文档
- **Parameters**: `feature_file` (string) - Path to the feature requirements file
- **Returns**: Complete PRP document generation guidance

### execute_prp
- **Description**: 根据 PRP 文件生成执行指南
- **Parameters**: `prpFile` (string) - Path to the PRP file
- **Returns**: Complete execution steps guidance

### process_thought
- **Description**: 处理单一思维并返回格式化输出
- **Parameters**: Various thought processing parameters
- **Returns**: Formatted thought processing output

## Development

To contribute to this project:

1. Clone the repository
2. Install dependencies: `uv sync`
3. Make your changes
4. Run tests: `uv run pytest`

## License

MIT License