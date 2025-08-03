import { create } from 'zustand';

interface BacktestResults {
  summary: {
    performance: {
      total_return: number;
      sharpe_ratio: number;
      max_drawdown: number;
      win_rate: number;
    };
    trade_statistics: {
      total_trades: number;
      winning_trades: number;
      losing_trades: number;
    };
  };
  trades: any[];
  charts: any;
  metadata: any;
}

interface BacktestState {
  results: BacktestResults | null;
  loading: boolean;
  error: string | null;
  symbol: string;
  strategy: string;
  timeframe: string;
  days: number;
  parameters: Record<string, any>;
  
  setResults: (results: BacktestResults | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConfiguration: (config: Partial<BacktestState>) => void;
  setParameters: (parameters: Record<string, any>) => void;
  
  runBacktest: () => Promise<void>;
  clearResults: () => void;
}

export const useBacktestStore = create<BacktestState>((set, get) => ({
  // Initial state
  results: null,
  loading: false,
  error: null,
  symbol: 'AAPL',
  strategy: 'cdc_actionzone',
  timeframe: '1Day',
  days: 90,
  parameters: {},

  // Actions
  setResults: (results) => set({ results, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  setConfiguration: (config) => set(config),
  setParameters: (parameters) => set({ parameters }),
  
  runBacktest: async () => {
    const { symbol, strategy, timeframe, days, parameters } = get();
    
    set({ loading: true, error: null });
    
    try {
      const response = await fetch('/api/v1/backtest/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          strategy,
          timeframe,
          days,
          parameters,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        set({ results: result.data, loading: false });
      } else {
        set({ error: result.message || 'Backtest failed', loading: false });
      }
    } catch (error) {
      console.error('Failed to run backtest:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to run backtest', 
        loading: false 
      });
    }
  },
  
  clearResults: () => set({ results: null, error: null }),
})); 