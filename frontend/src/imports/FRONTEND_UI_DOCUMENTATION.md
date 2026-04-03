# BitRAG Frontend UI/UX Documentation

> Complete UI/UX specification for recreation/rebuilding purposes.

---

## 1. GLOBAL LAYOUT & STRUCTURE

### 1.1 App Container
```tsx
<div className="flex h-screen bg-gray-900 text-gray-100">
```
- **Layout**: Flexbox, horizontal direction
- **Height**: `h-screen` (100vh)
- **Background**: `#1f2937` (Tailwind `gray-900`)
- **Text Color**: `rgba(255, 255, 255, 0.87)` (from index.css)
- **Root element**: `#root { width: 100%; height: 100vh; }`

### 1.2 Sidebar (Left Panel)
```tsx
<aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
```
- **Width**: `w-64` (16rem / 256px)
- **Background**: `#1f2937` (`gray-800`)
- **Border**: Right border, `1px solid #374151` (`gray-700`)
- **Layout**: Flex column
- **Structure**:
  - Header (logo): `p-4 border-b border-gray-700`
  - Navigation: `flex-1 p-4` with `ul.space-y-2`
  - Footer: `p-4 border-t border-gray-700`

### 1.3 Main Content Area
```tsx
<main className="flex-1 overflow-hidden">
```
- **Width**: `flex-1` (fills remaining space)
- **Overflow**: Hidden (scroll handled by children)

---

## 2. SIDEBAR COMPONENT

### 2.1 Logo Section
```tsx
<div className="p-4 border-b border-gray-700">
  <h1 className="text-xl font-bold text-blue-400">BitRAG</h1>
  <p className="text-xs text-gray-400">Local RAG Chat</p>
</div>
```
- **Logo**: `text-xl font-bold`, color `#60a5fa` (`blue-400`)
- **Subtitle**: `text-xs`, color `#9ca3af` (`gray-400`)

### 2.2 Navigation Items
```tsx
<NavLink className={({ isActive }) =>
  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
    isActive
      ? 'bg-blue-600 text-white'
      : 'text-gray-300 hover:bg-gray-700'
  }`
}>
  <Icon size={20} />
  <span>{label}</span>
</NavLink>
```
- **Nav Items**:
  - `/chat` → MessageSquare icon → "Chat"
  - `/documents` → FileText icon → "Documents"
  - `/graph` → Network icon → "Graph"
  - `/ollama-params` → Activity icon → "Ollama Params"
  - `/settings` → Settings icon → "Settings"
- **Icon Size**: `20px`
- **Padding**: `px-4 py-3` (horizontal 16px, vertical 12px)
- **Gap**: `gap-3` (12px)
- **Border Radius**: `rounded-lg` (8px)
- **Active State**:
  - Background: `#2563eb` (`blue-600`)
  - Text: White
- **Inactive State**:
  - Text: `#d1d5db` (`gray-300`)
  - Hover: Background `#374151` (`gray-700`)
- **Transition**: `transition-colors`

### 2.3 Footer
```tsx
<div className="p-4 border-t border-gray-700">
  <p className="text-xs text-gray-500">Powered by Ollama & ChromaDB</p>
</div>
```
- **Text**: `text-xs`, color `#6b7280` (`gray-500`)

---

## 3. CHAT PAGE (`/chat`)

### 3.1 Header
```tsx
<header className="p-4 border-b border-gray-700 bg-gray-800">
  <div className="flex items-center justify-between">
    <h2 className="text-xl font-semibold">Chat</h2>
    <button className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50">
      <Download size={16} />
      Export Chat
    </button>
  </div>
</header>
```
- **Background**: `bg-gray-800`
- **Title**: `text-xl font-semibold`
- **Export Button**:
  - Background: `bg-gray-700` → `hover:bg-gray-600`
  - Padding: `px-4 py-2`
  - Border: `rounded-lg`
  - Icon: `Download size={16}`
  - Gap: `gap-2`
  - Disabled opacity: `opacity-50`

### 3.2 Messages Container
```tsx
<div className="flex-1 overflow-y-auto p-4 space-y-4">
```
- **Overflow**: `overflow-y-auto`
- **Padding**: `p-4` (16px)
- **Spacing**: `space-y-4` (gap between messages)

