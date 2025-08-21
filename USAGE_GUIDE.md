# Brain System Manager - Usage Guide

## Overview

The Brain System Manager provides an intelligent layer on top of the existing brain tools, implementing the operational framework WITHOUT modifying any core functionality.

## Key Features

1. **Enhanced Session Initialization** - Automatically loads context and selects appropriate behavior mode
2. **Human-in-the-Loop Updates** - Proposes changes for confirmation before saving
3. **Project Stack** - Switch between projects while preserving context
4. **Obsidian Dashboards** - Auto-generate project status dashboards
5. **Semantic Mode Selection** - Intelligently determines conversation type

## Quick Start

```python
from brain_manager import init_brain_manager

# Start a session
manager = init_brain_manager("Let's continue working on that API project")

# The system will:
# 1. Initialize brain
# 2. Load last session context
# 3. Detect this is project continuation
# 4. Load the API project context
# 5. Show current status
```

## Core Operations

### 1. Starting a Session

```python
# Simple start - analyzes your message to determine mode
manager = init_brain_manager("I want to research machine learning")

# The system detects "research" mode and loads appropriate behaviors
```

### 2. Updating Project Context

```python
# Propose an update
update = manager.propose_context_update("progress", {
    "completed_tasks": ["Setup authentication", "Create user model"],
    "new_tasks": ["Add error handling", "Write tests"],
    "current_focus": "Testing the authentication flow"
})

# System shows:
# 📝 Proposed progress update for 'api_project':
#   • Completed 2 tasks
#   • Added 2 new tasks  
#   • Changed focus to: Testing the authentication flow
# 
# Confirm these changes? (yes/no/edit):

# Save if confirmed
manager.confirm_and_save_update(update, confirmed=True)
```

### 3. Recording Decisions

```python
# Record an important decision
update = manager.propose_context_update("decision", {
    "decision": "Use JWT tokens for authentication",
    "rationale": "Stateless, scalable, and works well with microservices",
    "impact": "Need to implement token refresh mechanism"
})

# Confirms and saves to project history
```

### 4. Project Switching

```python
# Switch to another project (current project saved to stack)
manager.switch_project("ml_research")

# ... work on ML research ...

# Return to previous project
manager.return_to_previous_project()
# Restores full context of API project
```

### 5. Generate Obsidian Dashboard

```python
# Create a dashboard for current project
dashboard = manager.create_obsidian_dashboard("api_project", save_to_vault=True)

# Creates a formatted markdown file in Obsidian with:
# - Project status and summary
# - Current focus
# - Open tasks (with checkboxes)
# - Recent milestones
# - Key decisions with rationale
# - Links to key files
```

## Integration with Brain Tools

The manager uses these brain tools internally:

- `brain_init` - Session initialization
- `state_set/get` - Structured context storage
- `brain_remember/recall` - Long-term memory
- `obsidian_note` - Dashboard creation

## Conversation Modes

The system automatically detects and adapts to different conversation types:

1. **project_continuation** - Continuing existing work
2. **project_management** - New development tasks
3. **research** - Learning and exploration
4. **analysis** - Pattern finding and insights
5. **general_assistant** - General help

## Best Practices

1. **Start Every Session** with init_brain_manager()
2. **Confirm Updates** before saving to prevent context corruption
3. **Use Descriptive Updates** when recording progress
4. **Create Dashboards** regularly for visual project tracking
5. **Switch Projects Cleanly** using the stack mechanism

## Example Workflow

```python
# Day 1: Start a new project
manager = init_brain_manager("Create a new chat application")
# ... work on project ...
update = manager.propose_context_update("progress", {
    "summary": "Real-time chat app with websockets",
    "completed_tasks": ["Setup project structure", "Install dependencies"],
    "current_focus": "Implementing websocket server"
})
manager.confirm_and_save_update(update)

# Day 2: Continue where you left off
manager = init_brain_manager("Let's continue with the chat app")
# System loads context, shows you were working on websockets

# Need to research something?
manager.switch_project("websocket_research")
# ... research websockets ...
manager.return_to_previous_project()
# Back to chat app with full context

# Day 3: Record important decision
update = manager.propose_context_update("decision", {
    "decision": "Use Socket.IO instead of raw websockets",
    "rationale": "Better browser compatibility and reconnection handling"
})
manager.confirm_and_save_update(update)

# Generate status dashboard
manager.create_obsidian_dashboard("chat_app", save_to_vault=True)
```

## Troubleshooting

**Q: What if the wrong mode is selected?**
A: You can explicitly switch: "Switch to research mode" in your message

**Q: Can I edit proposed updates?**
A: Yes, modify the proposed_context in the update dict before confirming

**Q: How do I see all my projects?**
A: Use `state_list(category="project")` to see all stored projects

**Q: What if I forget to save context?**
A: The system auto-saves critical moments, but manual saves are recommended

## Advanced Features

### Custom Instruction Sets
```python
# Store custom instructions for a specific project type
brain_remember(
    key="ml_project_instructions",
    value={
        "name": "ML Project Mode",
        "behaviors": ["Track experiments", "Log metrics", "Version datasets"],
        "context_schema": {"experiments": [], "best_model": None, "metrics": {}}
    },
    type="instruction_set"
)
```

### Context Compression
The system automatically manages context size:
- Active context: Immediate project state (<2k tokens)
- Summary context: Compressed history (loaded on demand)
- Archive: Full details in brain memories

### Multi-User Considerations
Each user should have their own brain instance to avoid context collision.

## Future Enhancements

1. **Automated Testing** - Verify context updates don't break project flow
2. **Context Templates** - Pre-built schemas for common project types
3. **Collaboration Mode** - Share project contexts between sessions
4. **Analytics** - Track productivity patterns and optimize workflows

---

Remember: This system enhances the brain tools without replacing them. All original functionality remains available for direct use when needed.
