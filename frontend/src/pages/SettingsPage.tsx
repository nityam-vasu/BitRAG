import { useState, useEffect } from 'react'
import { Save, RefreshCw, CheckCircle, XCircle, ChevronDown, ChevronUp, Cpu, Monitor, HardDrive, CircuitBoard } from 'lucide-react'
import { getSettings, updateSettings, getModels, getSystemInfo, Settings } from '../api'

interface ExtendedSettings extends Settings {
  summary_model?: string;
  tag_model?: string;
}

interface SystemInfo {
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

export default function SettingsPage() {
  const [settings, setSettings] = useState<ExtendedSettings | null>(null)
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [systemInfoExpanded, setSystemInfoExpanded] = useState(false)

  // Form state
  const [model, setModel] = useState('')
  const [summaryModel, setSummaryModel] = useState('')
  const [tagModel, setTagModel] = useState('')
  const [ollamaPort, setOllamaPort] = useState(11434)
  const [hybridMode, setHybridMode] = useState(false)
  const [dualMode, setDualMode] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [settingsData, modelsData, sysInfo] = await Promise.all([
          getSettings(),
          getModels(),
          getSystemInfo(),
        ])
        const extSettings = settingsData as ExtendedSettings
        setSettings(extSettings)
        setSystemInfo(sysInfo as SystemInfo)
        setAvailableModels(modelsData)
        setModel(extSettings.model)
        setSummaryModel(extSettings.summary_model || extSettings.model)
        setTagModel(extSettings.tag_model || extSettings.model)
        setOllamaPort(extSettings.ollamaPort)
        setHybridMode(extSettings.hybridMode)
        setDualMode(extSettings.dualMode)
      } catch (err) {
        console.error('Failed to load settings:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      await updateSettings({
        model,
        summary_model: summaryModel,
        tag_model: tagModel,
        ollamaPort,
        hybridMode,
        dualMode,
      })
      setMessage({ type: 'success', text: 'Settings saved successfully' })
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  const handleRefreshModels = async () => {
    try {
      const models = await getModels()
      setAvailableModels(models)
      setMessage({ type: 'success', text: 'Models refreshed' })
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to refresh models' })
    }
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <RefreshCw className="animate-spin text-blue-500" size={32} />
      </div>
    )
  }

  // Get OS info from browser
  const getOS = () => {
    const ua = navigator.userAgent;
    if (ua.includes('Windows')) return 'Windows';
    if (ua.includes('Mac OS')) return 'macOS';
    if (ua.includes('Linux')) return 'Linux';
    if (ua.includes('Android')) return 'Android';
    if (ua.includes('iOS')) return 'iOS';
    return 'Unknown';
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-2xl mx-auto p-8">
        <h2 className="text-2xl font-semibold mb-6">Settings</h2>

        {message && (
          <div
            className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
              message.type === 'success' ? 'bg-green-600/20 text-green-300' : 'bg-red-600/20 text-red-300'
            }`}
          >
            {message.type === 'success' ? <CheckCircle size={20} /> : <XCircle size={20} />}
            {message.text}
          </div>
        )}

        <div className="space-y-6">
          {/* System Information Box - Collapsible */}
          <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
            <button
              onClick={() => setSystemInfoExpanded(!systemInfoExpanded)}
              className="w-full p-4 flex items-center justify-between hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <CircuitBoard className="text-blue-400" size={20} />
                <span className="font-semibold">System Information</span>
                <span className="text-xs text-gray-500">(Click to {systemInfoExpanded ? 'collapse' : 'expand'})</span>
              </div>
              {systemInfoExpanded ? (
                <ChevronUp size={20} className="text-gray-400" />
              ) : (
                <ChevronDown size={20} className="text-gray-400" />
              )}
            </button>

            {systemInfoExpanded && (
              <div className="px-4 pb-4 border-t border-gray-700">
                <div className="grid grid-cols-2 gap-4 mt-4">
                  {/* CPU */}
                  <div className="bg-gray-700/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 mb-1">
                      <Cpu size={16} />
                      <span className="text-xs uppercase">CPU</span>
                    </div>
                    <p className="font-medium">{systemInfo?.cpu?.toFixed(1) || 'N/A'}%</p>
                    <p className="text-xs text-gray-500">
                      {navigator.hardwareConcurrency || 'N/A'} cores available
                    </p>
                  </div>

                  {/* Operating System */}
                  <div className="bg-gray-700/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 mb-1">
                      <Monitor size={16} />
                      <span className="text-xs uppercase">Operating System</span>
                    </div>
                    <p className="font-medium">{getOS()}</p>
                    <p className="text-xs text-gray-500">
                      {window.innerWidth}x{window.innerHeight} viewport
                    </p>
                  </div>

                  {/* RAM */}
                  <div className="bg-gray-700/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 mb-1">
                      <HardDrive size={16} />
                      <span className="text-xs uppercase">RAM</span>
                    </div>
                    <p className="font-medium">
                      {systemInfo?.memory 
                        ? `${systemInfo.memory.used.toFixed(1)} / ${systemInfo.memory.total.toFixed(1)} GB`
                        : 'N/A'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {systemInfo?.memory?.percent?.toFixed(1) || 'N/A'}% used
                    </p>
                  </div>

                  {/* GPU */}
                  <div className="bg-gray-700/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 mb-1">
                      <CircuitBoard size={16} />
                      <span className="text-xs uppercase">GPU</span>
                    </div>
                    {systemInfo?.gpu && systemInfo.gpu.memory_total > 0 ? (
                      <>
                        <p className="font-medium text-green-400">Available</p>
                        <p className="text-xs text-gray-500">
                          {systemInfo.gpu.memory_used.toFixed(1)} / {systemInfo.gpu.memory_total.toFixed(1)} GB VRAM
                        </p>
                        <p className="text-xs text-gray-500">
                          Utilization: {systemInfo.gpu.utilization.toFixed(1)}%
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="font-medium text-yellow-400">Not Available</p>
                        <p className="text-xs text-gray-500">No GPU detected</p>
                      </>
                    )}
                  </div>
                </div>

                {/* Software Versions */}
                <div className="mt-4 bg-gray-700/50 rounded-lg p-3">
                  <h4 className="text-xs uppercase text-gray-400 mb-3">Software & Configuration</h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Flask</span>
                      <span className="font-mono text-blue-400">Latest</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Ollama</span>
                      <span className={`font-mono ${settings?.ollamaStatus === 'running' ? 'text-green-400' : 'text-red-400'}`}>
                        {settings?.ollamaStatus === 'running' ? 'Connected' : 'Disconnected'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">ChromaDB</span>
                      <span className="font-mono text-blue-400">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">LlamaIndex</span>
                      <span className="font-mono text-blue-400">Integrated</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Embedding Model</span>
                      <span className="font-mono text-xs text-blue-400 truncate max-w-[120px]" title={systemInfo?.embeddingModel || ''}>
                        {systemInfo?.embeddingModel?.split('/').pop() || 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current Chat Model</span>
                      <span className="font-mono text-xs text-blue-400 truncate max-w-[120px]" title={settings?.model || ''}>
                        {settings?.model || 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Documents Indexed</span>
                      <span className="font-mono text-green-400">{systemInfo?.documentCount || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Chunk Size</span>
                      <span className="font-mono text-gray-300">{systemInfo?.chunkSize || 512}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Top-K Retrieval</span>
                      <span className="font-mono text-gray-300">{systemInfo?.topK || 3}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Ollama Models</span>
                      <span className="font-mono text-gray-300">
                        {systemInfo?.ollamaModels?.length || 0} available
                      </span>
                    </div>
                  </div>
                  
                  {/* Available Ollama Models List */}
                  {systemInfo?.ollamaModels && systemInfo.ollamaModels.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-600">
                      <p className="text-xs text-gray-400 mb-2">Available Models:</p>
                      <div className="flex flex-wrap gap-2">
                        {systemInfo.ollamaModels.map((modelName, idx) => (
                          <span 
                            key={idx} 
                            className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-xs font-mono"
                          >
                            {modelName}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Ollama Status */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold mb-2">Ollama Status</h3>
            <div className="flex items-center gap-2">
              <span
                className={`w-3 h-3 rounded-full ${
                  settings?.ollamaStatus === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="capitalize">{settings?.ollamaStatus || 'Unknown'}</span>
            </div>
            <p className="text-sm text-gray-400 mt-2">
              {settings?.documentCount || 0} documents indexed
            </p>
          </div>

          {/* Model Selection */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Chat Model</h3>
              <button
                onClick={handleRefreshModels}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <RefreshCw size={14} />
                Refresh
              </button>
            </div>
            <select
              value={model}
              onChange={e => setModel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            >
              {availableModels.length > 0 ? (
                availableModels.map(m => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))
              ) : (
                <option value={model}>{model} (not available)</option>
              )}
            </select>
          </div>

          {/* Summary Model */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold mb-2">Summary Model</h3>
            <p className="text-sm text-gray-400 mb-3">Model used to generate document summaries for the graph</p>
            <select
              value={summaryModel}
              onChange={e => setSummaryModel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            >
              {availableModels.length > 0 ? (
                availableModels.map(m => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))
              ) : (
                <option value={summaryModel}>{summaryModel} (not available)</option>
              )}
            </select>
          </div>

          {/* Tag Model */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold mb-2">Tag Model</h3>
            <p className="text-sm text-gray-400 mb-3">Model used to extract tags from documents</p>
            <select
              value={tagModel}
              onChange={e => setTagModel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            >
              {availableModels.length > 0 ? (
                availableModels.map(m => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))
              ) : (
                <option value={tagModel}>{tagModel} (not available)</option>
              )}
            </select>
          </div>

          {/* Ollama Port */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold mb-2">Ollama Port</h3>
            <input
              type="number"
              value={ollamaPort}
              onChange={e => setOllamaPort(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Hybrid Mode */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <h3 className="font-semibold">Hybrid Search</h3>
                <p className="text-sm text-gray-400">Combine vector and keyword search</p>
              </div>
              <input
                type="checkbox"
                checked={hybridMode}
                onChange={e => setHybridMode(e.target.checked)}
                className="w-5 h-5 rounded"
              />
            </label>
          </div>

          {/* Dual Mode */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <h3 className="font-semibold">Dual Model Mode</h3>
                <p className="text-sm text-gray-400">Use two models for different tasks</p>
              </div>
              <input
                type="checkbox"
                checked={dualMode}
                onChange={e => setDualMode(e.target.checked)}
                className="w-5 h-5 rounded"
              />
            </label>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {saving ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}