### 3.3 User Message Bubble
```tsx
<div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
  <div className={`max-w-[70%] rounded-lg p-4 ${
    message.type === 'user'
      ? 'bg-blue-600 text-white'
      : 'bg-gray-700 text-gray-100'
  }`}>
```
- **Alignment**: Flex, `justify-end` (user) / `justify-start` (assistant)
- **Max Width**: `max-w-[70%]`
- **Padding**: `p-4` (16px)
- **Border Radius**: `rounded-lg`
- **User Bubble**:
  - Background: `#2563eb` (`blue-600`)
  - Text: White
- **Assistant Bubble**:
  - Background: `#374151` (`gray-700`)
  - Text: `#f3f4f6` (`gray-100`)

### 3.4 Thinking Display
```tsx
<details className="mb-2 text-sm opacity-75">
  <summary className="cursor-pointer">Thinking...</summary>
  <pre className="mt-1 p-2 bg-gray-800 rounded text-xs whitespace-pre-wrap">
    {message.thinking}
  </pre>
</details>
```
- **Container**: `details`, margin bottom `mb-2`, font `text-sm`, opacity `75%`
- **Summary**: Cursor pointer, "Thinking..." label
- **Content**: `pre` tag, background `bg-gray-800`, padding `p-2`, border `rounded`, font `text-xs`, `whitespace-pre-wrap`

### 3.5 Markdown Content
```tsx
<div className="prose prose-invert prose-sm max-w-none">
  <ReactMarkdown>{message.content}</ReactMarkdown>
</div>
```
- **Tailwind Typography**: `prose prose-invert prose-sm max-w-none`

### 3.6 Sources Display
```tsx
<div className="mt-2 pt-2 border-t border-gray-600 text-xs text-gray-300">
  Sources: {message.sources.join(', ')}
</div>
```
- **Margin Top**: `mt-2`
- **Padding Top**: `pt-2`
- **Border**: Top `border-t border-gray-600`
- **Font**: `text-xs`
- **Text Color**: `#d1d5db` (`gray-300`)

### 3.7 Loading State
```tsx
<div className="flex justify-start">
  <div className="bg-gray-700 rounded-lg p-4">
    <Loader2 className="animate-spin" size={20} />
  </div>
</div>
```
- **Icon**: `Loader2` with `animate-spin` class
- **Size**: `20px`

### 3.8 Input Area
```tsx
<form className="p-4 border-t border-gray-700 bg-gray-800">
  <div className="flex gap-2">
    <input type="text" className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-50" />
    <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
      <Send size={18} />
      Send
    </button>
  </div>
</form>
```
- **Background**: `bg-gray-800`
- **Border Top**: `border-t border-gray-700`
- **Input Field**:
  - Flex: `flex-1` (fills space)
  - Padding: `px-4 py-3`
  - Background: `bg-gray-700`
  - Border: `border border-gray-600`
  - Border Radius: `rounded-lg`
  - Focus: `focus:border-blue-500` (blue border on focus)
  - Placeholder color: Default gray
  - Disabled: `disabled:opacity-50`
- **Send Button**:
  - Background: `bg-blue-600` → `hover:bg-blue-700`
  - Padding: `px-6 py-3`
  - Border: `rounded-lg`
  - Disabled: `opacity-50 cursor-not-allowed`
  - Icon: `Send size={18}`
  - Gap: `gap-2`
  - Text: "Send" after icon

### 3.9 Empty State
```tsx
<div className="text-center py-8 text-gray-400">
  <p>No documents indexed yet.</p>
  <p className="text-sm mt-2">Go to Documents page to upload PDFs.</p>
</div>
```
- **Alignment**: `text-center`
- **Padding**: `py-8`
- **Text**: `text-gray-400`
- **Secondary text**: `text-sm`, margin top `mt-2`

---

## 4. DOCUMENTS PAGE (`/documents`)

### 4.1 Header
```tsx
<header className="p-4 border-b border-gray-700 bg-gray-800">
  <div className="flex items-center justify-between">
    <h2 className="text-xl font-semibold">Documents</h2>
    <div>
      <input type="file" className="hidden" />
      <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">
        {uploading ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
        Upload Documents
      </button>
    </div>
  </div>
</header>
```
- **Upload Button**:
  - Icon: `Loader2` (spinning) when uploading, else `Upload`
  - Icon size: `16px`
  - Text: "Upload Documents"
  - Same button styles as Chat page

