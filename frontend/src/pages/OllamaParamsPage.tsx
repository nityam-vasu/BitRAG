import { useState, useEffect } from 'react'
import { Save, RefreshCw, CheckCircle, XCircle, Cpu, Zap, Server, Laptop, Activity, Info, Trash2, Plus, Edit2, Check } from 'lucide-react'
import { getSystemInfo } from '../api'

interface OllamaParams {
  threads: number;
  batch: number;
  ctx: number;
  mmap: number; // 0 = disabled, 1 = enabled
  numa: boolean;
  gpu: number; // GPU layers (0 = CPU only)
}

interface OllamaPreset {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  hardware: string;
  params: OllamaParams;
}

interface SavedConfig {
  id: string;
  name: string;
  params: OllamaParams;
  createdAt: string;
}

// Default preset configurations
const PRESETS: OllamaPreset[] = [
  {
    id: 'office-laptop',
    name: 'Office Laptop',
    description: 'Optimized for light workloads, leaves resources for other tasks',
    icon: <Laptop size={20} />,
    hardware: 'Core i5 (4 cores), 16GB RAM',
    params: {
      threads: 2,
      batch: 64,
      ctx: 4096,
      mmap: 1,
      numa: false,
      gpu: 0,
    },
  },
  {
    id: 'home-server',
    name: 'Home Server',
    description: 'Balanced performance for multi-user household',
    icon: <Server size={20} />,
    hardware: 'Ryzen 9 (16 cores), 64GB RAM',
    params: {
      threads: 12,
      batch: 256,
      ctx: 8192,
      mmap: 0,
      numa: false,
      gpu: 0,
    },
  },
  {
    id: 'headless-server',
    name: 'Headless Server',
    description: 'Maximum performance for production workloads',
    icon: <Zap size={20} />,
    hardware: 'Dual Xeon (48 cores), 256GB RAM',
    params: {
      threads: 40,
      batch: 512,
      ctx: 32768,
      mmap: 0,
      numa: true,
      gpu: 0,
    },
  },
]

// Local storage keys
const STORAGE_KEY = 'bitrag_ollama_params';
const SAVED_CONFIGS_KEY = 'bitrag_saved_configs';
const ACTIVE_CONFIG_KEY = 'bitrag_active_config';

