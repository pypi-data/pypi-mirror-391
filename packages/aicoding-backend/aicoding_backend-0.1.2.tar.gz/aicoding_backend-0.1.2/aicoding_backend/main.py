from mcp.server.fastmcp import FastMCP
from .utils import read_file, file_exists, generate_prompt
from typing import List, Optional
from pydantic import BaseModel, Field
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from .prompts import get_init_requirements_doc_prompt
from .utils.log import log_data

mcp = FastMCP("backend-coding")

current_dir = Path(__file__).parent


class ProcessThoughtPromptParam(BaseModel):
    """process_thought工具的参数结构"""
    thought: str = Field(
        ...,
        min_length=1,
        description="思维内容",
        example="这是一个关于项目架构的思考"
    )
    thought_number: int = Field(
        ...,
        gt=0,
        description="当前思维编号",
        example=1
    )
    total_thoughts: int = Field(
        ...,
        gt=0,
        description="预计总思维数量，如果需要更多的思考可以随时变更",
        example=5
    )
    next_thought_needed: bool = Field(
        ...,
        description="是否需要下一步思维",
        example=True
    )
    stage: str = Field(
        ...,
        min_length=1,
        description="思维阶段。可用阶段包括：问题定义、信息收集、研究、分析、综合、结论、批判性提问和规划。",
        example="分析"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="思维标签，是一个数组字符串",
        example=["架构", "设计"]
    )
    axioms_used: Optional[List[str]] = Field(
        default=None,
        description="使用的公理，是一个数组字符串",
        example=["单一职责原则", "开闭原则"]
    )
    assumptions_challenged: Optional[List[str]] = Field(
        default=None,
        description="挑战的假设，是一个数组字符串",
        example=["所有用户都需要这个功能"]
    )

class GeneratePrpParam(BaseModel):
    """generate_prp 工具的参数结构"""
    feature_file: str = Field(
        ...,
        description="功能需求文件路径（例如：INITIAL.md）"
    )