### 4.2 Error Message
```tsx
<div className="mb-4 p-3 bg-red-600/20 border border-red-600 rounded-lg text-red-300">
```
- **Background**: `bg-red-600/20` (20% opacity red)
- **Border**: `border-red-600`
- **Border Radius**: `rounded-lg`
- **Text**: `text-red-300`
- **Padding**: `p-3`

### 4.3 Loading State
```tsx
<div className="flex items-center justify-center py-12">
  <Loader2 className="animate-spin text-blue-500" size={32} />
</div>
```
- **Icon**: `Loader2 animate-spin`
- **Color**: `text-blue-500`
- **Size**: `32px`

### 4.4 Empty State
```tsx
<div className="text-center py-12 text-gray-400">
  <FileText size={48} className="mx-auto mb-4 opacity-50" />
  <p>No documents uploaded yet</p>
  <p className="text-sm mt-2">Click "Upload Documents" to get started</p>
</div>
```
- **Icon**: `FileText size={48}`, centered (`mx-auto`), margin bottom `mb-4`, opacity `50%`
- **Text**: Same as Chat empty state

### 4.5 Document List Item
```tsx
<div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg hover:bg-gray-750">
  <div className="flex items-center gap-3">
    <FileText className="text-blue-400" size={24} />
    <span className="font-medium">{doc.name}</span>
  </div>
  <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded">
    <Trash2 size={18} />
  </button>
</div>
```
- **Container**:
  - Padding: `p-4`
  - Background: `bg-gray-800` → `hover:bg-gray-750` (subtle change)
  - Border: `rounded-lg`
- **File Icon**:
  - Icon: `FileText size={24}`
  - Color: `#60a5fa` (`text-blue-400`)
- **File Name**: `font-medium`
- **Delete Button**:
  - Padding: `p-2`
  - Default: `text-gray-400`
  - Hover: `text-red-400` + `bg-red-400/10` (10% opacity red background)
  - Border: `rounded`
  - Icon: `Trash2 size={18}`

### 4.6 Footer
```tsx
<div className="p-4 border-t border-gray-700 bg-gray-800">
  <p className="text-sm text-gray-400">
    {documents.length} document{documents.length !== 1 ? 's' : ''} indexed
  </p>
</div>
```
- **Background**: `bg-gray-800`
- **Border Top**: `border-t border-gray-700`
- **Text**: `text-sm`, `text-gray-400`

---

## 5. SETTINGS PAGE (`/settings`)

### 5.1 Layout
```tsx
<div className="h-full overflow-y-auto">
  <div className="max-w-2xl mx-auto p-8">
```
- **Container**: `h-full overflow-y-auto`
- **Content**: `max-w-2xl mx-auto p-8` (max width 672px, centered)

### 5.2 Section: System Information (Collapsible)
```tsx
<div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
  <button className="w-full p-4 flex items-center justify-between hover:bg-gray-700/50 transition-colors">
    <div className="flex items-center gap-3">
      <CircuitBoard className="text-blue-400" size={20} />
      <span className="font-semibold">System Information</span>
      <span className="text-xs text-gray-500">(Click to collapse/expand)</span>
    </div>
    {systemInfoExpanded ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
  </button>
</div>
```
- **Container**: `bg-gray-800`, `border border-gray-700`, `rounded-lg`
- **Button**: Full width, padding `p-4`, hover `bg-gray-700/50`
- **Icon**: `CircuitBoard` with `text-blue-400`
- **Chevron**: `ChevronUp` or `ChevronDown`, `text-gray-400`, size `20`

### 5.3 System Info Grid
```tsx
<div className="grid grid-cols-2 gap-4 mt-4">
  {/* Each card */}
  <div className="bg-gray-700/50 rounded-lg p-3">
    <div className="flex items-center gap-2 text-gray-400 mb-1">
      <Cpu size={16} />
      <span className="text-xs uppercase">CPU</span>
    </div>
    <p className="font-medium">{value}</p>
    <p className="text-xs text-gray-500">{description}</p>
  </div>
</div>
```
- **Grid**: 2 columns, `gap-4`
- **Card**: `bg-gray-700/50`, `rounded-lg`, `p-3`
- **Label Row**: Flex, gap `2`, `text-gray-400`, `text-xs uppercase`, margin bottom `mb-1`
- **Value**: `font-medium`
- **Description**: `text-xs`, `text-gray-500`