export default function OllamaParamsPage() {
  const [currentParams, setCurrentParams] = useState<OllamaParams>({
    threads: 4,
    batch: 512,
    ctx: 4096,
    mmap: 1,
    numa: false,
    gpu: 0,
  })
  const [savedConfigs, setSavedConfigs] = useState<SavedConfig[]>([])
  const [activeConfigId, setActiveConfigId] = useState<string | null>(null)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editingName, setEditingName] = useState('')
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [newConfigName, setNewConfigName] = useState('')
  const [systemInfo, setSystemInfo] = useState<{ cpu: number; memory?: { total: number } } | null>(null)

  // Load saved configs and active config on mount
  useEffect(() => {
    const loadData = () => {
      // Load saved configs
      const saved = localStorage.getItem(SAVED_CONFIGS_KEY)
      if (saved) {
        try {
          setSavedConfigs(JSON.parse(saved))
        } catch {
          setSavedConfigs([])
        }
      }

      // Load active config
      const active = localStorage.getItem(ACTIVE_CONFIG_KEY)
      if (active) {
        try {
          const config = JSON.parse(active)
          setCurrentParams(config.params)
          setActiveConfigId(config.id)
        } catch {
          // Ignore
        }
      } else {
        // Load legacy params if no config saved
        const params = localStorage.getItem(STORAGE_KEY)
        if (params) {
          try {
            setCurrentParams(JSON.parse(params))
          } catch {
            // Use defaults
          }
        }
      }
    }

    loadData()

    // Load system info
    getSystemInfo().then(info => {
      setSystemInfo(info)
    }).catch(() => {
      // Use browser info as fallback
      setSystemInfo({
        cpu: navigator.hardwareConcurrency || 4,
        memory: { total: 16 }
      })
    })
  }, [])

  // Save current params
  const handleSaveParams = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentParams))
    setMessage({ type: 'success', text: 'Parameters saved successfully!' })
    setTimeout(() => setMessage(null), 3000)
  }

  // Apply preset
  const handleApplyPreset = (preset: OllamaPreset) => {
    setCurrentParams(preset.params)
    setActiveConfigId(preset.id)
    localStorage.setItem(ACTIVE_CONFIG_KEY, JSON.stringify({
      id: preset.id,
      name: preset.name,
      params: preset.params,
    }))
    setMessage({ type: 'success', text: `Applied "${preset.name}" preset!` })
    setTimeout(() => setMessage(null), 3000)
  }

  // Save custom config
  const handleSaveConfig = () => {
    if (!newConfigName.trim()) {
      setMessage({ type: 'error', text: 'Please enter a configuration name' })
      return
    }

    const newConfig: SavedConfig = {
      id: `custom-${Date.now()}`,
      name: newConfigName.trim(),
      params: { ...currentParams },
      createdAt: new Date().toISOString(),
    }

    const updated = [...savedConfigs, newConfig]
    setSavedConfigs(updated)
    localStorage.setItem(SAVED_CONFIGS_KEY, JSON.stringify(updated))
    localStorage.setItem(ACTIVE_CONFIG_KEY, JSON.stringify({
      id: newConfig.id,
      name: newConfig.name,
      params: newConfig.params,
    }))
    setActiveConfigId(newConfig.id)
    setNewConfigName('')
    setShowSaveModal(false)
    setMessage({ type: 'success', text: `Saved configuration "${newConfig.name}"!` })
    setTimeout(() => setMessage(null), 3000)
  }

  // Load custom config
  const handleLoadConfig = (config: SavedConfig) => {
    setCurrentParams(config.params)
    setActiveConfigId(config.id)
    localStorage.setItem(ACTIVE_CONFIG_KEY, JSON.stringify({
      id: config.id,
      name: config.name,
      params: config.params,
    }))
    setMessage({ type: 'success', text: `Loaded "${config.name}"` })
    setTimeout(() => setMessage(null), 3000)
  }

  // Delete custom config
  const handleDeleteConfig = (configId: string) => {
    const updated = savedConfigs.filter(c => c.id !== configId)
    setSavedConfigs(updated)
    localStorage.setItem(SAVED_CONFIGS_KEY, JSON.stringify(updated))
    if (activeConfigId === configId) {
      setActiveConfigId(null)
      localStorage.removeItem(ACTIVE_CONFIG_KEY)
    }
    setMessage({ type: 'success', text: 'Configuration deleted' })
    setTimeout(() => setMessage(null), 3000)
  }

  // Update parameter
  const updateParam = (key: keyof OllamaParams, value: number | boolean) => {
    setCurrentParams(prev => ({ ...prev, [key]: value }))
    setActiveConfigId(null) // Mark as custom when editing
  }

  // Auto-calculate threads based on CPU cores
  const getRecommendedThreads = () => {
    const cores = systemInfo?.cpu || navigator.hardwareConcurrency || 4
    if (cores <= 4) return Math.max(2, cores - 2)
    if (cores <= 8) return Math.max(4, cores - 4)
    if (cores <= 16) return Math.max(8, cores - 4)
    return Math.max(16, cores - 8)
  }

  // Generate command preview
  const generateCommand = () => {
    const parts = ['ollama run <model>']
    if (currentParams.threads > 0) parts.push(`--threads ${currentParams.threads}`)
    if (currentParams.batch > 0) parts.push(`--batch ${currentParams.batch}`)
    if (currentParams.ctx > 0) parts.push(`--ctx ${currentParams.ctx}`)
    if (currentParams.mmap === 0) parts.push('--mmap 0')
    if (currentParams.numa) parts.push('--numa')
    if (currentParams.gpu > 0) parts.push(`--gpu ${currentParams.gpu}`)
    return parts.join(' ')
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto p-8">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-blue-400" size={28} />
          <div>
            <h2 className="text-2xl font-semibold">Custom Ollama Parameters</h2>
            <p className="text-sm text-gray-400">Optimize model performance for your hardware</p>
          </div>
        </div>

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

        {/* System Info Banner */}
        <div className="mb-6 p-4 bg-blue-600/20 border border-blue-600/30 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Info size={18} className="text-blue-400" />
            <span className="font-semibold text-blue-300">Your System</span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">CPU Cores:</span>
              <span className="ml-2 font-mono text-white">{systemInfo?.cpu || navigator.hardwareConcurrency || 'N/A'}</span>
            </div>
            <div>
              <span className="text-gray-400">Recommended Threads:</span>
              <span className="ml-2 font-mono text-green-400">{getRecommendedThreads()}</span>
            </div>
          </div>
        </div>

        {/* Preset Configurations */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap size={18} className="text-yellow-400" />
            Quick Presets
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {PRESETS.map(preset => (
              <button
                key={preset.id}
                onClick={() => handleApplyPreset(preset)}
                className={`p-4 rounded-lg border text-left transition-all hover:scale-[1.02] ${
                  activeConfigId === preset.id
                    ? 'bg-blue-600/30 border-blue-500'
                    : 'bg-gray-800 border-gray-700 hover:border-gray-600'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-blue-400">{preset.icon}</span>
                  <span className="font-semibold">{preset.name}</span>
                  {activeConfigId === preset.id && (
                    <Check size={16} className="ml-auto text-green-400" />
                  )}
                </div>
                <p className="text-xs text-gray-400 mb-2">{preset.hardware}</p>
                <p className="text-sm text-gray-300">{preset.description}</p>
                <div className="mt-3 text-xs text-gray-500 font-mono">
                  threads={preset.params.threads} | batch={preset.params.batch} | ctx={preset.params.ctx}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Configuration */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Cpu size={18} className="text-purple-400" />
              Custom Configuration
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => setShowSaveModal(true)}
                className="px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm flex items-center gap-1"
              >
                <Save size={14} />
                Save Config
              </button>
              <button
                onClick={handleSaveParams}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-1"
              >
                <Check size={14} />
                Apply
              </button>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Threads */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--threads</span>
                  <span className="text-gray-500 ml-2">(CPU Threads)</span>
                </label>
                <input
                  type="number"
                  value={currentParams.threads}
                  onChange={e => updateParam('threads', parseInt(e.target.value) || 0)}
                  min={0}
                  max={64}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Recommended: {getRecommendedThreads()} for your system
                </p>
              </div>

              {/* Batch */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--batch</span>
                  <span className="text-gray-500 ml-2">(Batch Size)</span>
                </label>
                <input
                  type="number"
                  value={currentParams.batch}
                  onChange={e => updateParam('batch', parseInt(e.target.value) || 0)}
                  min={0}
                  max={8192}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Higher = faster but more memory
                </p>
              </div>

              {/* Context */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--ctx</span>
                  <span className="text-gray-500 ml-2">(Context Size)</span>
                </label>
                <input
                  type="number"
                  value={currentParams.ctx}
                  onChange={e => updateParam('ctx', parseInt(e.target.value) || 0)}
                  min={512}
                  max={131072}
                  step={512}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Max tokens in context window
                </p>
              </div>

              {/* GPU Layers */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--gpu</span>
                  <span className="text-gray-500 ml-2">(GPU Layers)</span>
                </label>
                <input
                  type="number"
                  value={currentParams.gpu}
                  onChange={e => updateParam('gpu', parseInt(e.target.value) || 0)}
                  min={0}
                  max={100}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <p className="mt-1 text-xs text-gray-500">
                  0 = CPU only, higher = use GPU
                </p>
              </div>

              {/* Memory Mapping */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--mmap</span>
                  <span className="text-gray-500 ml-2">(Memory Mapping)</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={currentParams.mmap === 1}
                      onChange={() => updateParam('mmap', 1)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Enabled (1)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={currentParams.mmap === 0}
                      onChange={() => updateParam('mmap', 0)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Disabled (0)</span>
                  </label>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  0 = Load in RAM (fast), 1 = Stream from disk (low memory)
                </p>
              </div>

              {/* NUMA */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <span className="text-gray-300">--numa</span>
                  <span className="text-gray-500 ml-2">(NUMA Awareness)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={currentParams.numa}
                    onChange={e => updateParam('numa', e.target.checked)}
                    className="w-5 h-5 rounded"
                  />
                  <span className="text-sm">Enable NUMA optimization</span>
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  For multi-socket servers only
                </p>
              </div>
            </div>

            {/* Command Preview */}
            <div className="mt-6 pt-6 border-t border-gray-700">
              <h4 className="text-sm font-medium mb-2 text-gray-400">Command Preview</h4>
              <code className="block p-3 bg-gray-900 rounded-lg text-sm font-mono text-green-400 overflow-x-auto">
                {generateCommand()}
              </code>
            </div>
          </div>
        </div>

        {/* Saved Configurations */}
        {savedConfigs.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Save size={18} className="text-green-400" />
              Saved Configurations
            </h3>
            <div className="space-y-3">
              {savedConfigs.map(config => (
                <div
                  key={config.id}
                  className={`p-4 rounded-lg border flex items-center justify-between ${
                    activeConfigId === config.id
                      ? 'bg-green-600/20 border-green-600/50'
                      : 'bg-gray-800 border-gray-700'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{config.name}</span>
                      {activeConfigId === config.id && (
                        <span className="px-2 py-0.5 bg-green-600/50 rounded text-xs">Active</span>
                      )}
                    </div>
                    <div className="mt-1 text-xs text-gray-500 font-mono">
                      threads={config.params.threads} | batch={config.params.batch} | ctx={config.params.ctx}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleLoadConfig(config)}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-1"
                    >
                      <Check size={14} />
                      Load
                    </button>
                    <button
                      onClick={() => handleDeleteConfig(config.id)}
                      className="p-1.5 bg-red-600/30 hover:bg-red-600/50 rounded-lg text-red-400"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Save Modal */}
        {showSaveModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
              <h3 className="text-lg font-semibold mb-4">Save Configuration</h3>
              <input
                type="text"
                value={newConfigName}
                onChange={e => setNewConfigName(e.target.value)}
                placeholder="Configuration name..."
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 mb-4"
                autoFocus
                onKeyDown={e => e.key === 'Enter' && handleSaveConfig()}
              />
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveConfig}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-1"
                >
                  <Save size={16} />
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
