export function SystemStatus() {
  // Mock system stats
  const stats = {
    cpu: 5,
    memory: { used: 2, total: 16 },
    gpu: 56,
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-[#0a0a0a] px-6 py-2">
      <div className="flex items-center gap-6 text-sm font-mono text-gray-500 dark:text-gray-500">
        <span>CPU {stats.cpu}%</span>
        <span>Memory {stats.memory.used}GB / {stats.memory.total}GB</span>
        <span>GPU {stats.gpu}%</span>
      </div>
    </div>
  );
}