### 5.4 Ollama Status Section
```tsx
<div className="p-4 bg-gray-800 rounded-lg">
  <h3 className="font-semibold mb-2">Ollama Status</h3>
  <div className="flex items-center gap-2">
    <span className={`w-3 h-3 rounded-full ${status === 'running' ? 'bg-green-500' : 'bg-red-500'}`} />
    <span className="capitalize">{status}</span>
  </div>
  <p className="text-sm text-gray-400 mt-2">{documentCount} documents indexed</p>
</div>
```
- **Indicator**: 12px circle (`w-3 h-3 rounded-full`), green `#22c55e` or red `#ef4444`
- **Status Text**: `capitalize`

### 5.5 Model Selection (Select Dropdown)
```tsx
<div className="p-4 bg-gray-800 rounded-lg">
  <div className="flex items-center justify-between mb-4">
    <h3 className="font-semibold">Chat Model</h3>
    <button className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
      <RefreshCw size={14} />
      Refresh
    </button>
  </div>
  <select className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500">
```
- **Dropdown**: Full width, `px-4 py-2`, `bg-gray-700`, `border-gray-600`, focus border `blue-500`

### 5.6 Toggle Switch (Hybrid Mode / Dual Mode)
```tsx
<div className="p-4 bg-gray-800 rounded-lg">
  <label className="flex items-center justify-between cursor-pointer">
    <div>
      <h3 className="font-semibold">Hybrid Search</h3>
      <p className="text-sm text-gray-400">Combine vector and keyword search</p>
    </div>
    <input type="checkbox" className="w-5 h-5 rounded" />
  </label>
</div>
```
- **Checkbox**: `w-5 h-5`, `rounded`
- **Description**: `text-sm`, `text-gray-400`

### 5.7 Number Input
```tsx
<input type="number" className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500" />
```
- Same styling as dropdown

### 5.8 Save Button (Full Width)
```tsx
<button className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
  {saving ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
  Save Settings
</button>
```
- **Width**: `w-full`
- **Height**: `py-3` (12px vertical)
- **Background**: `bg-blue-600` → hover `bg-blue-700`
- **Font**: `font-semibold`
- **Icon + Text**: Centered with `justify-center`, gap `gap-2`

### 5.9 Success/Error Message
```tsx
<div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
  message.type === 'success' ? 'bg-green-600/20 text-green-300' : 'bg-red-600/20 text-red-300'
}`}>
  {message.type === 'success' ? <CheckCircle size={20} /> : <XCircle size={20} />}
  {message.text}
</div>
```
- **Success**: Background `#22c55e20`, text `#34d399` (`green-300`)
- **Error**: Background `#ef444420`, text `#f87171` (`red-300`)
- **Icon**: `CheckCircle` or `XCircle`, size `20`

---

## 6. GRAPH PAGE (`/graph`)

### 6.1 Header with Controls
```tsx
<header className="p-4 border-b border-gray-700 bg-gray-800">
  <div className="flex items-center justify-between">
    <h2 className="text-xl font-semibold">Knowledge Graph</h2>
    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">
      <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
      Refresh
    </button>
  </div>
  {/* Search Row */}
  <div className="mt-4 flex items-center gap-4">
    <div className="relative flex-1 max-w-md">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
      <input className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500" />
    </div>
    <div className="flex items-center gap-1">
      <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Zoom In"><ZoomIn size={16} /></button>
      <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Zoom Out"><ZoomOut size={16} /></button>
      <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Fit to Screen"><Maximize2 size={16} /></button>
    </div>
    <div className="text-sm text-gray-400">{nodes} nodes, {links} links</div>
  </div>
</header>
```
- **Refresh Button**: Same as Chat export button
- **Search Input**:
  - Wrapper: `relative flex-1 max-w-md`
  - Search Icon: Absolute, `left-3`, vertically centered (`-translate-y-1/2`), `text-gray-400`
  - Input: `pl-10` (padding-left for icon), `pr-4`, `py-2`, `bg-gray-700`, border `gray-600`, focus `blue-500`
