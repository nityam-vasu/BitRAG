import { useState, useEffect } from "react";
import { Activity, Laptop, Server, Zap, Cpu, Save, Check, Info, X as XIcon, Loader2 } from "lucide-react";

interface Preset {
  name: string;
  icon: any;
  hardware: string;
  description: string;
  params: {
    threads: number;
    batch: number;
    ctx: number;
    gpu: number;
    mmap: number;
    numa: boolean;
  };
}

interface SavedConfig {
  id: string;
  name: string;
  params: {
    threads: number;
    batch: number;
    ctx: number;
    gpu: number;
    mmap: number;
    numa: boolean;
  };
  isActive: boolean;
}

export default function OllamaParamsPage() {
  const [threads, setThreads] = useState(8);
  const [batch, setBatch] = useState(512);
  const [ctx, setCtx] = useState(4096);
  const [gpu, setGpu] = useState(0);
  const [mmap, setMmap] = useState(1);
  const [numa, setNuma] = useState(false);
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [configName, setConfigName] = useState("");
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [savedConfigs, setSavedConfigs] = useState<SavedConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);

  // Fetch existing params on mount
  useEffect(() => {
    fetchParams();
  }, []);

  const fetchParams = async () => {
    try {
      const response = await fetch('/api/ollama/params');
      if (response.ok) {
        const data = await response.json();
        setThreads(data.threads || 8);
        setBatch(data.batch || 512);
        setCtx(data.ctx || 4096);
        setGpu(data.gpu || 0);
        setMmap(data.mmap || 1);
        setNuma(data.numa || false);
      }
    } catch (err) {
      console.error('Failed to fetch params:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    setApplying(true);
    try {
      const response = await fetch('/api/ollama/params', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threads,
          batch,
          ctx,
          gpu,
          mmap,
          numa,
        })
      });
      
      if (response.ok) {
        showMessage('success', 'Parameters applied successfully!');
      } else {
        throw new Error('Failed to apply parameters');
      }
    } catch (err) {
      showMessage('error', 'Failed to apply parameters');
    } finally {
      setApplying(false);
    }
  };

  const presets: Preset[] = [
    {
      name: "Office Laptop",
      icon: Laptop,
      hardware: "Core i5 (4 cores), 16GB RAM",
      description: "Optimized for light workloads and efficient battery usage",
      params: { threads: 4, batch: 256, ctx: 2048, gpu: 0, mmap: 1, numa: false }
    },
    {
      name: "Home Server",
      icon: Server,
      hardware: "Ryzen 9 (16 cores), 64GB RAM",
      description: "Balanced performance for moderate workloads",
      params: { threads: 8, batch: 512, ctx: 4096, gpu: 0, mmap: 0, numa: false }
    },
    {
      name: "Headless Server",
      icon: Zap,
      hardware: "Dual Xeon (48 cores), 256GB RAM",
      description: "Maximum performance for intensive workloads",
      params: { threads: 32, batch: 2048, ctx: 8192, gpu: 0, mmap: 0, numa: true }
    }
  ];

  const applyPreset = (preset: Preset) => {
    setThreads(preset.params.threads);
    setBatch(preset.params.batch);
    setCtx(preset.params.ctx);
    setGpu(preset.params.gpu);
    setMmap(preset.params.mmap);
    setNuma(preset.params.numa);
    setActivePreset(preset.name);
  };

  const handleSaveConfig = () => {
    if (!configName.trim()) return;
    
    const newConfig: SavedConfig = {
      id: Date.now().toString(),
      name: configName,
      params: { threads, batch, ctx, gpu, mmap, numa },
      isActive: false
    };
    
    setSavedConfigs([...savedConfigs, newConfig]);
    setConfigName("");
    setShowSaveModal(false);
    showMessage('success', 'Configuration saved successfully!');
  };

  const loadConfig = (config: SavedConfig) => {
    setThreads(config.params.threads);
    setBatch(config.params.batch);
    setCtx(config.params.ctx);
    setGpu(config.params.gpu);
    setMmap(config.params.mmap);
    setNuma(config.params.numa);
    setActivePreset(null);
    
    setSavedConfigs(savedConfigs.map(c => ({ ...c, isActive: c.id === config.id })));
  };

  const deleteConfig = (id: string) => {
    setSavedConfigs(savedConfigs.filter(c => c.id !== id));
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const generateCommand = () => {
    return `ollama run <model> --threads ${threads} --batch ${batch} --ctx ${ctx} --gpu ${gpu} --mmap ${mmap}${numa ? ' --numa' : ''}`;
  };

  return (
    <div className="h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="text-blue-500" size={32} />
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">Custom Ollama Parameters</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Optimize model performance for your hardware</p>
        </div>

        {/* System Info Banner */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Info className="text-blue-600 dark:text-blue-400" size={20} />
            <h3 className="font-semibold text-gray-900 dark:text-white">Your System</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">CPU Cores:</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{cpuCores}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Recommended Threads:</p>
              <p className="text-lg font-semibold text-green-600 dark:text-green-400">{recommendedThreads}</p>
            </div>
          </div>
        </div>

        {/* Message */}
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

        {/* Quick Presets */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="text-blue-500" size={20} />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Presets</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {presets.map((preset) => {
              const Icon = preset.icon;
              const isActive = activePreset === preset.name;
              
              return (
                <button
                  key={preset.name}
                  onClick={() => applyPreset(preset)}
                  className={`text-left p-6 rounded-lg border-2 transition-all ${
                    isActive
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <Icon className={isActive ? 'text-blue-500' : 'text-gray-600 dark:text-gray-400'} size={28} />
                    {isActive && <Check className="text-green-500" size={20} />}
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{preset.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{preset.hardware}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mb-3">{preset.description}</p>
                  <div className="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <span>threads: {preset.params.threads}</span>
                    <span>•</span>
                    <span>batch: {preset.params.batch}</span>
                    <span>•</span>
                    <span>ctx: {preset.params.ctx}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Configuration */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Cpu className="text-blue-500" size={20} />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Custom Configuration</h2>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowSaveModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                <Save size={18} />
                Save Config
              </button>
              <button
                onClick={handleApply}
                disabled={applying}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {applying ? <Loader2 className="animate-spin" size={18} /> : null}
                Apply
              </button>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Threads */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--threads</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(CPU Threads)</span>
                </label>
                <input
                  type="number"
                  value={threads}
                  onChange={(e) => setThreads(parseInt(e.target.value) || 0)}
                  min="0"
                  max="64"
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Recommended: {recommendedThreads} for your system
                </p>
              </div>

              {/* Batch */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--batch</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(Batch Size)</span>
                </label>
                <input
                  type="number"
                  value={batch}
                  onChange={(e) => setBatch(parseInt(e.target.value) || 0)}
                  min="0"
                  max="8192"
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Higher = faster but more memory
                </p>
              </div>

              {/* Context */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--ctx</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(Context Size)</span>
                </label>
                <input
                  type="number"
                  value={ctx}
                  onChange={(e) => setCtx(parseInt(e.target.value) || 512)}
                  min="512"
                  max="131072"
                  step="512"
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Max tokens in context window
                </p>
              </div>

              {/* GPU */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--gpu</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(GPU Layers)</span>
                </label>
                <input
                  type="number"
                  value={gpu}
                  onChange={(e) => setGpu(parseInt(e.target.value) || 0)}
                  min="0"
                  max="100"
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  0 = CPU only, higher = use GPU
                </p>
              </div>

              {/* Memory Mapping */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--mmap</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(Memory Mapping)</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mmap"
                      checked={mmap === 1}
                      onChange={() => setMmap(1)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-900 dark:text-white">Enabled (1)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mmap"
                      checked={mmap === 0}
                      onChange={() => setMmap(0)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-900 dark:text-white">Disabled (0)</span>
                  </label>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  0 = Load in RAM (fast), 1 = Stream from disk
                </p>
              </div>

              {/* NUMA */}
              <div>
                <label className="block mb-2">
                  <span className="text-white font-medium">--numa</span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(NUMA Awareness)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={numa}
                    onChange={(e) => setNuma(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-gray-900 dark:text-white">Enable NUMA optimization</span>
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  For multi-socket servers only
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Command Preview */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Command Preview</h2>
          <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-4 border border-gray-700">
            <code className="text-green-400 font-mono text-sm break-all">{generateCommand()}</code>
          </div>
        </div>

        {/* Saved Configurations */}
        {savedConfigs.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Saved Configurations</h2>
            <div className="space-y-3">
              {savedConfigs.map((config) => (
                <div
                  key={config.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{config.name}</h3>
                      {config.isActive && (
                        <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      threads: {config.params.threads} • batch: {config.params.batch} • ctx: {config.params.ctx} • gpu: {config.params.gpu}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => loadConfig(config)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      Load
                    </button>
                    <button
                      onClick={() => deleteConfig(config.id)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                    >
                      <XIcon size={20} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Save Config Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-md border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Save Configuration</h3>
              <input
                type="text"
                value={configName}
                onChange={(e) => setConfigName(e.target.value)}
                placeholder="Enter configuration name"
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white"
                autoFocus
              />
            </div>
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex gap-2">
              <button
                onClick={() => setShowSaveModal(false)}
                className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveConfig}
                disabled={!configName.trim()}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
