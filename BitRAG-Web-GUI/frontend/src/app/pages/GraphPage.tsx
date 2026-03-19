import { useState, useRef, useCallback, useEffect } from 'react';
import { Layout } from '../components/Layout';
import ForceGraph2D from 'react-force-graph-2d';
import { Search, Filter, ZoomIn, ZoomOut, Maximize2, Info, RefreshCw } from 'lucide-react';

interface GraphNode {
  id: string;
  name: string;
  val: number;
  color: string;
  group: number;
  keywords?: string[];
  summary?: string;
}

interface GraphLink {
  source: string;
  target: string;
  value: number;
  label: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface ApiGraphNode {
  id: string;
  name: string;
  val: number;
  group: number;
  keywords: string[];
  summary?: string;
}

interface ApiGraphLink {
  source: string;
  target: string;
  value: number;
  label: string;
}

interface ApiGraphData {
  nodes: ApiGraphNode[];
  links: ApiGraphLink[];
}

export function GraphPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [minConnections, setMinConnections] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>();

  // Fetch graph data from backend
  const fetchGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/graph');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ApiGraphData = await response.json();
      
      // Convert API data to frontend format
      const nodes: GraphNode[] = data.nodes.map((node) => ({
        id: node.id,
        name: node.name,
        val: node.val || 3,
        color: getGroupColor(node.group),
        group: node.group,
        keywords: node.keywords,
        summary: node.summary || '',
      }));
      
      const links: GraphLink[] = data.links.map((link) => ({
        source: link.source,
        target: link.target,
        value: link.value,
        label: link.label,
      }));
      