- **Zoom Controls**:
  - Button: `p-2`, `bg-gray-700` → `hover:bg-gray-600`, `rounded`
  - Icons: `ZoomIn`, `ZoomOut`, `Maximize2` size `16`
- **Stats**: `text-sm`, `text-gray-400`

### 6.2 Graph Container
```tsx
<div className="flex-1 relative" ref={graphRef}>
  {loading && (
    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
      <RefreshCw className="animate-spin text-blue-500" size={32} />
    </div>
  )}
</div>
```
- **Container**: Flex `flex-1`, `relative` (for absolute overlays)
- **Loading Overlay**: `absolute inset-0`, `bg-gray-900/80` (80% opacity), flex centered, z-index `10`

### 6.3 Node Colors (Group Mapping)
```tsx
const GROUP_COLORS: Record<number, string> = {
  1: '#3b82f6', // blue - documents
  2: '#22c55e', // green - text files
  3: '#f59e0b', // amber - code
  4: '#ec4899', // pink - images
  5: '#6b7280', // gray - other
}
```
- **Group 1 (Documents)**: `#3b82f6` (blue-500)
- **Group 2 (Text)**: `#22c55e` (green-500)
- **Group 3 (Code)**: `#f59e0b` (amber-500)
- **Group 4 (Images)**: `#ec4899` (pink-500)
- **Group 5 (Other)**: `#6b7280` (gray-500)

### 6.4 Node Details Panel (Right Sidebar)
```tsx
<div className="w-80 border-l border-gray-700 bg-gray-800 p-4 overflow-y-auto">
  <div className="flex items-center justify-between mb-4">
    <h3 className="font-semibold text-lg">Node Details</h3>
    <button className="text-gray-400 hover:text-white">×</button>
  </div>
  <div className="space-y-4">
    <div>
      <label className="text-xs text-gray-400 uppercase">Name</label>
      <p className="font-medium">{name}</p>
    </div>
    <div>
      <label className="text-xs text-gray-400 uppercase">Category</label>
      <p className="font-medium">
        <span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: GROUP_COLORS[group] }} />
        {categoryName}
      </p>
    </div>
    <div>
      <label className="text-xs text-gray-400 uppercase">Summary</label>
      <p className="text-sm text-gray-300">{summary}</p>
    </div>
    <div>
      <label className="text-xs text-gray-400 uppercase">Tags</label>
      <div className="flex flex-wrap gap-2 mt-1">
        <span className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-xs">{tag}</span>
      </div>
    </div>
  </div>
</div>
```
- **Width**: `w-80` (320px)
- **Border Left**: `border-l border-gray-700`
- **Close Button**: `text-gray-400` → `hover:text-white`, text "×"
- **Field Labels**: `text-xs uppercase text-gray-400`
- **Values**: `font-medium` for name, `text-sm text-gray-300` for summary
- **Category Dot**: `inline-block w-3 h-3 rounded-full`, margin right `mr-2`
- **Tags**: Flex wrap, gap `2`, tag style `px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-xs`

### 6.5 Legend (Bottom Bar)
```tsx
<div className="p-4 border-t border-gray-700 bg-gray-800">
  <div className="flex items-center gap-6 text-sm">
    <span className="text-gray-400">Legend:</span>
    {Object.entries(GROUP_COLORS).map(([group, color]) => (
      <div key={group} className="flex items-center gap-2">
        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-gray-300">{label}</span>
      </div>
    ))}
  </div>
</div>
```
- **Labels**: "Documents", "Text Files", "Code", "Images", "Other"
- **Color dots**: `w-3 h-3 rounded-full`
- **Text**: `text-gray-300`

---

## 7. OLLAMA PARAMS PAGE (`/ollama-params`)

### 7.1 Page Header
```tsx
<div className="flex items-center gap-3 mb-6">
  <Activity className="text-blue-400" size={28} />
  <div>
    <h2 className="text-2xl font-semibold">Custom Ollama Parameters</h2>
    <p className="text-sm text-gray-400">Optimize model performance for your hardware</p>
  </div>
</div>
```
- **Icon**: `Activity` with `text-blue-400`, size `28`
- **Title**: `text-2xl font-semibold`
- **Subtitle**: `text-sm text-gray-400`

