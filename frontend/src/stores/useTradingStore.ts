import { create } from 'zustand';

interface TradingStatus {
  is_trading: boolean;
  portfolio: {
    cash: number;
    position: number;
    portfolio_value: number;
  };
  performance: {
    total_trades: number;
    win_rate: number;
    total_pnl: number;
  };
  recent_trades: any[];
}

interface TradingState {
  isTrading: boolean;
  status: TradingStatus | null;
  loading: boolean;
  error: string | null;
  symbol: string;
  strategy: string;
  timeframe: string;
  parameters: Record<string, any>;
  
  setIsTrading: (isTrading: boolean) => void;
  setStatus: (status: TradingStatus | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConfiguration: (config: Partial<TradingState>) => void;
  setParameters: (parameters: Record<string, any>) => void;
  
  startTrading: () => Promise<void>;
  stopTrading: () => Promise<void>;
  fetchStatus: () => Promise<void>;
  clearError: () => void;
}

export const useTradingStore = create<TradingState>((set, get) => ({
  // Initial state
  isTrading: false,
  status: null,
  loading: false,
  error: null,
  symbol: 'AAPL',
  strategy: 'cdc_actionzone',
  timeframe: '1Day',
  parameters: {},

  // Actions
  setIsTrading: (isTrading) => set({ isTrading }),
  setStatus: (status) => set({ status }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  setConfiguration: (config) => set(config),
  setParameters: (parameters) => set({ parameters }),
  
  startTrading: async () => {
    const { symbol, strategy, timeframe, parameters } = get();
    
    set({ loading: true, error: null });
    
    try {
      const response = await fetch('/api/v1/trading/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          strategy,
          timeframe,
          parameters,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        set({ isTrading: true, loading: false });
        // Start polling for status
        get().fetchStatus();
      } else {
        set({ error: result.message || 'Failed to start trading', loading: false });
      }
    } catch (error) {
      console.error('Failed to start trading:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to start trading', 
        loading: false 
      });
    }
  },
  
  stopTrading: async () => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch('/api/v1/trading/stop', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        set({ isTrading: false, status: null, loading: false });
      } else {
        set({ error: result.message || 'Failed to stop trading', loading: false });
      }
    } catch (error) {
      console.error('Failed to stop trading:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to stop trading', 
        loading: false 
      });
    }
  },
  
  fetchStatus: async () => {
    const { isTrading } = get();
    
    if (!isTrading) return;
    
    try {
      const response = await fetch('/api/v1/trading/status');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        set({ status: result.data });
      }
    } catch (error) {
      console.error('Failed to fetch trading status:', error);
    }
  },
  
  clearError: () => set({ error: null }),
})); 