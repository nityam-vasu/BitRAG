import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { getStatus } from "../../api/index";

interface ServerStatus {
  initialized: boolean;
  status?: string;
  message?: string;
}

interface ServerStatusContextType {
  serverStatus: ServerStatus;
  loading: boolean;
}

const ServerStatusContext = createContext<ServerStatusContextType>({
  serverStatus: { initialized: false },
  loading: true,
});

export function useServerStatus() {
  return useContext(ServerStatusContext);
}

export function ServerStatusProvider({ children }: { children: ReactNode }) {
  const [serverStatus, setServerStatus] = useState<ServerStatus>({ initialized: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check status immediately
    checkStatus();
    
    // Poll every 5 seconds
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const status = await getStatus();
      setServerStatus({
        initialized: status.initialized ?? status.status === 'ready',
        status: status.status,
        message: status.message
      });
    } catch (err) {
      setServerStatus({ initialized: false });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ServerStatusContext.Provider value={{ serverStatus, loading }}>
      {children}
    </ServerStatusContext.Provider>
  );
}