### 7.2 System Info Banner
```tsx
<div className="mb-6 p-4 bg-blue-600/20 border border-blue-600/30 rounded-lg">
  <div className="flex items-center gap-2 mb-2">
    <Info size={18} className="text-blue-400" />
    <span className="font-semibold text-blue-300">Your System</span>
  </div>
  <div className="grid grid-cols-2 gap-4 text-sm">
    <div><span className="text-gray-400">CPU Cores:</span><span className="ml-2 font-mono text-white">{cpu}</span></div>
    <div><span className="text-gray-400">Recommended Threads:</span><span className="ml-2 font-mono text-green-400">{threads}</span></div>
  </div>
</div>
```
- **Background**: `bg-blue-600/20`
- **Border**: `border-blue-600/30`
- **Title**: `font-semibold text-blue-300`
- **Values**: `font-mono text-white` or `text-green-400`

### 7.3 Preset Cards (Quick Presets)
```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <button className={`p-4 rounded-lg border text-left transition-all hover:scale-[1.02] ${
    activeConfigId === preset.id
      ? 'bg-blue-600/30 border-blue-500'
      : 'bg-gray-800 border-gray-700 hover:border-gray-600'
  }`}>
    <div className="flex items-center gap-2 mb-2">
      <span className="text-blue-400">{preset.icon}</span>
      <span className="font-semibold">{preset.name}</span>
      {activeConfigId === preset.id && <Check size={16} className="ml-auto text-green-400" />}
    </div>
    <p className="text-xs text-gray-400 mb-2">{preset.hardware}</p>
    <p className="text-sm text-gray-300">{preset.description}</p>
    <div className="mt-3 text-xs text-gray-500 font-mono">
      threads={preset.params.threads} | batch={preset.params.batch} | ctx={preset.params.ctx}
    </div>
  </button>
</div>
```
- **Grid**: 1 column mobile, 3 columns (`md:grid-cols-3`), gap `4`
- **Card**:
  - Padding: `p-4`
  - Border radius: `rounded-lg`
  - Active: `bg-blue-600/30`, `border-blue-500`
  - Inactive: `bg-gray-800`, `border-gray-700`
  - Hover: Scale `1.02`, border `gray-600`
  - Transition: `transition-all`
- **Check Icon**: `ml-auto`, `text-green-400`
- **Hardware/Description**: `text-xs text-gray-400`, `text-sm text-gray-300`
- **Params Display**: `text-xs text-gray-500 font-mono`

### 7.4 Custom Configuration Section
```tsx
<div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    {/* Each Input */}
    <div>
      <label className="block text-sm font-medium mb-2">
        <span className="text-gray-300">--parameter</span>
        <span className="text-gray-500 ml-2">(Description)</span>
      </label>
      <input type="number" className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 font-mono" />
      <p className="mt-1 text-xs text-gray-500">Help text</p>
    </div>
  </div>
</div>
```
- **Container**: `bg-gray-800`, `p-6`, `border border-gray-700`, `rounded-lg`
- **Grid**: 2 columns, gap `6`
- **Input**: Same as Settings page dropdown styling, `font-mono`
- **Help Text**: `mt-1 text-xs text-gray-500`

### 7.5 Radio Buttons (MMAP)
```tsx
<div className="flex gap-4">
  <label className="flex items-center gap-2 cursor-pointer">
    <input type="radio" checked={value === 1} onChange={() => updateParam(1)} className="w-4 h-4" />
    <span className="text-sm">Enabled (1)</span>
  </label>
</div>
```
- **Radio**: `w-4 h-4`
- **Label**: `text-sm`

### 7.6 Checkbox (NUMA)
```tsx
<label className="flex items-center gap-2 cursor-pointer">
  <input type="checkbox" checked={value} onChange={e => updateParam(e.target.checked)} className="w-5 h-5 rounded" />
  <span className="text-sm">Enable NUMA optimization</span>
</label>
```
- **Checkbox**: `w-5 h-5 rounded`

### 7.7 Command Preview
```tsx
<div className="mt-6 pt-6 border-t border-gray-700">
  <h4 className="text-sm font-medium mb-2 text-gray-400">Command Preview</h4>
  <code className="block p-3 bg-gray-900 rounded-lg text-sm font-mono text-green-400 overflow-x-auto">
    {command}
  </code>
</div>
```
- **Container**: Margin top `mt-6`, padding top `pt-6`, border top `border-gray-700`
- **Code Block**: `bg-gray-900`, `p-3`, `rounded-lg`, `text-sm font-mono text-green-400`

