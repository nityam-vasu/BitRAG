import { X, CheckCircle, AlertCircle, Info, Loader2 } from "lucide-react";
import { useEffect } from "react";

export type ToastType = 'success' | 'error' | 'info' | 'loading';

interface ToastProps {
  message: string;
  type: ToastType;
  onClose: () => void;
  autoClose?: boolean;
  duration?: number;
}

export default function Toast({ 
  message, 
  type, 
  onClose, 
  autoClose = true,
  duration = 5000 
}: ToastProps) {
  useEffect(() => {
    if (autoClose && type !== 'loading') {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, onClose, type]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      case 'loading':
        return <Loader2 className="text-blue-500 animate-spin" size={20} />;
      case 'info':
      default:
        return <Info className="text-blue-500" size={20} />;
    }
  };

  const getBorderColor = () => {
    switch (type) {
      case 'success':
        return 'border-green-500';
      case 'error':
        return 'border-red-500';
      case 'loading':
      case 'info':
      default:
        return 'border-blue-500';
    }
  };

  return (
    <div 
      className={`fixed top-4 right-4 z-50 min-w-[320px] max-w-md bg-white dark:bg-gray-800 rounded-lg border-l-4 ${getBorderColor()} shadow-lg animate-slide-in-right`}
    >
      <div className="flex items-start gap-3 p-4">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-900 dark:text-white font-medium">
            {message}
          </p>
        </div>
        
        {type !== 'loading' && (
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
