---
inclusion: always
---

# Production Practices

## Configuration

- Use environment variables for all config (API keys, URLs, settings)
- Never hardcode secrets or API keys
- Provide .env.example with placeholder values

## Data Validation

- Use Pydantic models for all API request/response data
- Validate user input before processing
- Return clear error messages to users

## Logging

- Log important events (agent start, completion, errors)
- Don't log sensitive data (API keys, user info)
- Keep logs concise and actionable

## Async Operations

- Use async/await for all I/O operations (API calls, database queries)
- Don't block the event loop
- Handle concurrent operations properly

## Code Documentation

- Write docstrings for public functions only
- Include parameter types and return types
- Keep docstrings brief and clear

## Simplicity First

- Start with the simplest solution that works
- Add complexity only when necessary
- Ask questions when requirements are unclear
- Prefer proven patterns over custom solutions

## When to Ask Questions

- When requirements are ambiguous
- When multiple approaches are possible
- When unsure about user preferences
- Before making architectural decisions