### 7.8 Save/Apply Buttons
```tsx
<button className="px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm flex items-center gap-1">
  <Save size={14} />
  Save Config
</button>
<button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-1">
  <Check size={14} />
  Apply
</button>
```
- **Save Config (Green)**: `bg-green-600` → `hover:bg-green-700`
- **Apply (Blue)**: `bg-blue-600` → `hover:bg-blue-700`
- **Size**: `px-3 py-1.5` (smaller than full-width buttons)
- **Text**: `text-sm`

### 7.9 Saved Configurations List
```tsx
<div className={`p-4 rounded-lg border flex items-center justify-between ${
  activeConfigId === config.id
    ? 'bg-green-600/20 border-green-600/50'
    : 'bg-gray-800 border-gray-700'
}`}>
  <div>
    <div className="flex items-center gap-2">
      <span className="font-semibold">{config.name}</span>
      {activeConfigId === config.id && <span className="px-2 py-0.5 bg-green-600/50 rounded text-xs">Active</span>}
    </div>
    <div className="mt-1 text-xs text-gray-500 font-mono">params</div>
  </div>
  <div className="flex gap-2">
    <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-1"><Check size={14} />Load</button>
    <button className="p-1.5 bg-red-600/30 hover:bg-red-600/50 rounded-lg text-red-400"><Trash2 size={14} /></button>
  </div>
</div>
```
- **Active Card**: `bg-green-600/20 border-green-600/50`
- **Inactive Card**: `bg-gray-800 border-gray-700`
- **Badge**: `px-2 py-0.5 bg-green-600/50 rounded text-xs`
- **Load Button**: Same as Apply button
- **Delete Button**: `p-1.5`, `bg-red-600/30`, hover `bg-red-600/50`, `text-red-400`

### 7.10 Modal (Save Configuration)
```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
    <h3 className="text-lg font-semibold mb-4">Save Configuration</h3>
    <input type="text" className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 mb-4" autoFocus />
    <div className="flex gap-2 justify-end">
      <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">Cancel</button>
      <button className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-1"><Save size={16} />Save</button>
    </div>
  </div>
</div>
```
- **Overlay**: `fixed inset-0 bg-black/50` (50% black overlay), `flex items-center justify-center`, z-index `50`
- **Modal**: `bg-gray-800`, `p-6`, `max-w-md`, `border border-gray-700`, `rounded-lg`
- **Cancel Button**: `bg-gray-700` → `hover:bg-gray-600`
- **Save Button**: `bg-green-600` → `hover:bg-green-700`

---

## 8. SHARED COMPONENTS & STYLES

### 8.1 Icons Used (from lucide-react)
| Icon | Usage |
|------|-------|
| `MessageSquare` | Chat nav |
| `FileText` | Documents nav, file icons |
| `Network` | Graph nav |
| `Settings` | Settings nav |
| `Activity` | Ollama Params nav |
| `Send` | Chat submit |
| `Download` | Export chat |
| `Upload` | Upload documents |
| `Trash2` | Delete document/config |
| `Loader2` | Loading spinner |
| `RefreshCw` | Refresh models/params |
| `Save` | Save buttons |
| `CheckCircle` | Success message |
| `XCircle` | Error message |
| `ChevronDown` | Collapsible expand |
| `ChevronUp` | Collapsible collapse |
| `Search` | Graph search |
| `ZoomIn` | Graph zoom |
| `ZoomOut` | Graph zoom |
| `Maximize2` | Graph fit |
| `Cpu` | CPU info |
| `Monitor` | OS info |
| `HardDrive` | RAM info |
| `CircuitBoard` | GPU info |
| `Zap` | Presets |
| `Server` | Server preset |
| `Laptop` | Laptop preset |
| `Info` | Info banner |
| `Plus` | Add config (unused) |
| `Edit2` | Edit (unused) |
| `Check` | Apply/active indicator |

