---
inclusion: always
---

# Deep Agents Reference

When implementing Deep Agents features, always search the LangChain documentation using the MCP tool before writing code.

## When to Search Docs

- Before implementing planning (write_todos)
- Before implementing filesystem operations (read_file, write_file, edit_file, ls)
- Before implementing sub-agents (task delegation)
- Before configuring checkpointers
- When encountering errors with Deep Agents
- When unsure about best practices

## Search Examples

```
Use mcp_docs_langchain_SearchDocsByLangChain with queries like:
- "Deep Agents write_todos planning"
- "Deep Agents filesystem write_file"
- "Deep Agents sub-agents task delegation"
- "Deep Agents checkpointer PostgreSQL"
- "Deep Agents human-in-the-loop interrupt"
```

## Official Patterns

Follow these official Deep Agents patterns:
1. **Planning** - Use write_todos for task decomposition
2. **Context Management** - Offload data to filesystem to prevent context overflow
3. **Sub-agents** - Delegate complex tasks for context isolation

Always reference official documentation over custom implementations.