      setGraphData({ nodes, links });
    } catch (err) {
      console.error('Error fetching graph data:', err);
      setError('Failed to load graph data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load graph data on mount
  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  // Filter connections based on minConnections setting
  useEffect(() => {
    if (graphData.nodes.length === 0) return;
    
    const filteredLinks = graphData.links.filter(link => link.value >= minConnections);
    setGraphData(prev => ({ ...prev, links: filteredLinks }));
  }, [minConnections, graphData.nodes.length]);

  const getGroupColor = (group: number) => {
    const colors: { [key: number]: string } = {
      1: '#9333ea', // Documents - purple
      2: '#06b6d4', // Text files - cyan
      3: '#f97316', // Code - orange
      4: '#10b981', // Images - emerald
      5: '#6b7280', // Other - gray
    };
    return colors[group] || '#6b7280';
  };

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node);
    
    // Highlight connected nodes and links
    const connectedNodes = new Set([node.id]);
    const connectedLinks = new Set();

    graphData.links.forEach((link: any) => {
      if (link.source.id === node.id || link.source === node.id) {
        connectedNodes.add(typeof link.target === 'object' ? link.target.id : link.target);
        connectedLinks.add(link);
      }
      if (link.target.id === node.id || link.target === node.id) {
        connectedNodes.add(typeof link.source === 'object' ? link.source.id : link.source);
        connectedLinks.add(link);
      }
    });

    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
  }, [graphData.links]);

  const getDocumentKeywords = (id: string) => {
    const node = graphData.nodes.find(n => n.id === id);
    return node?.keywords || [];
  };

  const handleBackgroundClick = useCallback(() => {
    setSelectedNode(null);
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());
  }, []);

  const handleZoomIn = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() * 1.2, 400);
    }
  };

  const handleZoomOut = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() / 1.2, 400);
    }
  };

  const handleFitView = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  };

  // Filter nodes based on search
  const filteredGraphData = {
    nodes: graphData.nodes.filter((node) =>
      node.name.toLowerCase().includes(searchQuery.toLowerCase())
    ),
    links: graphData.links.filter((link: any) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return (
        graphData.nodes.some((n) => n.id === sourceId && n.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        graphData.nodes.some((n) => n.id === targetId && n.name.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }),
  };

  const getDocumentByNodeId = (id: string) => {
    return mockDocuments.find((doc) => doc.id === id);
  };

  return (
    <Layout>
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Controls Bar */}
        <div className="bg-gray-50 dark:bg-[#111111] border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700"
                />
              </div>

              <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-3 py-2">
                <Filter className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">Min Keywords:</span>
                <select
                  value={minConnections}
                  onChange={(e) => setMinConnections(parseInt(e.target.value))}
                  className="bg-transparent text-sm text-gray-900 dark:text-gray-100 focus:outline-none font-mono"
                >
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={fetchGraphData}
                disabled={loading}
                className="p-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
                title="Refresh Graph"
              >
                <RefreshCw className={`w-4 h-4 text-gray-700 dark:text-gray-300 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={handleZoomIn}
                className="p-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </button>
              <button
                onClick={handleFitView}
                className="p-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Fit View"
              >
                <Maximize2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </button>
            </div>
          </div>
        </div>

        {/* Graph Container */}
        <div className="flex-1 relative bg-white dark:bg-[#0d0d0d]">
          <ForceGraph2D
            ref={fgRef}
            graphData={filteredGraphData}
            nodeLabel="name"
            nodeVal="val"
            nodeRelSize={5}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.name;
              const fontSize = 10 / globalScale;
              const nodeSize = 5;
              ctx.font = `${fontSize}px monospace`;
              
              const isHighlighted = highlightNodes.size === 0 || highlightNodes.has(node.id);
              const opacity = isHighlighted ? 1 : 0.4;
              
              // Draw node circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI);
              ctx.fillStyle = isHighlighted ? node.color : '#6b7280';
              ctx.globalAlpha = opacity;
              ctx.fill();
              ctx.globalAlpha = 1;
              
              // Draw border for selected node
              if (selectedNode?.id === node.id) {
                ctx.beginPath();
                ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2 / globalScale;
                ctx.stroke();
              }
              
              // Draw label only if highlighted or zoomed in
              if (isHighlighted && globalScale > 0.8) {
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillStyle = '#e5e7eb';
                ctx.globalAlpha = opacity;
                ctx.fillText(label, node.x, node.y + nodeSize + 3);
                ctx.globalAlpha = 1;
              }
            }}
            linkColor={(link: any) => {
              if (highlightLinks.size === 0) return '#4b5563';
              return highlightLinks.has(link) ? '#9ca3af' : '#374151';
            }}
            linkWidth={(link: any) => {
              if (highlightLinks.size === 0) return 1;
              return highlightLinks.has(link) ? 2 : 0.5;
            }}
            linkDirectionalParticles={(link: any) => {
              return highlightLinks.has(link) ? 3 : 0;
            }}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleSpeed={0.006}
            onNodeClick={handleNodeClick}
            onBackgroundClick={handleBackgroundClick}
            backgroundColor="transparent"
            enableNodeDrag={true}
            cooldownTicks={150}
            d3VelocityDecay={0.3}
            d3AlphaDecay={0.02}
            linkDistance={120}
            chargeStrength={-150}
          />

          {/* Legend */}
          <div className="absolute top-4 left-4 bg-gray-50/95 dark:bg-[#111111]/95 border border-gray-300 dark:border-gray-800 rounded-lg p-4 backdrop-blur-sm">
            <h3 className="text-sm font-mono text-gray-900 dark:text-gray-100 mb-2">Document Categories</h3>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#9333ea' }}></div>
                <span className="text-xs font-mono text-gray-700 dark:text-gray-300">Documents (PDF, DOC, etc.)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#06b6d4' }}></div>
                <span className="text-xs font-mono text-gray-700 dark:text-gray-300">Text Files (MD, TXT)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#f97316' }}></div>
                <span className="text-xs font-mono text-gray-700 dark:text-gray-300">Code (PY, JS, etc.)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#10b981' }}></div>
                <span className="text-xs font-mono text-gray-700 dark:text-gray-300">Images</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#6b7280' }}></div>
                <span className="text-xs font-mono text-gray-700 dark:text-gray-300">Other</span>
              </div>
            </div>
          </div>

          {/* Info Panel */}
          {selectedNode && (
            <div className="absolute top-4 right-4 bg-gray-50/95 dark:bg-[#111111]/95 border border-gray-300 dark:border-gray-800 rounded-lg p-4 backdrop-blur-sm max-w-sm">
              <div className="flex items-start gap-2 mb-3">
                <Info className="w-5 h-5 text-gray-600 dark:text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-mono text-gray-900 dark:text-gray-100 mb-1 truncate">{selectedNode.name}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-mono">
                    {(() => {
                      const doc = getDocumentByNodeId(selectedNode.id);
                      return doc ? `${doc.size} KB • ${doc.type.toUpperCase()}` : '';
                    })()}
                  </p>
                </div>
              </div>
              
              {/* Summary Section */}
              {selectedNode.summary && (
                <div className="mb-3">
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-mono mb-1">Summary:</p>
                  <p className="text-xs text-gray-700 dark:text-gray-300 font-mono leading-relaxed">
                    {selectedNode.summary}
                  </p>
                </div>
              )}
              
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-mono mb-1">Keywords:</p>
                  <div className="flex flex-wrap gap-1">
                    {(() => {
                      const keywords = selectedNode.keywords || [];
                      return keywords.length > 0 ? keywords.map((keyword) => (
                        <span
                          key={keyword}
                          className="px-2 py-0.5 bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs font-mono rounded"
                        >
                          {keyword}
                        </span>
                      )) : (
                        <span className="text-xs text-gray-500 font-mono">No keywords extracted</span>
                      );
                    })()}
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-mono mb-1">
                    Connected Documents: {highlightNodes.size - 1}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="absolute bottom-4 left-4 bg-gray-50/95 dark:bg-[#111111]/95 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-2 backdrop-blur-sm">
            <p className="text-xs font-mono text-gray-700 dark:text-gray-300">
              {filteredGraphData.nodes.length} documents • {filteredGraphData.links.length} connections
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}