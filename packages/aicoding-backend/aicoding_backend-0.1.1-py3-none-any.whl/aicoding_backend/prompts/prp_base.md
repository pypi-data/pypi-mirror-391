名称: "基础 PRP 模板 v2 - 上下文丰富且带验证循环"
描述: |

## 目的
该模板专为 AI 代理优化，使其能够通过充分的上下文和自我验证能力，通过迭代改进实现可工作的代码。

## 核心原则
1. **上下文为王**: 包含所有必要的文档、示例和注意事项
2. **验证循环**: 提供 AI 可运行和修复的可执行测试/检查
3. **信息密集**: 使用代码库中的关键词和模式
4. **渐进式成功**: 从简单开始，验证后再增强
5. **全局规则**: 确保遵循 CLAUDE.md 中的所有规则

---

## 目标
[需要构建什么 - 明确说明最终状态和期望]

## 为什么
- [业务价值和用户影响]
- [与现有功能的集成]
- [解决的问题以及为谁解决]

## 什么
[用户可见的行为和技术需求]

### 成功标准
- [ ] [具体的可衡量结果]

## 所有必需的上下文

### 文档和参考资料（列出实现功能所需的所有上下文）
```yaml
# 必读 - 将这些包含在您的上下文窗口中
- url: [官方 API 文档 URL]
  why: [您需要的具体章节/方法]
  
- file: [path/to/example.java]
  why: [要遵循的模式，要避免的陷阱]
  
- doc: [库文档 URL] 
  section: [关于常见陷阱的具体章节]
  critical: [防止常见错误的关键见解]

- docfile: [PRPs/ai_docs/file.md]
  why: [用户粘贴到项目中的文档]

```

### 当前代码库结构（在项目根目录运行 `tree` 命令）以获取代码库概览
```bash

```

### 期望的代码库结构（包含要添加的文件及文件职责）
```bash

```

### 已知的代码库陷阱和库怪癖
```typescript
// 关键: [库名称] 需要 [特定设置]
// 示例: React 组件需要使用 PascalCase 命名
// 示例: Vue 3 组合式 API 需要正确的响应式引用
// 示例: 我们使用 TypeScript 严格模式
```

## 实施蓝图

### 数据模型和结构

创建核心数据模型，确保类型安全和一致性。
```typescript
示例: 
 - 接口定义
 - 类型别名
 - Zod 验证模式
 - 枚举类型
```

### 按顺序完成 PRP 所需完成的任务列表

```yaml
任务 1:
修改 src/existing_module.ts:
  - 查找模式: "class OldImplementation"
  - 在包含 "constructor" 的行之后注入
  - 保留现有方法签名

创建 src/new_feature.ts:
  - 镜像模式来自: src/similar_feature.ts
  - 修改类名和核心逻辑
  - 保持错误处理模式相同

...(...）

任务 N:
...

```

### 每个任务所需的伪代码（根据需要添加到每个任务）
```typescript

// 任务 1
// 伪代码，包含关键细节，不写完整代码
async function newFeature(param: string): Promise<Result> {
    // 模式: 始终首先验证输入（参见 src/validators.ts）
    const validated = validateInput(param);  // 抛出 ValidationError
    
    // 陷阱: 此库需要连接池
    const conn = await getConnection();  // 参见 src/db/pool.ts
    try {
        // 模式: 使用现有的重试装饰器
        const result = await retry(
            async () => {
                // 关键: API 每秒超过 10 个请求会返回 429
                await rateLimiter.acquire();
                return await externalApi.call(validated);
            },
            { attempts: 3, backoff: 'exponential' }
        );
        
        // 模式: 标准化响应格式
        return formatResponse(result);  // 参见 src/utils/responses.ts
    } finally {
        await conn.release();
    }
}
```

### 集成点
```yaml
数据库:
  - 迁移: "在 users 表中添加 'feature_enabled' 列"
  - 索引: "CREATE INDEX idx_feature_lookup ON users(feature_id)"
  
配置:
  - 添加到: config/settings.ts
  - 模式: "export const FEATURE_TIMEOUT = Number(process.env.FEATURE_TIMEOUT || 30)"
  
路由:
  - 添加到: src/api/routes.ts  
  - 模式: "router.use('/feature', featureRouter)"
```

## 验证循环

### 级别 1: 语法和样式
```bash
# 首先运行这些 - 在继续之前修复任何错误
npm run lint              # 自动修复可能的问题
npm run type-check        # 类型检查

# 预期: 无错误。如果有错误，阅读错误并修复。
```

### 级别 2: 单元测试（每个新功能/文件/函数使用现有测试模式）
```typescript
// 创建 new-feature.test.ts 包含以下测试用例:
describe('newFeature', () => {
  it('基本功能正常工作', async () => {
    const result = await newFeature('valid_input');
    expect(result.status).toBe('success');
  });

  it('无效输入抛出 ValidationError', async () => {
    await expect(newFeature('')).rejects.toThrow(ValidationError);
  });

  it('优雅处理超时', async () => {
    vi.spyOn(externalApi, 'call').mockRejectedValue(new TimeoutError());
    const result = await newFeature('valid');
    expect(result.status).toBe('error');
    expect(result.message).toContain('timeout');
  });
});
```

```bash
# 运行并迭代直到通过:
npm test new-feature.test.ts
# 如果失败: 阅读错误，理解根本原因，修复代码，重新运行（永远不要通过 mock 来通过测试）
```

### 级别 3: 集成测试
```bash
# 启动服务
npm run dev

# 测试端点
curl -X POST http://localhost:3000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'

# 预期: {"status": "success", "data": {...}}
# 如果错误: 检查日志以获取堆栈跟踪
```

## 最终验证清单
- [ ] 所有测试通过: `npm test`
- [ ] 无 lint 错误: `npm run lint`
- [ ] 无类型错误: `npm run type-check`
- [ ] 手动测试成功: [具体的 curl/命令]
- [ ] 错误情况得到优雅处理
- [ ] 日志信息丰富但不冗长
- [ ] 文档已更新（如需要）

---

## 要避免的反模式
- ❌ 当现有模式有效时不要创建新模式
- ❌ 不要因为"应该可以工作"而跳过验证
- ❌ 不要忽略失败的测试 - 修复它们
- ❌ 不要在异步上下文中使用同步函数
- ❌ 不要硬编码应该是配置的值
- ❌ 不要捕获所有异常 - 要具体
