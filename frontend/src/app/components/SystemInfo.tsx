export default function SystemInfo() {
  return (
    <div className="px-6 py-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-600 dark:text-gray-400">CPU</span>
          <span className="font-medium text-gray-900 dark:text-white">2.4%</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-600 dark:text-gray-400">Memory</span>
          <span className="font-medium text-gray-900 dark:text-white">8.5GB / 23.2GB (37%)</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-600 dark:text-gray-400">GPU</span>
          <span className="font-medium text-gray-900 dark:text-white">0.0% (0.3/4.0GB)</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-600 dark:text-gray-400">Ollama:</span>
          <span className="font-medium text-green-500">running</span>
        </div>
      </div>
    </div>
  );
}
