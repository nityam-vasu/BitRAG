import { ChevronRight, FileText } from "lucide-react";

interface ProcessingCardProps {
  fileName: string;
  fileSize: string;
  content?: string;
  isExpanded?: boolean;
}

export default function ProcessingCard({ fileName, fileSize, content, isExpanded = false }: ProcessingCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Processing Header */}
      <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-700">
        <ChevronRight className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} size={18} />
        <FileText className="text-blue-500" size={20} />
        <div className="flex-1">
          <span className="text-gray-900 dark:text-white font-medium">Processing...</span>
          <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">({fileSize})</span>
        </div>
      </div>

      {/* Content (if provided and expanded) */}
      {content && isExpanded && (
        <div className="p-4 text-sm text-gray-700 dark:text-gray-300">
          {content}
        </div>
      )}
    </div>
  );
}
