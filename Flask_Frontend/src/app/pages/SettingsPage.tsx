import { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { Link } from 'react-router';
import { Download, Trash2, FileText, Save } from 'lucide-react';
import { ModelDownloadModal } from '../components/ModelDownloadModal';
import { ModelDeleteModal } from '../components/ModelDeleteModal';

export function SettingsPage() {
  const [ollamaPort, setOllamaPort] = useState('11434');
  const [selectedModel, setSelectedModel] = useState('llama3.2');
  const [dualMode, setDualMode] = useState(false);
  const [model1, setModel1] = useState('llama3.2');
  const [model2, setModel2] = useState('mistral');
  const [hybridValue, setHybridValue] = useState(0);
  const [downloadModalOpen, setDownloadModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [availableModels, setAvailableModels] = useState(['llama3.2']);
  const [saving, setSaving] = useState(false);

  // Load settings on mount
  useEffect(() => {
    loadSettings();
    loadModels();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      if (data.model) setSelectedModel(data.model);
      if (data.ollamaPort) setOllamaPort(data.ollamaPort);
      if (data.hybridMode !== undefined) setHybridValue(data.hybridMode);
      if (data.dualMode !== undefined) setDualMode(data.dualMode);
      if (data.model1) setModel1(data.model1);
      if (data.model2) setModel2(data.model2);
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const loadModels = async () => {
    try {
      const response = await fetch('/api/models');
      const data = await response.json();
      if (data.models && data.models.length > 0) {
        setAvailableModels(data.models);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          ollamaPort: ollamaPort,
          hybridMode: hybridValue,
          dualMode: dualMode,
          model1: model1,
          model2: model2,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const getHybridLabel = () => {
    if (hybridValue === -1) return 'Vector Search';
    if (hybridValue === 0) return 'Hybrid Search';
    return 'Keyword Search';
  };

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-mono text-gray-900 dark:text-gray-100">Settings</h1>
            <button
              onClick={saveSettings}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Ollama Configuration */}
            <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-4">
              <h2 className="text-base font-mono text-gray-900 dark:text-gray-100 mb-3">Ollama Configuration</h2>
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1.5 font-mono">
                  Ollama Port
                </label>
                <input
                  type="text"
                  value={ollamaPort}
                  onChange={(e) => setOllamaPort(e.target.value)}
                  className="w-full bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700"
                  placeholder="11434"
                />
              </div>
            </div>

            {/* Model Selection */}
            <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-4">
              <h2 className="text-base font-mono text-gray-900 dark:text-gray-100 mb-3">Model Selection</h2>
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1.5 font-mono">
                  Active Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700 mb-3"
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setDownloadModalOpen(true)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors text-xs"
                >
                  <Download className="w-3 h-3" />
                  Download
                </button>
                <button
                  onClick={() => setDeleteModalOpen(true)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors text-xs"
                >
                  <Trash2 className="w-3 h-3" />
                  Delete
                </button>
              </div>
            </div>

            {/* Hybrid Retrieval Slider */}
            <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-4">
              <h2 className="text-base font-mono text-gray-900 dark:text-gray-100 mb-3">Hybrid Retrieval</h2>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">Vector</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">Hybrid</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">Keyword</span>
                </div>
                <input
                  type="range"
                  min="-1"
                  max="1"
                  step="1"
                  value={hybridValue}
                  onChange={(e) => setHybridValue(parseInt(e.target.value))}
                  className="w-full accent-gray-600 dark:accent-gray-400"
                />
                <p className="text-center text-sm text-gray-900 dark:text-gray-100 mt-2 font-mono">
                  {getHybridLabel()}
                </p>
              </div>
            </div>

            {/* Dual Model Mode - Spans 2 columns */}
            <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-4 lg:col-span-2">
              <h2 className="text-base font-mono text-gray-900 dark:text-gray-100 mb-3">Dual Model Mode</h2>
              <div className="flex items-center gap-3 mb-3">
                <button
                  onClick={() => setDualMode(!dualMode)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    dualMode ? 'bg-gray-600 dark:bg-gray-600' : 'bg-gray-300 dark:bg-gray-800'
                  }`}
                >
                  <div
                    className={`absolute top-1 left-1 w-4 h-4 bg-white dark:bg-gray-100 rounded-full transition-transform ${
                      dualMode ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                  {dualMode ? 'Enabled' : 'Disabled'}
                </span>
              </div>

              {dualMode && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1.5 font-mono">
                      Model 1
                    </label>
                    <select
                      value={model1}
                      onChange={(e) => setModel1(e.target.value)}
                      className="w-full bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700"
                    >
                      {availableModels.map((model) => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1.5 font-mono">
                      Model 2
                    </label>
                    <select
                      value={model2}
                      onChange={(e) => setModel2(e.target.value)}
                      className="w-full bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700"
                    >
                      {availableModels.map((model) => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="md:col-span-2 bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-800/50 rounded-lg px-3 py-2">
                    <p className="text-xs text-yellow-800 dark:text-yellow-200 font-mono">
                      ⚠ Using two models increases inference time and resource usage.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Document Management Link */}
            <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-4">
              <h2 className="text-base font-mono text-gray-900 dark:text-gray-100 mb-3">Documents</h2>
              <Link
                to="/documents"
                className="flex items-center justify-center gap-2 px-3 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors text-sm"
              >
                <FileText className="w-4 h-4" />
                Manage Documents
              </Link>
            </div>
          </div>
        </div>
      </div>

      <ModelDownloadModal
        isOpen={downloadModalOpen}
        onClose={() => setDownloadModalOpen(false)}
        onModelDownloaded={loadModels}
      />

      <ModelDeleteModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onModelDeleted={loadModels}
      />
    </Layout>
  );
}
