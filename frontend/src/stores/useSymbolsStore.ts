import { create } from 'zustand';
import { apiClient } from '../lib/api';

interface SymbolPriceData {
  symbol: string;
  candlestick: {
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
  };
}

interface SymbolsState {
  symbols: string[];
  selectedSymbol: string;
  symbolPriceData: SymbolPriceData | null;
  loading: boolean;
  error: string | null;
  
  fetchSymbols: () => Promise<void>;
  fetchSymbolPrice: (symbol: string, days?: number) => Promise<void>;
  setSelectedSymbol: (symbol: string) => void;
  addSymbol: (symbol: string) => void;
  clearError: () => void;
}

export const useSymbolsStore = create<SymbolsState>((set, get) => ({
  symbols: [],
  selectedSymbol: 'AAPL',
  symbolPriceData: null,
  loading: false,
  error: null,

  fetchSymbols: async () => {
    set({ loading: true, error: null });
    
    try {
      const result = await apiClient.get('/v1/symbols/');
      
      if (result.success) {
        set({ symbols: result.data.symbols, loading: false });
        // Auto-fetch price data for the first symbol
        const firstSymbol = result.data.symbols[0];
        if (firstSymbol) {
          get().setSelectedSymbol(firstSymbol);
        }
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

  fetchSymbolPrice: async (symbol: string, days: number = 365) => {
    set({ loading: true, error: null });
    
    try {
      const result = await apiClient.get(`/v1/symbols/${symbol}/price?days=${days}`);
      
      if (result.success) {
        set({ symbolPriceData: result.data, loading: false });
      } else {
        set({ error: result.message || 'Failed to fetch symbol price data', loading: false });
      }
    } catch (error) {
      console.error('Failed to fetch symbol price data:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch symbol price data', 
        loading: false 
      });
    }
  },

  setSelectedSymbol: (symbol: string) => {
    set({ selectedSymbol: symbol });
    // Automatically fetch price data for the selected symbol
    get().fetchSymbolPrice(symbol);
  },

  addSymbol: (symbol: string) => {
    set(state => ({ symbols: [...state.symbols, symbol] }));
    // Optionally, auto-fetch price data for the new symbol
    get().fetchSymbolPrice(symbol);
  },

  clearError: () => set({ error: null }),
})); 