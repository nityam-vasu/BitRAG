const API_BASE = '';

export interface GraphNode {
  id: string;
  name: string;
  val: number;
  group: number;
  summary: string;
  tags: string[];
  keywords: string[];
}

export interface GraphLink {
  source: string;
  target: string;
  value: number;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  thinking?: string;
  sources?: string[];
}

export interface Settings {
  model: string;
  summary_model?: string;
  tag_model?: string;
  ollamaPort: number;
  hybridMode: boolean;
  dualMode: boolean;
  model1: string;
  model2: string;
  documentCount: number;
  ollamaStatus: string;
}

export interface SystemInfo {
  sessionId: string;
  documentCount: number;
  embeddingModel: string;
  chunkSize: number;
  topK: number;
  cpu: number;
  memory: {
    used: number;
    total: number;
    percent: number;
  };
  gpu?: {
    utilization: number;
    memory_used: number;
    memory_total: number;
  };
  ollamaStatus: string;
  ollamaModels?: string[];
}

// Status API
export async function getStatus(): Promise<{ status: string; initialized: boolean }> {
  const res = await fetch(`${API_BASE}/api/status`);
  return res.json();
}

// System Info API
export async function getSystemInfo(): Promise<SystemInfo> {
  const res = await fetch(`${API_BASE}/api/system/info`);
  return res.json();
}

// Settings API
export async function getSettings(): Promise<Settings> {
  const res = await fetch(`${API_BASE}/api/settings`);
  return res.json();
}

export async function updateSettings(settings: Partial<Settings>): Promise<Settings> {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  return res.json();
}

// Models API
export async function getModels(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/models`);
  const data = await res.json();
  return data.models || [];
}

export async function downloadModel(model: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/models/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model }),
  });
  return res.json();
}

// Documents API
export interface Document {
  id: string;
  name: string;
}

export async function getDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/api/documents`);
  return res.json();
}

export async function uploadDocument(file: File, processForGraph: boolean = false): Promise<{ success: boolean; id: string; name: string; metadata?: { summary: string; tags: string[] }; graph_updated?: boolean }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('process', processForGraph.toString());
  
  const res = await fetch(`${API_BASE}/api/documents`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function deleteDocument(docId: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/api/documents/${encodeURIComponent(docId)}`, {
    method: 'DELETE',
  });
  return res.json();
}

// Graph API
export async function getGraph(refresh = false): Promise<GraphData> {
  const url = refresh ? `${API_BASE}/api/graph?refresh=true` : `${API_BASE}/api/graph`;
  const res = await fetch(url);
  return res.json();
}

export async function regenerateGraph(): Promise<{ success: boolean; message: string; stats: { nodes: number; links: number } }> {
  const res = await fetch(`${API_BASE}/api/graph/regenerate`);
  return res.json();
}

export async function getGraphInfo(): Promise<{ initialized: boolean; cache_size: number }> {
  const res = await fetch(`${API_BASE}/api/graph/info`);
  return res.json();
}

export async function regenerateDocumentTags(docId: string): Promise<{ success: boolean; metadata: { summary: string; tags: string[] } }> {
  const res = await fetch(`${API_BASE}/api/documents/${encodeURIComponent(docId)}/regenerate-tags`, {
    method: 'POST',
  });
  return res.json();
}

// Session Management API
export interface Session {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionData extends Session {
  messages: Array<{
    content: string;
    role: 'user' | 'assistant' | 'system';
    timestamp: string;
    sources?: string[];
  }>;
}

export async function getSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/api/sessions`);
  const data = await res.json();
  return data.sessions || [];
}

export async function getSession(sessionId: string): Promise<SessionData> {
  const res = await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`);
  if (!res.ok) throw new Error('Session not found');
  return res.json();
}

export async function createSession(title?: string): Promise<{ success: boolean; session: Session }> {
  const res = await fetch(`${API_BASE}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function renameSession(sessionId: string, title: string): Promise<{ success: boolean; title: string }> {
  const res = await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
  return res.json();
}

export function getSessionExportUrl(sessionId: string): string {
  return `${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}/export`;
}

export function getCurrentChatExportUrl(): string {
  return `${API_BASE}/api/chat/export`;
}

// Ollama Parameters API
export interface OllamaParams {
  threads: number;
  batch: number;
  ctx: number;
  mmap: number;
  numa: boolean;
  gpu: number;
}

export interface OllamaParamsConfig {
  active: OllamaParams;
  presets: {
    id: string;
    name: string;
    params: OllamaParams;
  }[];
}

export async function getOllamaParams(): Promise<OllamaParamsConfig> {
  const res = await fetch(`${API_BASE}/api/ollama/params`);
  return res.json();
}

export async function updateOllamaParams(params: OllamaParams): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/api/ollama/params`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

// Chat API (non-streaming)
export async function sendChat(query: string): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  const data = await res.json();
  
  if (data.error) {
    throw new Error(data.message || data.error);
  }
  
  return {
    id: data.id,
    type: 'assistant',
    content: data.output,
    thinking: data.thinking,
    sources: data.sources,
  };
}
