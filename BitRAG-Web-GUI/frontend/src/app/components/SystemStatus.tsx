import { useState, useEffect } from 'react';

interface SystemStats {
  cpu: number;
  memory: {
    used: number;
    total: number;
    percent: number;
  };
  gpu: {
    utilization: number;
    memory_used: number;
    memory_total: number;
  };
  ollamaStatus?: string;
  ollamaError?: string;
}

export function SystemStatus() {
  const [stats, setStats] = useState<SystemStats>({
    cpu: 0,
    memory: { used: 0, total: 0, percent: 0 },
    gpu: { utilization: 0, memory_used: 0, memory_total: 0 },
    ollamaStatus: undefined,
    ollamaError: undefined,
  });
  const [loading, setLoading] = useState(true);

  const fetchSystemInfo = async () => {
    try {
      const response = await fetch('/api/system/info');
      const data = await response.json();
      
      // Always update stats if we get a valid response (even if cpu is 0)
      if (data && data.cpu !== undefined && data.memory) {
        setStats({
          cpu: data.cpu,
          memory: data.memory || { used: 0, total: 0, percent: 0 },
          gpu: data.gpu || { utilization: 0, memory_used: 0, memory_total: 0 },
          ollamaStatus: data.ollamaStatus,
          ollamaError: data.ollamaError,
        });
      } else if (data && Object.keys(data).length > 0) {
        // Partial data - update what we have
        setStats(prev => ({
          cpu: data.cpu !== undefined ? data.cpu : prev.cpu,
          memory: data.memory ? { ...prev.memory, ...data.memory } : prev.memory,
          gpu: data.gpu ? { ...prev.gpu, ...data.gpu } : prev.gpu,
          ollamaStatus: data.ollamaStatus || prev.ollamaStatus,
          ollamaError: data.ollamaError || prev.ollamaError,
        }));
      }
    } catch (error) {
      console.error('Error fetching system info:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch immediately
    fetchSystemInfo();
    
    // Poll every 2 seconds for real-time updates
    const interval = setInterval(fetchSystemInfo, 2000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-[#0a0a0a] px-6 py-2">
        <div className="flex items-center gap-6 text-sm font-mono text-gray-500 dark:text-gray-500">
          <span>Loading system info...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-[#0a0a0a] px-6 py-2">
      <div className="flex items-center gap-6 text-sm font-mono text-gray-500 dark:text-gray-500">
        <span className="flex items-center gap-1">
          <span className={`w-2 h-2 rounded-full ${stats.cpu > 80 ? 'bg-red-500' : stats.cpu > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}></span>
          CPU {stats.cpu.toFixed(1)}%
        </span>
        <span className="flex items-center gap-1">
          <span className={`w-2 h-2 rounded-full ${stats.memory.percent > 80 ? 'bg-red-500' : stats.memory.percent > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}></span>
          Memory {stats.memory.used.toFixed(1)}GB / {stats.memory.total.toFixed(1)}GB ({stats.memory.percent.toFixed(0)}%)
        </span>
        <span className="flex items-center gap-1">
          <span className={`w-2 h-2 rounded-full ${stats.gpu.utilization > 80 ? 'bg-red-500' : stats.gpu.utilization > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}></span>
          GPU {stats.gpu.utilization.toFixed(1)}%
          {stats.gpu.memory_total > 0 && (
            <span className="opacity-75">({stats.gpu.memory_used.toFixed(1)}/{stats.gpu.memory_total.toFixed(1)}GB)</span>
          )}
        </span>
        {/* Ollama Status */}
        {stats.ollamaStatus && (
          <span className={`flex items-center gap-1 ${
            stats.ollamaStatus === 'running' ? 'text-green-500' : 
            stats.ollamaStatus === 'not installed' ? 'text-red-500' :
            stats.ollamaStatus === 'not responding' ? 'text-red-500' :
            'text-yellow-500'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              stats.ollamaStatus === 'running' ? 'bg-green-500' : 
              stats.ollamaStatus === 'not installed' ? 'bg-red-500' :
              stats.ollamaStatus === 'not responding' ? 'bg-red-500' :
              'bg-yellow-500'
            }`}></span>
            Ollama: {stats.ollamaStatus}
          </span>
        )}
      </div>
    </div>
  );
}