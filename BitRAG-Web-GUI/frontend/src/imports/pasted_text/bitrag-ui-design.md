Design a clean modern web UI for an AI document chat system called "BitRAG".

The interface should be minimal, developer-focused, and inspired by tools like ChatGPT, Cursor, and Claude.

Use a dark theme with subtle borders, terminal-style aesthetics, and simple typography.

--------------------------------------------------

PAGE 1 — MAIN CHAT INTERFACE

Layout structure:

Top Navigation Bar
- Left: "BitRAG" project title
- Left side button: "Documents"
- Right side button: "Settings"

Below the navbar is the main workspace.

Main Workspace Layout:
- Large chat conversation area centered
- Messages appear in stacked message blocks
- Model outputs should support markdown formatting

Bottom Chat Bar:
- Left: File Upload button/icon
- Middle: Large input field for user queries
- Right: Send button

The file upload button allows users to upload multiple documents by providing file paths.

--------------------------------------------------

CHAT RESPONSE STRUCTURE

When the AI responds, show three sections:

1. User Query
A boxed section displaying the user's prompt.

2. Thinking Section
- Appears only if the model supports reasoning
- Collapsible panel
- Displays reasoning steps
- Supports markdown rendering

3. Model Output
Large response area showing the final answer in markdown.

4. Sources Button
A button below the response.
When clicked, open a modal showing documents used as references.

Sources Modal Layout:
List of referenced documents:
- document1.pdf
- report.md
- notes.txt

--------------------------------------------------

PAGE 2 — SETTINGS PAGE

Settings page contains configuration options.

Sections:

Ollama Configuration
- Input field for Ollama port
- Default port shown

Model Selection
Dropdown to choose the active model.

Model Download
Button opens modal with:
- List of available models
- Option to enter a custom model name
- Download progress bar

Model Delete
Modal showing installed models with delete buttons.

Dual Model Mode
Toggle switch.

If enabled:
Show dropdowns to choose Model 1 and Model 2.

Include warning text:
"Using two models increases inference time and resource usage."

Hybrid Retrieval Slider
3-point slider:
-1 = Vector Search
0 = Hybrid Search
1 = Keyword Search

Button linking to Document Management page.

--------------------------------------------------

PAGE 3 — DOCUMENT MANAGEMENT

Document management page for indexing documents.

Sections:

Indexed Documents List
Display list of uploaded documents.

Each document entry shows:
Document name
Delete button

Upload Document
Button opens modal with:
File path input
Submit button

When uploading:
Show indexing progress bar.

After completion:
Show success notification.

When deleting:
Show progress indicator then confirmation message.

--------------------------------------------------

GLOBAL UI ELEMENTS

Header System Status Bar
Display system usage indicators:

CPU usage
Memory usage
GPU usage

Example:
CPU 5% | Memory 2GB / 16GB | GPU 56%

Footer Shortcuts Bar

Display keyboard shortcuts:

C → Chat
S → Settings
U → Upload

--------------------------------------------------

DESIGN STYLE

Dark theme
Clean modern layout
Rounded cards
Subtle shadows
Monospace font for code blocks
Minimal icons
Terminal-inspired aesthetic
Responsive layout

Use a developer-focused interface similar to AI developer tools.