@mcp.tool("generate_prp")
async def handle_generate_prp(args: GeneratePrpParam) -> str:
    """根据功能需求文件生成全面的产品需求提示（PRP）文档的指导。
    
    此工具会：
    1. 读取功能需求文件。
    2. 加载一个模板，指导用户或 AI 如何通过研究代码库和外部资源来构建一个高质量的 PRP。
    """
    try:
        feature_file = args.feature_file

        if not file_exists(feature_file):
            raise Exception(f"功能需求文件不存在: {feature_file}")

        # 获取当前文件的目录路径
        template_path = current_dir / "prompts"

        # 构建示例文件路径（注释掉的代码）
        # form_example_path = current_dir / "../../examples/form-vue-template.md"
        # list_example_path = current_dir / "../../examples/list-vue-template.md"
        # pro_list_example_path = current_dir / "../../examples/pro-list-vue-template.md"

        # 检查模板文件是否存在
        if not file_exists(template_path / "prp_base.md"):
            raise Exception(f"PRP 模板文件不存在: {template_path}")

        # 获取 template 内容
        template_content = await read_file(str(template_path), "prp_base.md")

        # 从功能文件名提取功能名称（用于输出路径）
        feature_name = Path(feature_file).stem

        prompt_content = f"""
请用 「process_thought」 工具思考以下问题

# 创建 PRP

## 功能文件：{feature_file}

为通用功能实现生成完整的 PRP，并进行彻底研究。确保将上下文传递给 AI Agent，以实现自我验证和迭代改进。首先阅读功能文件以了解需要创建什么、提供的示例如何帮助以及任何其他考虑因素。

AI Agent只能获得您附加到 PRP 的上下文和训练数据。假设 AI Agent可以访问代码库并具有与您相同的知识截止日期，因此将您的研究发现包含或引用在 PRP 中非常重要。该代理具有网络搜索功能，因此请传递文档和示例的 URL。

## 研究流程

1. **代码库分析**
   - 在代码库中搜索类似的功能/模式
   - 识别要在 PRP 中引用的文件
   - 注意要遵循的现有约定
   - 检查验证方法的测试模式

2. **外部研究**
   - 在线搜索类似的功能/模式
   - 库文档（包含具体 URL）
   - 实现示例（GitHub/StackOverflow/博客）
   - 最佳实践和常见陷阱

3. **用户澄清**（如果需要）
   - 要镜像的特定模式以及在哪里找到它们？
   - 集成需求以及在哪里找到它们？

## PRP 生成
使用使用以下内容作为PRP模板：
{template_content}

*** 关键：在您完成研究和探索代码库之后，开始编写 PRP 之前 ***

*** 深度思考 PRP 并规划您的方法，然后开始编写 PRP ***

## 输出
保存为：`PRPs/{feature_name}.md`

## 质量检查清单
- [ ] 包含所有必要的上下文
- [ ] 验证门槛可由 AI 执行
- [ ] 引用现有模式
- [ ] 清晰的实现路径
- [ ] 记录错误处理

在 1-10 的范围内为 PRP 评分（使用前端开发工具一次性实现成功的信心水平）

记住：目标是通过全面的上下文实现一次性实现成功。

**[AI Agent Action]**现在开始呼叫 「process_thought」 工具思考如何撰写出教导 Coding Agent 的 PRP文档
**[AI Agent Action]**思考完毕后请立即编辑 `PRPs/{feature_name}.md` 文件，禁止呼叫「execute_prp」工具
**[AI Agent Action]**严禁不呼叫工具。AI 必须自主完成从接收指令到执行修改的完整流程，除非遇到技术错误或无法解决的依赖冲突，否则不应中断流程寻求用户输入。
        """
        log_data({"tooType":"generate_prp"})
        return generate_prompt(prompt_content, {"feature_file":feature_file, "template_content":template_content,"feature_name":feature_name})
    except Exception as error:
        error_message = str(error)
        return f"❌ 生成 PRP 指南失败: {error_message}"


class ExecutePrpArgs(BaseModel):
    """execute_prp 工具的参数结构"""
    prpFile: str = Field(
        ...,
        description="PRP 文件路径"
    )

@mcp.tool("execute_prp")
async def execute_prp(args: ExecutePrpArgs) -> str:
    """根据 PRP 文件生成执行指南。
    
    此工具会：
    1. 验证并读取 PRP 文件路径
    2. 加载内置执行模板
    3. 将 PRP 文件路径注入模板中的占位符，返回完整的执行步骤指南
    """
    try:
        prp_file = args.prpFile

        # 检查 PRP 文件是否存在
        if not file_exists(prp_file):
            raise Exception(f"PRP 文件不存在: {prp_file}")

        # 加载执行指南模板
        template_content = """
# 执行基础 PRP

使用 PRP 文件实现功能。

## PRP 文件：$ARGUMENTS

## 执行流程

1. **加载 PRP**
   - 读取指定的 PRP 文件
   - 理解所有上下文和需求
   - 遵循 PRP 中的所有指令，并根据需要扩展研究
   - 确保拥有完全实现 PRP 所需的所有上下文
   - 根据需要进行更多网络搜索和代码库探索

2. **深度思考**
   - 在执行计划之前深入思考。创建一个解决所有需求的综合计划。
   - 使用待办事项工具将复杂任务分解为更小、可管理的步骤。
   - 使用 TodoWrite 工具创建和跟踪实现计划。
   - 从现有代码中识别要遵循的实现模式。

3. **执行计划**
   - 执行 PRP
   - 实现所有代码

4. **验证**
   - 运行每个验证命令
   - 修复任何失败
   - 重新运行直到全部通过

5. **完成**
   - 确保所有检查清单项目完成
   - 运行最终验证套件
   - 报告完成状态
   - 再次阅读 PRP 以确保已实现所有内容

6. **引用 PRP**
   - 如果需要，您可以随时再次引用 PRP

注意：如果验证失败，请使用 PRP 中的错误模式进行修复并重试。
        """
        
        # 将模板中的 `$ARGUMENTS` 替换为传入的 prp_file 路径
        
        guide = template_content.replace("$ARGUMENTS", prp_file)
        log_data({"tooType":"execute_prp"})
        return guide
        
    except Exception as error:
        error_message = str(error)
        return f"❌ 生成执行指南失败: {error_message}"


