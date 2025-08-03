import { create } from 'zustand';

interface Strategy {
  name: string;
  display_name: string;
  description: string;
  parameters: Record<string, any>;
  class: string;
}

interface StrategyParameters {
  [key: string]: {
    type: string;
    default: number;
    min?: number;
    max?: number;
  };
}

interface StrategiesState {
  strategies: Strategy[];
  loading: boolean;
  error: string | null;
  parameters: Record<string, StrategyParameters>;
  
  setStrategies: (strategies: Strategy[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setParameters: (strategyName: string, parameters: StrategyParameters) => void;
  
  fetchStrategies: () => Promise<void>;
  fetchStrategyParameters: (strategyName: string) => Promise<void>;
}

export const useStrategiesStore = create<StrategiesState>((set, get) => ({
  // Initial state
  strategies: [],
  loading: false,
  error: null,
  parameters: {},

  // Actions
  setStrategies: (strategies) => set({ strategies }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  setParameters: (strategyName, parameters) => 
    set((state) => ({
      parameters: { ...state.parameters, [strategyName]: parameters }
    })),
  
  fetchStrategies: async () => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch('/api/v1/backtest/strategies');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        set({ strategies: result.data.strategies, loading: false });
      } else {
        set({ error: result.message || 'Failed to fetch strategies', loading: false });
      }
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch strategies', 
        loading: false 
      });
    }
  },
  
  fetchStrategyParameters: async (strategyName: string) => {
    try {
      const response = await fetch(`/api/v1/backtest/strategies/${strategyName}/parameters`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        get().setParameters(strategyName, result.data.parameters);
      } else {
        console.error('Failed to fetch strategy parameters:', result.message);
      }
    } catch (error) {
      console.error('Failed to fetch strategy parameters:', error);
    }
  },
})); 