import { useState, useEffect, useRef, useCallback } from 'react'
import { RefreshCw, Download, Search, ZoomIn, ZoomOut, Maximize2, BarChart3 } from 'lucide-react'
import ForceGraph, { ForceGraphMethods } from 'force-graph'
import { getGraph, regenerateGraph, getGraphInfo, GraphData, GraphNode, GraphLink } from '../api'

// Color palette for groups
const GROUP_COLORS: Record<number, string> = {
  1: '#3b82f6', // blue - documents
  2: '#22c55e', // green - text files
  3: '#f59e0b', // amber - code
  4: '#ec4899', // pink - images
  5: '#6b7280', // gray - other
}

export default function GraphPage() {
  const graphRef = useRef<HTMLDivElement>(null)
  const fgRef = useRef<ForceGraphMethods | undefined>(undefined)
  
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] })
  const [loading, setLoading] = useState(true)
  const [visualizeClicked, setVisualizeClicked] = useState(false)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null)
  const [graphInitialized, setGraphInitialized] = useState(false)

  // Check if graph data exists (without loading it)
  const checkGraphData = useCallback(async () => {
    setLoading(true)
    try {
      const info = await getGraphInfo()
      // If graph is initialized and has data, we can show the Visualize option
      return info.initialized && info.cache_size > 0
    } catch (err) {
      console.error('Failed to check graph info:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial check on mount
  useEffect(() => {
    checkGraphData()
  }, [checkGraphData])

  // Load graph data only when Visualize is clicked
  const handleVisualize = useCallback(async () => {
    setLoading(true)
    setVisualizeClicked(true)
    try {
      const data = await getGraph(false)
      setGraphData(data)
      setGraphInitialized(true)
    } catch (err) {
      console.error('Failed to load graph:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Initialize force-graph (only when visualize clicked and data available)
  useEffect(() => {
    if (!graphRef.current || graphData.nodes.length === 0 || !visualizeClicked) return

    // Clean up previous instance
    if (fgRef.current) {
      fgRef.current = undefined
    }

    const graph = ForceGraph()(graphRef.current)
      .graphData(graphData)
      .nodeId('id')
      .nodeLabel('name')
      .nodeVal('val')
      .nodeColor((node: any) => GROUP_COLORS[node.group] || GROUP_COLORS[5])
      .nodeCanvasObjectMode(() => 'replace')
      .nodeCanvasObject((node: any, ctx, globalScale) => {
        const label = node.name
        const fontSize = Math.max(12 / globalScale, 3)
        ctx.font = `${fontSize}px Sans-Serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        
        // Draw label
        ctx.fillStyle = node === hoveredNode ? '#fff' : '#ccc'
        ctx.fillText(label.length > 20 ? label.slice(0, 17) + '...' : label, node.x, node.y + 4)
      })
      .linkSource('source')
      .linkTarget('target')
      .linkValue('value')
      .linkLabel('label')
      .linkColor((link: any) => {
        const source = graphData.nodes.find(n => n.id === link.source)
        return source ? GROUP_COLORS[source.group] || GROUP_COLORS[5] : '#666'
      })
      .linkWidth(2)
      .onNodeClick((node: any) => {
        setSelectedNode(node as GraphNode)
      })
      .onNodeHover((node: any) => {
        setHoveredNode(node as GraphNode | null)
        graphRef.current!.style.cursor = node ? 'pointer' : 'grab'
      })
      .cooldownTicks(100)
      .d3AlphaDecay(0.02)
      .d3VelocityDecay(0.3)

    fgRef.current = graph

    // Center graph on load
    setTimeout(() => {
      graph.zoomToFit(400, 50)
    }, 1000)

    return () => {
      graph._destructor()
    }
  }, [graphData, hoveredNode, visualizeClicked, graphInitialized])

  // Handle refresh
  const handleRefresh = async () => {
    setLoading(true)
    try {
      await regenerateGraph()
      await loadGraph(true)
    } catch (err) {
      console.error('Failed to regenerate graph:', err)
    }
  }

  // Handle zoom controls
  const handleZoomIn = () => fgRef.current?.zoom(fgRef.current.zoom() * 1.5, 300)
  const handleZoomOut = () => fgRef.current?.zoom(fgRef.current.zoom() / 1.5, 300)
  const handleFitToScreen = () => fgRef.current?.zoomToFit(400, 50)

  // Filter nodes by search
  const filteredNodes = searchTerm
    ? graphData.nodes.filter(
        n =>
          n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          n.tags.some(t => t.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : graphData.nodes

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Knowledge Graph</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={handleVisualize}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50"
            >
              <BarChart3 size={16} />
              Visualize
            </button>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </div>
        
        {/* Search and controls - show only after visualize clicked */}
        {visualizeClicked && (
        <div className="mt-4 flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search nodes by name or tag..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div className="flex items-center gap-1">
            <button onClick={handleZoomIn} className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Zoom In">
              <ZoomIn size={16} />
            </button>
            <button onClick={handleZoomOut} className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Zoom Out">
              <ZoomOut size={16} />
            </button>
            <button onClick={handleFitToScreen} className="p-2 bg-gray-700 hover:bg-gray-600 rounded" title="Fit to Screen">
              <Maximize2 size={16} />
            </button>
          </div>
          
          <div className="text-sm text-gray-400">
            {graphData.nodes.length} nodes, {graphData.links.length} links
          </div>
        </div>
        )}
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph container */}
        <div className="flex-1 relative" ref={graphRef}>
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
              <RefreshCw className="animate-spin text-blue-500" size={32} />
            </div>
          )}
          {graphData.nodes.length === 0 && !loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
              {visualizeClicked ? (
                <p>No documents to display. Upload some documents first!</p>
              ) : (
                <>
                  <BarChart3 size={48} className="mb-4 opacity-50" />
                  <p className="text-lg mb-2">Click "Visualize" to generate the knowledge graph</p>
                  <p className="text-sm">This will show connections between your documents based on tags and summaries</p>
                </>
              )}
            </div>
          )}
        </div>

        {/* Node details panel */}
        {selectedNode && (
          <div className="w-80 border-l border-gray-700 bg-gray-800 p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Node Details</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 uppercase">Name</label>
                <p className="font-medium">{selectedNode.name}</p>
              </div>
              
              <div>
                <label className="text-xs text-gray-400 uppercase">Category</label>
                <p className="font-medium">
                  <span
                    className="inline-block w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: GROUP_COLORS[selectedNode.group] }}
                  />
                  {['Document', 'Text', 'Code', 'Image', 'Other'][selectedNode.group - 1] || 'Other'}
                </p>
              </div>
              
              <div>
                <label className="text-xs text-gray-400 uppercase">Summary</label>
                <p className="text-sm text-gray-300">{selectedNode.summary || 'No summary available'}</p>
              </div>
              
              <div>
                <label className="text-xs text-gray-400 uppercase">Tags</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {selectedNode.tags.length > 0 ? (
                    selectedNode.tags.map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-xs">
                        {tag}
                      </span>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400">No tags available</p>
                  )}
                </div>
              </div>
              
              <div>
                <label className="text-xs text-gray-400 uppercase">Connections</label>
                <p className="text-sm">
                  {graphData.links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id).length} links
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="p-4 border-t border-gray-700 bg-gray-800">
        <div className="flex items-center gap-6 text-sm">
          <span className="text-gray-400">Legend:</span>
          {Object.entries(GROUP_COLORS).map(([group, color]) => (
            <div key={group} className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-gray-300">
                {['Documents', 'Text Files', 'Code', 'Images', 'Other'][parseInt(group) - 1]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
