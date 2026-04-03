import { Search, ZoomIn, ZoomOut, Maximize2, RefreshCw, X, FileText, Calendar, Tag } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import Toast, { ToastType } from "../components/Toast";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  originalX: number;
  originalY: number;
  vx: number; // velocity x
  vy: number; // velocity y
  color: string;
  category: string;
  size: string;
  summary: string;
  dateAdded: string;
  tags: string[];
}

interface DragState {
  nodeId: string | null;
  offsetX: number;
  offsetY: number;
}

export default function GraphPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [dragState, setDragState] = useState<DragState>({ nodeId: null, offsetX: 0, offsetY: 0 });
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const categories = [
    { name: 'Documents (PDF, DOC, etc.)', color: '#a855f7', bgColor: 'bg-purple-500', count: 15 },
    { name: 'Text Files (MD, TXT)', color: '#06b6d4', bgColor: 'bg-cyan-500', count: 8 },
    { name: 'Code (PY, JS, etc.)', color: '#f97316', bgColor: 'bg-orange-500', count: 23 },
    { name: 'Images', color: '#22c55e', bgColor: 'bg-green-500', count: 12 },
    { name: 'Other', color: '#6b7280', bgColor: 'bg-gray-500', count: 5 },
  ];

  const processingSteps = [
    { message: "Scanning documents...", duration: 1500 },
    { message: "Summarizing documents...", duration: 2500 },
    { message: "Extracting tags and keywords...", duration: 2000 },
    { message: "Building knowledge graph...", duration: 2000 },
    { message: "Analyzing relationships...", duration: 1500 },
  ];

  const generateRandomLayout = () => {
    const width = 800;
    const height = 600;
    const padding = 100;

    return nodes.map((node) => ({
      ...node,
      x: padding + Math.random() * (width - 2 * padding),
      y: padding + Math.random() * (height - 2 * padding),
      originalX: padding + Math.random() * (width - 2 * padding),
      originalY: padding + Math.random() * (height - 2 * padding),
      vx: 0,
      vy: 0,
    }));
  };

  const refreshLayout = () => {
    const newNodes = generateRandomLayout();
    setNodes(newNodes.map((node) => ({
      ...node,
      originalX: node.x,
      originalY: node.y,
    })));
    setToast({ message: "Layout refreshed!", type: 'success' });
  };

  const generateGraph = async () => {
    setIsProcessing(true);

    for (let i = 0; i < processingSteps.length; i++) {
      const stepMessage = `${processingSteps[i].message} (${i + 1}/${processingSteps.length})`;
      setToast({ message: stepMessage, type: 'loading' });
      await new Promise(resolve => setTimeout(resolve, processingSteps[i].duration));
    }

    setToast({ message: "Knowledge graph generated successfully!", type: 'success' });
    setIsProcessing(false);

    // Generate sample nodes
    const sampleDocs = [
      { name: 'Machine Learning Basics.pdf', category: 0, summary: 'Introduction to ML algorithms, supervised and unsupervised learning techniques.', tags: ['machine-learning', 'ai', 'algorithms'] },
      { name: 'Python Guide.md', category: 1, summary: 'Comprehensive guide to Python programming fundamentals and best practices.', tags: ['python', 'programming', 'tutorial'] },
      { name: 'data_processor.py', category: 2, summary: 'Script for processing and cleaning large datasets with pandas library.', tags: ['python', 'data', 'preprocessing'] },
      { name: 'neural_net.jpg', category: 3, summary: 'Diagram showing neural network architecture with multiple layers.', tags: ['neural-network', 'visualization', 'deep-learning'] },
      { name: 'Research Notes.txt', category: 1, summary: 'Notes on recent research papers in natural language processing.', tags: ['nlp', 'research', 'notes'] },
      { name: 'API Documentation.pdf', category: 0, summary: 'Complete API reference for the REST endpoints and authentication methods.', tags: ['api', 'documentation', 'rest'] },
      { name: 'model_training.py', category: 2, summary: 'Training script for deep learning models using TensorFlow framework.', tags: ['tensorflow', 'training', 'deep-learning'] },
      { name: 'architecture.png', category: 3, summary: 'System architecture diagram showing microservices and data flow.', tags: ['architecture', 'system-design', 'diagram'] },
    ];

    const width = 800;
    const height = 600;
    const padding = 100;

    const generatedNodes: Node[] = sampleDocs.map((doc, index) => {
      const x = padding + Math.random() * (width - 2 * padding);
      const y = padding + Math.random() * (height - 2 * padding);
      return {
        id: `node-${index}`,
        label: doc.name,
        x,
        y,
        originalX: x,
        originalY: y,
        vx: 0,
        vy: 0,
        color: categories[doc.category].color,
        category: categories[doc.category].name,
        size: `${(Math.random() * 100 + 50).toFixed(2)} KB`,
        summary: doc.summary,
        dateAdded: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
        tags: doc.tags,
      };
    });

    setNodes(generatedNodes);
  };

  const handleMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const svg = svgRef.current;
    if (!svg) return;

    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(svg.getScreenCTM()?.inverse());

    const node = nodes.find(n => n.id === nodeId);
    if (node) {
      setDragState({
        nodeId,
        offsetX: svgP.x - node.x,
        offsetY: svgP.y - node.y,
      });
    }
  };

  const handleSvgMouseMove = (e: React.MouseEvent) => {
    const svg = svgRef.current;
    if (!svg) return;

    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(svg.getScreenCTM()?.inverse());

    // Update mouse position for elastic effect
    setMousePos({ x: svgP.x, y: svgP.y });

    // Handle dragging
    if (dragState.nodeId) {
      setNodes(prevNodes =>
        prevNodes.map(node =>
          node.id === dragState.nodeId
            ? { ...node, x: svgP.x - dragState.offsetX, y: svgP.y - dragState.offsetY }
            : node
        )
      );
    }
  };

  const handleMouseUp = () => {
    if (dragState.nodeId) {
      setDragState({ nodeId: null, offsetX: 0, offsetY: 0 });
    }
  };

  const handleMouseLeave = () => {
    setMousePos(null);
    handleMouseUp();
  };

  // Physics simulation with mouse interaction
  useEffect(() => {
    if (nodes.length === 0) return;

    let animationId: number;
    const animate = () => {
      setNodes(prevNodes =>
        prevNodes.map(node => {
          // Skip physics for dragged node
          if (node.id === dragState.nodeId) {
            return node;
          }

          let fx = 0;
          let fy = 0;

          // Mouse push/pull force
          if (mousePos) {
            const dx = node.x - mousePos.x;
            const dy = node.y - mousePos.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const pushRadius = 150; // Radius of influence

            if (distance < pushRadius && distance > 0) {
              // Push force (repulsion) - stronger when closer
              const force = (pushRadius - distance) / pushRadius;
              const angle = Math.atan2(dy, dx);
              fx += Math.cos(angle) * force * 8; // Push strength
              fy += Math.sin(angle) * force * 8;
            }
          }

          // Spring force back to original position
          const springDx = node.originalX - node.x;
          const springDy = node.originalY - node.y;
          const springStrength = 0.05;
          fx += springDx * springStrength;
          fy += springDy * springStrength;

          // Update velocity with damping
          const damping = 0.85;
          let newVx = (node.vx + fx) * damping;
          let newVy = (node.vy + fy) * damping;

          // Apply velocity
          let newX = node.x + newVx;
          let newY = node.y + newVy;

          // Stop if very close to original position and velocity is low
          const distToOriginal = Math.sqrt(springDx * springDx + springDy * springDy);
          const speed = Math.sqrt(newVx * newVx + newVy * newVy);
          
          if (distToOriginal < 0.5 && speed < 0.1 && !mousePos) {
            newX = node.originalX;
            newY = node.originalY;
            newVx = 0;
            newVy = 0;
          }

          return {
            ...node,
            x: newX,
            y: newY,
            vx: newVx,
            vy: newVy,
          };
        })
      );
      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, [nodes.length, dragState.nodeId, mousePos]);

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header with Search and Controls */}
      <div className="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search documents..."
                className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-1">
              <button
                className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
                title="Zoom In"
              >
                <ZoomIn size={18} />
              </button>
              <button
                className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
                title="Zoom Out"
              >
                <ZoomOut size={18} />
              </button>
              <button
                className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-900 dark:text-white transition-colors"
                title="Fit to Screen"
              >
                <Maximize2 size={18} />
              </button>
            </div>

            {/* Refresh Layout Button */}
            <button
              onClick={refreshLayout}
              disabled={nodes.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Rearrange nodes"
            >
              <RefreshCw size={18} />
              Refresh Layout
            </button>

            {/* Generate Graph Button */}
            <button
              onClick={generateGraph}
              disabled={isProcessing}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={18} className={isProcessing ? 'animate-spin' : ''} />
              {isProcessing ? 'Processing...' : 'Generate Graph'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar with Categories */}
        <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Document Categories</h3>
          
          <div className="space-y-3">
            {categories.map((category, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              >
                <span className={`w-3 h-3 rounded-full ${category.bgColor}`}></span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{category.name}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Interaction Hint */}
          {nodes.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-xs text-blue-700 dark:text-blue-300 font-medium mb-2">💡 Interactive Graph</p>
              <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                <li>• Hover to push nodes</li>
                <li>• Drag nodes around</li>
                <li>• Click for details</li>
              </ul>
            </div>
          )}
        </div>

        {/* Graph Visualization Area */}
        <div className="flex-1 bg-gray-50 dark:bg-gray-900 overflow-hidden">
          {nodes.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <div className="w-32 h-32 mx-auto mb-6 rounded-full border-4 border-dashed border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <div className="text-4xl">📊</div>
                </div>
                <p className="text-lg font-medium mb-2">Knowledge Graph Visualization</p>
                <p className="text-sm">Click "Generate Graph" to visualize document relationships</p>
              </div>
            </div>
          ) : (
            <svg
              ref={svgRef}
              className="w-full h-full"
              viewBox="0 0 1000 700"
              onMouseMove={handleSvgMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseLeave}
            >
              {/* Mouse influence radius indicator (debug) */}
              {mousePos && (
                <circle
                  cx={mousePos.x}
                  cy={mousePos.y}
                  r="150"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="1"
                  strokeDasharray="5,5"
                  opacity="0.2"
                  pointerEvents="none"
                />
              )}

              {/* Connection lines */}
              {nodes.map((node, i) =>
                nodes.slice(i + 1).map((otherNode) => {
                  const distance = Math.sqrt(
                    Math.pow(node.x - otherNode.x, 2) + Math.pow(node.y - otherNode.y, 2)
                  );
                  if (distance < 200) {
                    return (
                      <line
                        key={`${node.id}-${otherNode.id}`}
                        x1={node.x}
                        y1={node.y}
                        x2={otherNode.x}
                        y2={otherNode.y}
                        stroke="#d1d5db"
                        strokeWidth="1"
                        opacity="0.3"
                      />
                    );
                  }
                  return null;
                })
              )}

              {/* Nodes */}
              {nodes.map((node) => (
                <g key={node.id}>
                  {/* Node circle */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r="30"
                    fill={node.color}
                    stroke="#fff"
                    strokeWidth="3"
                    className="cursor-move hover:opacity-80 transition-opacity"
                    onMouseDown={(e) => handleMouseDown(node.id, e)}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNode(node);
                    }}
                  />
                  
                  {/* Node label */}
                  <text
                    x={node.x}
                    y={node.y + 50}
                    textAnchor="middle"
                    className="fill-gray-700 dark:fill-gray-300 text-xs font-medium pointer-events-none select-none"
                    style={{ fontSize: '12px' }}
                  >
                    {node.label.length > 15 ? node.label.substring(0, 15) + '...' : node.label}
                  </text>
                </g>
              ))}
            </svg>
          )}
        </div>
      </div>

      {/* Node Details Modal */}
      {selectedNode && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedNode(null)}
        >
          <div 
            className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl border border-gray-200 dark:border-gray-700 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: selectedNode.color }}
                ></div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {selectedNode.label}
                </h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {/* File Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <FileText size={16} className="text-gray-400" />
                  <span className="text-gray-600 dark:text-gray-400">Category:</span>
                  <span className="text-gray-900 dark:text-white font-medium">{selectedNode.category}</span>
                </div>
                
                <div className="flex items-center gap-2 text-sm">
                  <FileText size={16} className="text-gray-400" />
                  <span className="text-gray-600 dark:text-gray-400">Size:</span>
                  <span className="text-gray-900 dark:text-white font-medium">{selectedNode.size}</span>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Calendar size={16} className="text-gray-400" />
                  <span className="text-gray-600 dark:text-gray-400">Date Added:</span>
                  <span className="text-gray-900 dark:text-white font-medium">{selectedNode.dateAdded}</span>
                </div>
              </div>

              {/* Summary */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Summary</h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {selectedNode.summary}
                </p>
              </div>

              {/* Tags */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <Tag size={16} />
                  Tags
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedNode.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setSelectedNode(null)}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white transition-colors"
              >
                Close
              </button>
              <button
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
              >
                View Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          autoClose={toast.type !== 'loading'}
        />
      )}
    </div>
  );
}