### 8.2 Color Palette
| Name | Hex Code | Usage |
|------|----------|-------|
| `gray-900` | `#111827` | App background, body |
| `gray-800` | `#1f2937` | Cards, sidebar, headers |
| `gray-750` | `#293548` | Document hover |
| `gray-700` | `#374151` | Input backgrounds, borders |
| `gray-600` | `#4b5563` | Borders, secondary elements |
| `gray-500` | `#6b7280` | Disabled, secondary text |
| `gray-400` | `#9ca3af` | Placeholder, secondary |
| `gray-300` | `#d1d5db` | Body text |
| `gray-100` | `#f3f4f6` | Primary text |
| `blue-600` | `#2563eb` | Primary buttons, active nav |
| `blue-700` | `#1d4ed8` | Button hover |
| `blue-500` | `#3b82f6` | Focus border, links |
| `blue-400` | `#60a5fa` | Icons, accents |
| `blue-300` | `#93c5fd` | Active states |
| `green-500` | `#22c55e` | Success, running status |
| `green-400` | `#4ade80` | Active config indicator |
| `green-300` | `#86efac` | Success text |
| `red-500` | `#ef4444` | Error, delete |
| `red-400` | `#f87171` | Error hover |
| `red-300` | `#fca5a5` | Error text |
| `yellow-400` | `#facc15` | Warning |
| `amber-500` | `#f59e0b` | Code group |
| `pink-500` | `#ec4899` | Images group |

### 8.3 Typography
- **Font Family**: `Inter, system-ui, Avenir, Helvetica, Arial, sans-serif`
- **Line Height**: `1.5`
- **Font Weights**: `400` (normal), `500` (medium), `600` (semibold), `700` (bold)
- **Font Sizes**:
  - `text-xs`: 12px
  - `text-sm`: 14px
  - `text-base`: 16px
  - `text-lg`: 18px
  - `text-xl`: 20px
  - `text-2xl`: 24px

### 8.4 Spacing System
- **Base unit**: 4px
- **Common values**:
  - `p-2`: 8px
  - `p-3`: 12px
  - `p-4`: 16px
  - `p-6`: 24px
  - `p-8`: 32px
  - `m-2`: 8px
  - `m-4`: 16px
  - `gap-1`: 4px
  - `gap-2`: 8px
  - `gap-3`: 12px
  - `gap-4`: 16px

### 8.5 Border Radius
- `rounded`: 4px
- `rounded-lg`: 8px
- `rounded-full`: Full circle/rounded

### 8.6 Common Button Styles
```tsx
// Primary (Blue)
className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"

// Secondary (Gray)
className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"

// Danger (Red)
className="p-2 bg-red-600/30 hover:bg-red-600/50 rounded text-red-400"

// Icon Only
className="p-2 bg-gray-700 hover:bg-gray-600 rounded"

// Disabled
className="disabled:opacity-50 disabled:cursor-not-allowed"
```

### 8.7 Common Input Styles
```tsx
// Text Input / Select
className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"

// Checkbox
className="w-5 h-5 rounded"

// Radio
className="w-4 h-4"
```

### 8.8 Animations
- **Spin**: `animate-spin` - CSS keyframe rotation
- **Transitions**: `transition-colors`, `transition-all`
- **Hover Scale**: `hover:scale-[1.02]`

---

## 9. ROUTING STRUCTURE

```tsx
<Routes>
  <Route path="/" element={<Navigate to="/chat" replace />} />
  <Route path="/chat" element={<ChatPage />} />
  <Route path="/documents" element={<DocumentsPage />} />
  <Route path="/graph" element={<GraphPage />} />
  <Route path="/ollama-params" element={<OllamaParamsPage />} />
  <Route path="/settings" element={<SettingsPage />} />
</Routes>
```

- Default route `/` redirects to `/chat`
- 5 main pages with corresponding nav items

---

## 10. TECHNOLOGY STACK

- **Framework**: React 18.2.0 + TypeScript 5.2.2
- **Routing**: React Router DOM 6.20.0
- **Styling**: Tailwind CSS 3.3.5
- **Icons**: Lucide React 0.294.0
- **Markdown**: React Markdown 9.0.1
- **Graph**: Force Graph 1.51.2
- **Build**: Vite 5.0.0

---

## 11. ASSETS

### 11.1 Generated Files (in `/dist`)
- `index.html` - Entry point
- `assets/index-*.css` - Minified Tailwind styles (~14.84 KB)
- `assets/index-*.js` - Bundled React app (~513 KB)

### 11.2 API Files (in `src/api/`)
- `index.ts` - API functions for all backend calls

---

*Generated from BitRAG frontend source code analysis*