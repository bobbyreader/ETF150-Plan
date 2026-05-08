## CLAUDE.md速查模板

最后，附一份精简版的CLAUDE.md模板，你可以直接复制到自己项目里用：

1. `# 开发工作流`
2. `**始终使用 bun，不要用 npm**`
3. `## 常用命令`
4. `-类型检查（快）：bun run typecheck`
5. `-跑单个测试：bun run test ---t "测试名"`
6. `-跑指定文件测试：bun run test:file --"glob"`
7. `-Lint检查：bun run lint:file --"file1.ts"`
8. `-提PR前必做：bun run lint && bun run test`
9. `## 代码规范`
10. `-用 type 不用interface`
11. `-永远不要用enum，用string literal union`
12. `-变量命名用 camelCase`
13. `-文件命名用 kebab-case`
14. `## Claude行为规范`
15. `-改代码前先跑 typecheck`
16. `-每次改动后立刻跑相关测试`
17. `-不确定的地方先问，不要猜`
18. `- commit message 用英文，格式：<type>:<description>`
19. `## 常见错误（遇到就加）`
20. `-[这里放Claude犯过的具体错误和修复规则]`
