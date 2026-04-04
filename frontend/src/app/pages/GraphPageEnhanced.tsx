import { useState, useEffect } from "react";
import { Search, ZoomIn, ZoomOut, Maximize2, RefreshCw, X } from "lucide-react";
import { getGraph } from "../../api/index";

interface Node {
  id: string;
  name: string;
  category: 'document' | 'text' | 'code' | 'image' | 'other';
  summary: string;
  tags: string[];
  connections: number;
  x: number;
  y: number;
}

export default function GraphPageEnhanced() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [loading, setLoading] = useState(false);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [zoom, setZoom] = useState(1);
  const [viewBox, setViewBox] = useState({ width: 800, height: 600 });

  const categories = [
    { name: 'Documents', color: 'fill-blue-500', borderColor: 'border-blue-500' },
    { name: 'Text Files', color: 'fill-green-500', borderColor: 'border-green-500' },
    { name: 'Code', color: 'fill-amber-500', borderColor: 'border-amber-500' },
    { name: 'Images', color: 'fill-pink-500', borderColor: 'border-pink-500' },
    { name: 'Other', color: 'fill-gray-500', borderColor: 'border-gray-500' },
  ];

  // Force-directed layout simulation
  const runForceLayout = (nodeList: Node[]) => {
    if (nodeList.length === 0) return nodeList;
    
    const width = 800;
    const height = 600;
    const padding = 50;
    
    // Initialize positions if not set
    let positioned = nodeList.map((node, i) => ({
      ...node,
      x: node.x || Math.random() * (width - 2 * padding) + padding,
      y: node.y || Math.random() * (height - 2 * padding) + padding,
      vx: 0,
      vy: 0,
    }));
    
    // Run force simulation
    for (let iteration = 0; iteration < 100; iteration++) {
      // Repulsion between all nodes
      for (let i = 0; i < positioned.length; i++) {
        for (let j = i + 1; j < positioned.length; j++) {
          const dx = positioned[j].x - positioned[i].x;
          const dy = positioned[j].y - positioned[i].y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 5000 / (distance * distance);
          
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;
          
          positioned[i].vx -= fx;
          positioned[i].vy -= fy;
          positioned[j].vx += fx;
          positioned[j].vy += fy;
        }
      }
      
      // Attraction towards center
      const centerX = width / 2;
      const centerY = height / 2;
      for (let i = 0; i < positioned.length; i++) {
        positioned[i].vx += (centerX - positioned[i].x) * 0.01;
        positioned[i].vy += (centerY - positioned[i].y) * 0.01;
      }
      
      // Apply velocities and constrain to bounds
      for (let i = 0; i < positioned.length; i++) {
        positioned[i].x += positioned[i].vx * 0.5;
        positioned[i].y += positioned[i].vy * 0.5;
        
        // Damping
        positioned[i].vx *= 0.9;
        positioned[i].vy *= 0.9;
        
        // Keep within bounds
        positioned[i].x = Math.max(padding, Math.min(width - padding, positioned[i].x));
        positioned[i].y = Math.max(padding, Math.min(height - padding, positioned[i].y));
      }
    }
    
    return positioned.map(({ vx, vy, ...rest }) => rest);
  };

  // Fetch graph data from API
  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const data = await getGraph();
        
        // Transform API response to Node format
        const rawNodes: Node[] = data.nodes.map(node => ({
          id: node.id,
          name: node.name,
          category: 'document' as const,
          summary: node.summary || '',
          tags: node.tags || [],
          connections: node.val || 1,
          x: 0,
          y: 0,
        }));
        
        // Apply force-directed layout
        const layoutedNodes = runForceLayout(rawNodes);
        setNodes(layoutedNodes);
      } catch (err) {
        console.error('Failed to fetch graph:', err);
        setNodes([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraph();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    getGraph().then(data => {
      const rawNodes: Node[] = data.nodes.map(node => ({
        id: node.id,
        name: node.name,
        category: 'document' as const,
        summary: node.summary || '',
        tags: node.tags || [],
        connections: node.val || 1,
        x: 0,
        y: 0,
      }));
      const layoutedNodes = runForceLayout(rawNodes);
      setNodes(layoutedNodes);
    }).finally(() => setLoading(false));
  };

  const handleFitScreen = () => {
    setZoom(1);
    setViewBox({ width: 800, height: 600 });
  };

  const handleZoomIn = () => setZoom(Math.min(zoom + 0.2, 2));
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.2, 0.5));

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'document': return 'fill-blue-500';
      case 'text': return 'fill-green-500';
      case 'code': return 'fill-amber-500';
      case 'image': return 'fill-pink-500';
      default: return 'fill-gray-500';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'document': return 'Documents';
      case 'text': return 'Text Files';
      case 'code': return 'Code';
      case 'image': return 'Images';
      default: return 'Other';
    }
  };

  const filteredNodes = nodes.filter(node =>
    node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    node.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
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
            {filteredNodes.length} nodes, {filteredNodes.reduce((sum, n) => sum + n.connections, 0)} links
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Graph Visualization */}
        <div className="flex-1 relative bg-gray-50 dark:bg-gray-900 overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-black/30 flex items-center justify-center z-10">
              <div className="animate-spin text-white">
                <RefreshCw size={48} />
              </div>
            </div>
          )}

          {filteredNodes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <p className="text-lg">No documents to display. Upload some documents first!</p>
              </div>
            </div>
          ) : (
            <div className="w-full h-full relative p-8">
              <svg
                className="w-full h-full"
                style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
                viewBox={`0 0 ${viewBox.width} ${viewBox.height}`}
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
                      cx={node.x}
                      cy={node.y}
                      r="20"
                      className={`${getCategoryColor(node.category)} stroke-2 stroke-white dark:stroke-gray-900 transition-all hover:opacity-80`}
                    />
                    <text
                      x={node.x}
                      y={node.y + 35}
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
                  <span className={`w-3 h-3 rounded-full ${getCategoryColor(selectedNode.category).replace('fill-', 'bg-')}`}></span>
                  <span className="text-gray-900 dark:text-white">{getCategoryLabel(selectedNode.category)}</span>
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
                  Connections
                </label>
                <p className="text-gray-900 dark:text-white">{selectedNode.connections}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
