import { create } from 'zustand';
import { apiClient } from '../lib/api';

interface SymbolsState {
  symbols: string[];
  loading: boolean;
  error: string | null;
  
  setSymbols: (symbols: string[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  fetchSymbols: () => Promise<void>;
  addSymbol: (symbol: string, name?: string, description?: string) => Promise<void>;
}

export const useSymbolsStore = create<SymbolsState>((set, get) => ({
  // Initial state
  symbols: ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'],
  loading: false,
  error: null,

  // Actions
  setSymbols: (symbols) => set({ symbols }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  
  fetchSymbols: async () => {
    set({ loading: true, error: null });
    
    try {
      const result = await apiClient.get('/v1/symbols/symbols/');
      
      if (result.success) {
        set({ symbols: result.data.symbols, loading: false });
      } else {
        set({ error: result.message || 'Failed to fetch symbols', loading: false });
      }
    } catch (error) {
      console.error('Failed to fetch symbols:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch symbols', 
        loading: false 
      });
    }
  },
  
  addSymbol: async (symbol: string, name?: string, description?: string) => {
    set({ loading: true, error: null });
    
    try {
      const result = await apiClient.post('/v1/symbols/symbols/', {
        symbol: symbol.toUpperCase(),
        name: name || symbol.toUpperCase(),
        description: description || '',
      });

      if (result.success) {
        // Refresh symbols list
        get().fetchSymbols();
      } else {
        set({ error: result.message || 'Failed to add symbol', loading: false });
      }
    } catch (error) {
      console.error('Failed to add symbol:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to add symbol', 
        loading: false 
      });
    }
  },
})); 