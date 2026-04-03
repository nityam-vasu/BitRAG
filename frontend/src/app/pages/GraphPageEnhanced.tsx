import { useState, useEffect } from "react";
import { Search, ZoomIn, ZoomOut, Maximize2, RefreshCw, X, Loader2 } from "lucide-react";

interface Node {
  id: string;
  name: string;
  group: number;
  summary: string;
  tags: string[];
  val: number;
  x?: number;
  y?: number;
}

interface Link {
  source: string;
  target: string;
  weight?: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function GraphPageEnhanced() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [zoom, setZoom] = useState(1);

  const getCategoryFromGroup = (group: number): string => {
    switch (group) {
      case 1: return 'document';
      case 2: return 'text';
      case 3: return 'code';
      case 4: return 'image';
      default: return 'other';
    }
  };

  const categories = [
    { name: 'Documents', color: 'bg-blue-500', textColor: 'text-blue-500' },
    { name: 'Text Files', color: 'bg-green-500', textColor: 'text-green-500' },
    { name: 'Code', color: 'bg-amber-500', textColor: 'text-amber-500' },
    { name: 'Images', color: 'bg-pink-500', textColor: 'text-pink-500' },
    { name: 'Other', color: 'bg-gray-500', textColor: 'text-gray-500' },
  ];

  // Fetch graph data on mount
  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async (refresh = false) => {
    setLoading(true);
    try {
      const url = refresh ? '/api/graph?refresh=true' : '/api/graph';
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setGraphData({
          nodes: data.nodes || [],
          links: data.links || data.edges || []
        });
      }
    } catch (err) {
      console.error('Failed to fetch graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchGraphData(true);
  };

  const handleZoomIn = () => setZoom(Math.min(zoom + 0.2, 2));
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.2, 0.5));
  const handleFitScreen = () => setZoom(1);

  const getCategoryColor = (group: number) => {
    switch (group) {
      case 1: return 'fill-blue-500';
      case 2: return 'fill-green-500';
      case 3: return 'fill-amber-500';
      case 4: return 'fill-pink-500';
      default: return 'fill-gray-500';
    }
  };

  const getCategoryLabel = (group: number) => {
    switch (group) {
      case 1: return 'Documents';
      case 2: return 'Text Files';
      case 3: return 'Code';
      case 4: return 'Images';
      default: return 'Other';
    }
  };

  const filteredNodes = graphData.nodes.filter(node =>
    node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    node.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Knowledge Graph</h2>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Search and Controls */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search nodes by name or tag..."
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={handleZoomIn}
              className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
              title="Zoom In"
            >
              <ZoomIn size={18} />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
              title="Zoom Out"
            >
              <ZoomOut size={18} />
            </button>
            <button
              onClick={handleFitScreen}
              className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
              title="Fit to Screen"
            >
              <Maximize2 size={18} />
            </button>
          </div>

          {/* Stats */}
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {filteredNodes.length} nodes, {graphData.links.length} links
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Graph Visualization */}
        <div className="flex-1 relative bg-gray-50 dark:bg-gray-900 overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-black/30 flex items-center justify-center z-10">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="animate-spin text-white" size={48} />
                <span className="text-white">Loading graph...</span>
              </div>
            </div>
          )}

          {filteredNodes.length === 0 && !loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <p className="text-lg">No documents to display. Upload some documents first!</p>
              </div>
            </div>
          ) : filteredNodes.length > 0 && (
            <div className="w-full h-full relative p-8">
              <svg
                className="w-full h-full"
                style={{ transform: `scale(${zoom})` }}
                viewBox="0 0 600 400"
              >
                {/* Draw connections */}
                {filteredNodes.map((node, i) => (
                  filteredNodes.slice(i + 1).map((otherNode, j) => (
                    <line
                      key={`${node.id}-${otherNode.id}`}
                      x1={node.x}
                      y1={node.y}
                      x2={otherNode.x}
                      y2={otherNode.y}
                      stroke="currentColor"
                      strokeWidth="1"
                      className="text-gray-300 dark:text-gray-600"
                      opacity="0.3"
                    />
                  ))
                ))}

                {/* Draw nodes */}
                {filteredNodes.map((node) => (
                  <g
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={100 + (index * 100) % 500}
                      cy={100 + Math.floor(index / 5) * 100}
                      r={node.val * 5}
                      className={`${getCategoryColor(node.group)} transition-all hover:opacity-80`}
                    />
                    <text
                      x={100 + (index * 100) % 500}
                      y={100 + Math.floor(index / 5) * 100 + (node.val * 5) + 20}
                      textAnchor="middle"
                      className="text-xs fill-gray-700 dark:fill-gray-300 pointer-events-none"
                    >
                      {node.name.length > 15 ? node.name.substring(0, 12) + '...' : node.name}
                    </text>
                  </g>
                ))}
              </svg>
            </div>
          )}
        </div>

        {/* Node Details Panel */}
        {selectedNode && (
          <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="p-6">
              {/* Close Button */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Node Details</h3>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                >
                  <X size={20} className="text-gray-400" />
                </button>
              </div>

              {/* Name */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Name
                </label>
                <p className="text-gray-900 dark:text-white">{selectedNode.name}</p>
              </div>

              {/* Category */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Category
                </label>
                <div className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${getCategoryColor(selectedNode.group).replace('fill-', 'bg-')}`}></span>
                  <span className="text-gray-900 dark:text-white">{getCategoryLabel(selectedNode.group)}</span>
                </div>
              </div>

              {/* Summary */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Summary
                </label>
                <p className="text-sm text-gray-700 dark:text-gray-300">{selectedNode.summary}</p>
              </div>

              {/* Tags */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Tags
                </label>
                <div className="flex flex-wrap gap-2">
                  {selectedNode.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Connections */}
              <div>
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Node Size
                </label>
                <p className="text-gray-900 dark:text-white">{selectedNode.val}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend Bar */}
      <div className="px-6 py-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center gap-6">
          {categories.map((category, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${category.color}`}></span>
              <span className="text-sm text-gray-600 dark:text-gray-400">{category.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
