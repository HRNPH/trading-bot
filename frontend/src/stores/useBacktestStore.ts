import { create } from 'zustand';
import { apiClient } from '../lib/api';

interface BacktestResults {
  summary: {
    performance: {
      total_return: number;
      sharpe_ratio: number;
      max_drawdown: number;
      win_rate: number;
    };
    risk_metrics: {
      volatility: number;
      var_95: number;
      cvar_95: number;
      calmar_ratio: number;
    };
    trade_statistics: {
      total_trades: number;
      winning_trades: number;
      losing_trades: number;
    };
  };
  trades: any[];
  charts: {
    equity?: {
      type: string;
      data: {
        x: string[];
        y: number[];
      };
      layout: {
        title: string;
        xaxis: { title: string };
        yaxis: { title: string };
      };
    };
    candlestick?: {
      type: string;
      data: Array<{
        time: string;
        open: number;
        high: number;
        low: number;
        close: number;
        volume: number;
      }>;
      indicators: Record<string, Array<{
        time: string;
        value: number;
      }>>;
      signals: {
        buy: Array<{
          time: string;
          price: number;
          text: string;
        }>;
        sell: Array<{
          time: string;
          price: number;
          text: string;
        }>;
      };
      layout: {
        title: string;
        xaxis: { title: string };
        yaxis: { title: string };
      };
    };
  };
  metadata: any;
}

interface BacktestConfig {
  symbol?: string;
  strategy?: string;
  timeframe?: string;
  days?: number;
  initialBalance?: number;
}

interface BacktestState {
  results: BacktestResults | null;
  loading: boolean;
  error: string | null;
  symbol: string;
  strategy: string;
  timeframe: string;
  days: number;
  initialBalance: number;
  
  setConfiguration: (config: Partial<BacktestConfig>) => void;
  setInitialBalance: (balance: number) => void;
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
  initialBalance: 100000, // Added initial balance
  parameters: {},

  // Actions
  setResults: (results: BacktestResults | null) => set({ results, error: null }),
  setLoading: (loading: boolean) => set({ loading }),
  setError: (error: string | null) => set({ error, loading: false }),
  setConfiguration: (config) => set({ ...config, results: null }),
  setInitialBalance: (balance) => set({ initialBalance: balance }),
  
  runBacktest: async () => {
    const { symbol, strategy, timeframe, days, initialBalance } = get();
    
    set({ loading: true, error: null });
    
    try {
      const result = await apiClient.post('/v1/backtest/', {
        symbol,
        strategy,
        timeframe,
        days,
        initialBalance,
      });
      
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