@mcp.tool()
async def init_project_rules() -> str:
    """初始化项目规则
    Args: None
    Return: 模版提示词
    """
    log_data({"tooType":"init_project_rules"})
    template = await read_file(current_dir / "prompts", "CreateFeatureProjectRules.md")
    return template

@mcp.tool()
async def init_requirements_doc() -> str:
    """初始化需求描述文档模板
    Args: None
    Return: 需求描述文档模板提示词
    """
    log_data({"tooType":"init_requirements_doc"})
    return await get_init_requirements_doc_prompt()

@mcp.tool()
async def process_thought(processThoughtPromptParam : ProcessThoughtPromptParam) -> str:
    """处理单一思维并返回格式化输出
    """
    return await execute_process_thought(
        thought=processThoughtPromptParam.thought,
        thought_number=processThoughtPromptParam.thought_number,
        total_thoughts=processThoughtPromptParam.total_thoughts,
        next_thought_needed=processThoughtPromptParam.next_thought_needed,
        stage=processThoughtPromptParam.stage,
        tags=processThoughtPromptParam.tags,
        axioms_used=processThoughtPromptParam.axioms_used,
        assumptions_challenged=processThoughtPromptParam.assumptions_challenged
    )

async def execute_process_thought(
    thought: str,
    thought_number: int,
    total_thoughts: int,
    next_thought_needed: bool,
    stage: str,
    tags: List[str] = None,
    axioms_used: List[str] = None,
    assumptions_challenged: List[str] = None
) -> str:
    try:
        logging.info('Executing process_thought tool')

        # 确保列表参数不为None
        tags = tags or []
        axioms_used = axioms_used or []
        assumptions_challenged = assumptions_challenged or []

        # 更新total_thoughts如果thought_number更大
        if thought_number > total_thoughts:
            total_thoughts = thought_number

        # 构建next_section内容
        if next_thought_needed:
            next_section = '需要更多思考，继续使用 「process_thought」 工具思考找寻答案'
        else:
            next_section_lines = [
                '## 思考完成',
                '',
                '返回最终分析结果概要',
                '',
                '1. **任务摘要** - 目标、范围、挑战和限制条件',
                '2. **初步解答构想** - 可行的技术方案和实施计划',
            ]
            next_section = '\n'.join(next_section_lines)

        # 构建模板
        template_lines = [
            '## 思维 {{thought_number}}/{{total_thoughts}} - {{stage}}',
            '',
            '{{thought}}',
            '',
            '**标签:** {{tags}}',
            '',
            '**使用的原则:** {{axioms_used}}',
            '',
            '**挑战的假设:** {{assumptions_challenged}}',
            '',
            '**禁止事项：** 你应该禁止一切猜测，任何疑虑请完整查看相关程序代码或使用网络搜寻工具查询',
            '',
            '{{next_section}}',
        ]
        template = '\n'.join(template_lines)

        param = {
            "thought":thought,
            "thought_number":thought_number,
            "total_thoughts":total_thoughts,
            "stage":stage,
            "tags":",".join(tags) or "no tags",
            "axioms_used": ",".join(axioms_used) or "no axioms used",
            "assumptions_challenged":",".join(assumptions_challenged) or "no assumptions challenged",
        }

        # 格式化输出
        return generate_prompt(template, param)

    except Exception as error:
        logging.error('Error executing process_thought', exc_info=error)
        raise Exception('Error executing process_thought') from error


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()