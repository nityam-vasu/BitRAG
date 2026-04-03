import { useState, useEffect } from "react";
import { RefreshCw, Download, Trash2, FileText, Save, CircuitBoard, ChevronDown, Cpu, Monitor, HardDrive, Check, X as XIcon, Loader2 } from "lucide-react";

interface SystemInfoData {
  cpu: number;
  memory: { used: number; total: number; percent: number };
  gpu?: { utilization: number; memory_used: number; memory_total: number };
  documentCount: number;
  embeddingModel: string;
  chunkSize: number;
  topK: number;
  sessionId: string;
}

export default function SettingsPage() {
  const [ollamaPort, setOllamaPort] = useState("11434");
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [chatModel, setChatModel] = useState("llama3.2:1b");
  const [summaryModel, setSummaryModel] = useState("llama3.2:1b");
  const [tagModel, setTagModel] = useState("llama3.2:1b");
  const [hybridSearch, setHybridSearch] = useState(50);
  const [dualModelMode, setDualModelMode] = useState(false);
  const [dualModel1, setDualModel1] = useState("llama3.2:1b");
  const [dualModel2, setDualModel2] = useState("llama3.2:3b");
  const [systemInfoExpanded, setSystemInfoExpanded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfoData | null>(null);
  
  // New UI settings from config.json
  const [darkMode, setDarkMode] = useState(true);
  const [showSystemInfo, setShowSystemInfo] = useState(true);
  const [autoSaveSessions, setAutoSaveSessions] = useState(true);
  const [maxMessagesMemory, setMaxMessagesMemory] = useState(100);
  const [embeddingModel, setEmbeddingModel] = useState("BAAI/bge-small-en-v1.5");
  const [chunkSize, setChunkSize] = useState(512);
  const [topK, setTopK] = useState(5);
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState("http://localhost:11434");
  const [ollamaStatus, setOllamaStatus] = useState("not responding");

  // Fetch settings and models on mount
  useEffect(() => {
    fetchSettings();
    fetchSystemInfo();
    
    // Poll system info every 5 seconds
    const interval = setInterval(fetchSystemInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemInfo = async () => {
    try {
      const response = await fetch('/api/system/info');
      if (response.ok) {
        const data = await response.json();
        setSystemInfo(data);
      }
    } catch (err) {
      console.error('Failed to fetch system info:', err);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const data = await response.json();
        setChatModel(data.default_model || 'llama3.2:1b');
        setSummaryModel(data.summary_model || 'llama3.2:1b');
        setTagModel(data.tag_model || 'llama3.2:1b');
        setOllamaPort(data.ollama_port || '11434');
        setOllamaBaseUrl(data.ollama_base_url || 'http://localhost:11434');
        setHybridSearch(data.hybrid_search_ratio || 50);
        setDualModelMode(data.dual_mode || false);
        setDualModel1(data.dual_model1 || 'llama3.2:1b');
        setDualModel2(data.dual_model2 || 'llama3.2:3b');
        setOllamaStatus(data.ollamaStatus || 'not responding');
        
        // Load available models from Ollama API
        if (data.available_models && data.available_models.length > 0) {
          setAvailableModels(data.available_models);
          setConnected(true);
        }
        
        // Load new UI settings
        setDarkMode(data.dark_mode ?? true);
        setShowSystemInfo(data.show_system_info ?? true);
        setAutoSaveSessions(data.auto_save_sessions ?? true);
        setMaxMessagesMemory(data.max_messages_memory || 100);
        setEmbeddingModel(data.embedding_model || 'BAAI/bge-small-en-v1.5');
        setChunkSize(data.chunk_size || 512);
        setTopK(data.top_k || 5);
      }
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/models');
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models || []);
        setConnected(true);
      } else {
        setConnected(false);
      }
    } catch (err) {
      console.error('Failed to fetch models:', err);
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    // Validation for dual model mode
    if (dualModelMode && dualModel1 === dualModel2) {
      showMessage('error', 'Model 1 and Model 2 must be different!');
      return;
    }
    
    setSaving(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          default_model: chatModel,
          summary_model: summaryModel,
          tag_model: tagModel,
          ollama_port: ollamaPort,
          ollama_base_url: ollamaBaseUrl,
          embedding_model: embeddingModel,
          top_k: topK,
          hybrid_search_ratio: hybridSearch,
          chunk_size: chunkSize,
          dual_mode: dualModelMode,
          dual_model1: dualModel1,
          dual_model2: dualModel2,
          dark_mode: darkMode,
          show_system_info: showSystemInfo,
          auto_save_sessions: autoSaveSessions,
          max_messages_memory: maxMessagesMemory,
        })
      });
      
      if (response.ok) {
        showMessage('success', 'Settings saved successfully!');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      showMessage('error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  return (
    <div className="h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Settings</h2>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <span className="animate-spin">⟳</span>
                Saving...
              </>
            ) : (
              <>
                <Save size={18} />
                Save Settings
              </>
            )}
          </button>
        </div>

        {/* Message Toast */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success' 
              ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-300' 
              : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300'
          }`}>
            {message.type === 'success' ? <Check size={20} /> : <XIcon size={20} />}
            <span>{message.text}</span>
          </div>
        )}

        <div className="space-y-6">
          {/* System Information (Collapsible) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setSystemInfoExpanded(!systemInfoExpanded)}
              className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <CircuitBoard className="text-blue-500" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">System Information</h3>
              </div>
              <ChevronDown className={`text-gray-400 transition-transform ${systemInfoExpanded ? 'rotate-180' : ''}`} size={20} />
            </button>

            {systemInfoExpanded && systemInfo && (
              <div className="px-6 pb-6 space-y-6">
                {/* Hardware Info Grid */}
                <div className="grid grid-cols-2 gap-4">
                  {/* CPU */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Cpu className="text-blue-500" size={20} />
                      <span className="text-xs uppercase text-gray-500 dark:text-gray-400">CPU</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {systemInfo.cpu}%
                    </p>
                  </div>

                  {/* OS */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Monitor className="text-blue-500" size={20} />
                      <span className="text-xs uppercase text-gray-500 dark:text-gray-400">Documents</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {systemInfo.documentCount}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">indexed</p>
                  </div>

                  {/* RAM */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <HardDrive className="text-blue-500" size={20} />
                      <span className="text-xs uppercase text-gray-500 dark:text-gray-400">RAM</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {systemInfo.memory.used}GB / {systemInfo.memory.total}GB
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{systemInfo.memory.percent}% used</p>
                  </div>

                  {/* GPU */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CircuitBoard className="text-blue-500" size={20} />
                      <span className="text-xs uppercase text-gray-500 dark:text-gray-400">GPU</span>
                    </div>
                    {systemInfo.gpu ? (
                      <>
                        <p className="text-lg font-semibold text-green-600 dark:text-green-400">Available</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          VRAM: {systemInfo.gpu.memory_used}GB / {systemInfo.gpu.memory_total}GB ({systemInfo.gpu.utilization}%)
                        </p>
                      </>
                    ) : (
                      <p className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">Not Available</p>
                    )}
                  </div>
                </div>

                {/* Software Configuration */}
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Software & Configuration</h4>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Flask:</span>
                      <span className="text-green-600 dark:text-green-400">Connected</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Ollama:</span>
                      <span className={connected ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>
                        {connected ? "Running" : "Not Connected"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">ChromaDB:</span>
                      <span className="text-green-600 dark:text-green-400">Connected</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">LlamaIndex:</span>
                      <span className="text-green-600 dark:text-green-400">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Embedding Model:</span>
                      <span className="text-gray-900 dark:text-white truncate ml-2">{systemInfo?.embeddingModel || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Chat Model:</span>
                      <span className="text-gray-900 dark:text-white">{chatModel}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Documents:</span>
                      <span className="text-gray-900 dark:text-white">{systemInfo?.documentCount || 0} indexed</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Chunk Size:</span>
                      <span className="text-gray-900 dark:text-white">{systemInfo?.chunkSize || 512}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Top-K:</span>
                      <span className="text-gray-900 dark:text-white">{systemInfo?.topK || 3}</span>
                    </div>
                  </div>
                  
                  {/* Available Models */}
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Available Ollama Models: {availableModels.length}</p>
                    <div className="flex flex-wrap gap-2">
                      {availableModels.map((model) => (
                        <span key={model} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded">
                          {model}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 2-Column Grid for all settings */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Ollama Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Ollama Status</h3>
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-gray-900 dark:text-white font-medium">
                  {connected ? 'running' : 'stopped'}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">5 documents indexed</p>
            </div>
          </div>

          {/* Settings Grid - 2 columns, 3 rows */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Selection */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Chat Model</h3>
                <button className="text-sm text-blue-500 hover:text-blue-600 flex items-center gap-1">
                  <RefreshCw size={14} />
                  Refresh
                </button>
              </div>

              <select
                value={chatModel}
                onChange={(e) => setChatModel(e.target.value)}
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
              >
                {availableModels.map((model) => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            {/* Summary Model */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Summary Model</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Model used to generate document summaries</p>
              
              <select
                value={summaryModel}
                onChange={(e) => setSummaryModel(e.target.value)}
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
              >
                {availableModels.map((model) => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            {/* Tag Model */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Tag Model</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Model used to extract tags from documents</p>
              
              <select
                value={tagModel}
                onChange={(e) => setTagModel(e.target.value)}
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
              >
                {availableModels.map((model) => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            {/* Ollama Port */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Ollama Port</h3>
              
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={ollamaPort}
                  onChange={(e) => setOllamaPort(e.target.value)}
                  className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                />
                <button className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white transition-colors">
                  <RefreshCw size={20} />
                </button>
              </div>
            </div>

            {/* Hybrid Search */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Hybrid Search</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Combine vector and keyword search</p>
                </div>
                <div className="relative inline-block w-12 h-6">
                  <input
                    type="checkbox"
                    checked={hybridSearch > 0}
                    onChange={(e) => setHybridSearch(e.target.checked ? 50 : 0)}
                    className="sr-only peer"
                  />
                  <div className="w-12 h-6 bg-gray-300 dark:bg-gray-600 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
                </div>
              </div>
            </div>

            {/* Dual Model Mode */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Dual Model Mode</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Use two models for different tasks</p>
                </div>
                <div className="relative inline-block w-12 h-6">
                  <input
                    type="checkbox"
                    checked={dualModelMode}
                    onChange={(e) => setDualModelMode(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-12 h-6 bg-gray-300 dark:bg-gray-600 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
                </div>
              </div>
            </div>

            {/* Dual Model 1 - Only show if dual mode is enabled */}
            {dualModelMode && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Model 1</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">First model for dual mode</p>
                
                <select
                  value={dualModel1}
                  onChange={(e) => {
                    setDualModel1(e.target.value);
                    // If same as model 2, show warning
                    if (e.target.value === dualModel2) {
                      showMessage('error', 'Model 1 and Model 2 cannot be the same!');
                    }
                  }}
                  className={`w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border ${
                    dualModel1 === dualModel2 
                      ? 'border-red-500 dark:border-red-500' 
                      : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white`}
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
                {dualModel1 === dualModel2 && (
                  <p className="mt-2 text-xs text-red-600 dark:text-red-400">⚠️ Models must be different</p>
                )}
              </div>
            )}

            {/* Dual Model 2 - Only show if dual mode is enabled */}
            {dualModelMode && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Model 2</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Second model for dual mode</p>
                
                <select
                  value={dualModel2}
                  onChange={(e) => {
                    setDualModel2(e.target.value);
                    // If same as model 1, show warning
                    if (e.target.value === dualModel1) {
                      showMessage('error', 'Model 1 and Model 2 cannot be the same!');
                    }
                  }}
                  className={`w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border ${
                    dualModel1 === dualModel2 
                      ? 'border-red-500 dark:border-red-500' 
                      : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white`}
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
                {dualModel1 === dualModel2 && (
                  <p className="mt-2 text-xs text-red-600 dark:text-red-400">⚠️ Models must be different</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}