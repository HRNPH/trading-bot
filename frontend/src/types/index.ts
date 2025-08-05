export interface BacktestResults {
  summary: {
    performance: {
      total_return: number;
      annualized_return: number;
      sharpe_ratio: number;
      max_drawdown: number;
      win_rate: number;
      profit_factor: number;
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
      open_trades: number;
      avg_win: number;
      avg_loss: number;
      max_win: number;
      max_loss: number;
      avg_duration_days: number;
    };
    drawdown_periods: Array<{
      start_date: string;
      end_date: string;
      max_drawdown: number;
      duration_days: number;
    }>;
    monthly_returns: Record<string, number>;
  };
  trades: Trade[];
  charts: {
    equity: ChartData;
    price: ChartData;
  };
  metadata: {
    symbol: string;
    strategy: string;
    timeframe: string;
    start_date: string;
    end_date: string;
    initial_cash: number;
  };
}

export interface LiveStatus {
  is_trading: boolean;
  portfolio: {
    cash: number;
    position: number;
    portfolio_value: number;
    total_trades: number;
    current_position_value: number;
  };
  performance: {
    total_trades: number;
    winning_trades: number;
    win_rate: number;
    total_pnl: number;
    current_portfolio_value: number;
    initial_cash: number;
    total_return: number;
  };
  recent_trades: Array<{
    timestamp: string;
    type: string;
    price: number;
    quantity: number;
    value: number;
    order_id: string;
    signal_type: string;
  }>;
  price_history: Array<{
    timestamp: string;
    price: number;
    volume: number;
    symbol: string;
  }>;
  chart_data?: Array<{
    timestamp: string;
    value: number;
  }>;
  last_updated: string;
}

export interface Trade {
  trade_id: number;
  entry_time: string;
  entry_price: string;
  exit_time?: string;
  exit_price?: string;
  profit_loss: string;
  profit_loss_pct: string;
  duration_days: number;
  status: string;
}

export interface ChartData {
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
}

export interface Symbol {
  id: string;
  symbol: string;
  name: string;
  description?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Strategy {
  name: string;
  display_name: string;
  description: string;
  parameters: Record<string, {
    type: string;
    default: number;
    min?: number;
    max?: number;
  }>;
} 