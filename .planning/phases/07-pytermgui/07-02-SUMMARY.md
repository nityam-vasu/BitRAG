---
phase: 07-pytermgui
plan: 02
type: execute
subsystem: tui-widgets
tags: [pytermgui, widgets, tui]
dependency_graph:
  requires: [07-01]
  provides: [bitrag.tui.widgets.ChatDisplay, bitrag.tui.widgets.InputWidget, bitrag.tui.widgets.Sidebar]
  affects: [src/bitrag/tui/main.py]
tech-stack:
  added: []
  patterns: [observer-pattern, callback-pattern]
key-files:
  created:
    - src/bitrag/tui/widgets.py
decisions:
  - Used callback pattern for event handling (on_submit, on_cancel, on_session_select)
  - ChatMessage class encapsulates message data with role, content, timestamp, sources
  - Widgets are lazy-loaded (created on first access)
---

# Plan 07-02: Core TUI Components - Summary

## Objective

Create core TUI widgets: message display, input field, and sidebar.

## What Was Done

### 1. ChatMessage Class

Represents a single chat message with:
- `role`: user, assistant, or system
- `content`: message text
- `timestamp`: datetime object
- `sources`: list of source citations

Properties:
- `formatted_time`: HH:MM format
- `is_user`, `is_assistant`: role checks

### 2. ChatDisplay Widget

Displays chat messages with:
- **User messages**: Right-aligned, green color
- **Assistant messages**: Left-aligned, cyan color
- **System messages**: Centered, dimmed
- **Timestamps**: Shown for all messages
- **Source citations**: Displayed for assistant messages

Methods:
- `add_message()`, `add_user_message()`, `add_assistant_message()`, `add_system_message()`
- `clear()`: Clear all messages
- `get_widget()`: Get PyTermGUI window

### 3. InputWidget

Single-line text input with:
- **Customizable prompt** (default: "You: ")
- **Placeholder text**
- **Submit callback** (Enter key)
- **Cancel callback** (Escape key)

Methods:
- `set_focus()`: Set input focus

### 4. Sidebar Widget

Session/conversation list with:
- **Session list display** with active highlight
- **Session selection** callback
- **New session** button callback
- **Delete session** button callback

Methods:
- `add_session()`, `remove_session()`
- `set_active_session()`

## Verification

- [x] ChatDisplay imports and creates
- [x] InputWidget imports and creates
- [x] Sidebar imports and creates
- [x] Widgets respond to callbacks

## Notes

- Widgets use lazy initialization (created on first access)
- Callbacks use closure pattern for passing data
- Ready for integration with main application in subsequent plans

## Commit

`73dd2a3` - feat(07-02): Add core TUI widgets
