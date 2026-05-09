# BitRAG Frontend

Modern React-based web interface for BitRAG.

## Features

- 💬 **Chat Interface** - Interactive chat with your PDF documents
- 📄 **Document Management** - Upload, view, and manage indexed documents
- 🔗 **Knowledge Graph** - Visualize document relationships
- ⚙️ **Settings** - Configure Ollama parameters and model selection
- 📊 **System Info** - Monitor CPU, RAM, and GPU usage

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
# Start development server
npm run dev

# Access at http://localhost:5173
```

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Main application components
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components
│   ├── api/           # API client
│   └── styles/        # Global styles
├── public/            # Static assets
├── index.html         # Entry HTML
├── package.json       # Dependencies
├── vite.config.ts     # Vite configuration
└── tailwind.config.js # Tailwind CSS configuration
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **React Query** - Data fetching
- **React Router** - Routing