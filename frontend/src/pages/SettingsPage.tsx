import { useState, useEffect } from 'react'
import { Save, RefreshCw, CheckCircle, XCircle } from 'lucide-react'
import { getSettings, updateSettings, getModels, Settings } from '../api'

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null)
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Form state
  const [model, setModel] = useState('')
  const [ollamaPort, setOllamaPort] = useState(11434)
  const [hybridMode, setHybridMode] = useState(false)
  const [dualMode, setDualMode] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [settingsData, modelsData] = await Promise.all([
          getSettings(),
          getModels(),
        ])
        setSettings(settingsData)
        setAvailableModels(modelsData)
        setModel(settingsData.model)
        setOllamaPort(settingsData.ollamaPort)
        setHybridMode(settingsData.hybridMode)
        setDualMode(settingsData.dualMode)
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
