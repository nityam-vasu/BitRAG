# BitRAG Web GUI Frontend

React + TypeScript + Tailwind CSS frontend for BitRAG.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── pages/        # ChatPage, SettingsPage, DocumentsPage
│   │   ├── components/   # UI components
│   │   └── routes.tsx    # React Router config
│   ├── main.tsx          # App entry
│   └── styles/           # Global styles
├── package.json
├── vite.config.ts
└── postcss.config.mjs
```

## Building for Production

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Copy to backend:
   ```bash
   cp -r dist/* ../backend/static/
   ```

## Environment Variables

No environment variables needed for development.
