import React, { useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Plus, Play, Square, Activity, AlertCircle } from "lucide-react";
import {
  useBacktestStore,
  useTradingStore,
  useSymbolsStore,
  useStrategiesStore,
} from "../stores";
import { useStatusPolling } from "../hooks/useStatusPolling";

const Dashboard: React.FC = () => {
  // Initialize stores
  const {
    results: backtestResults,
    loading: backtestLoading,
    error: backtestError,
    symbol: backtestSymbol,
    strategy: backtestStrategy,
    timeframe: backtestTimeframe,
    days: backtestDays,
    setConfiguration: setBacktestConfig,
    runBacktest,
  } = useBacktestStore();

  const {
    isTrading,
    status: liveStatus,
    loading: tradingLoading,
    error: tradingError,
    setConfiguration: setTradingConfig,
    startTrading,
    stopTrading,
  } = useTradingStore();

  const {
    symbols,
    error: symbolsError,
    fetchSymbols,
    addSymbol,
  } = useSymbolsStore();

  const {
    strategies,
    error: strategiesError,
    fetchStrategies,
  } = useStrategiesStore();

  // Status polling
  useStatusPolling();

  // Initialize data on component mount
  useEffect(() => {
    fetchSymbols();
    fetchStrategies();
  }, [fetchSymbols, fetchStrategies]);

  // State for add symbol dialog
  const [showAddSymbol, setShowAddSymbol] = React.useState(false);
  const [newSymbol, setNewSymbol] = React.useState("");
  const [symbolName, setSymbolName] = React.useState("");
  const [symbolDescription, setSymbolDescription] = React.useState("");

  const handleRunBacktest = () => {
    runBacktest();
  };

  const handleStartLiveTrading = () => {
    startTrading();
  };

  const handleStopLiveTrading = () => {
    stopTrading();
  };

  const handleAddSymbol = async () => {
    await addSymbol(newSymbol, symbolName, symbolDescription);
    setShowAddSymbol(false);
    setNewSymbol("");
    setSymbolName("");
    setSymbolDescription("");
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">
          Trading Bot Platform
        </h1>
        <p className="text-muted-foreground mt-2">
          Advanced algorithmic trading with real-time analytics
        </p>
      </div>

      {/* Error Display */}
      {(backtestError || tradingError || symbolsError || strategiesError) && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">
                {backtestError ||
                  tradingError ||
                  symbolsError ||
                  strategiesError}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Strategy Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Configuration</CardTitle>
          <CardDescription>
            Configure your trading strategy parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Symbol</label>
              <div className="flex gap-2">
                <Select
                  value={backtestSymbol}
                  onValueChange={(value) => {
                    setBacktestConfig({ symbol: value });
                    setTradingConfig({ symbol: value });
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select symbol" />
                  </SelectTrigger>
                  <SelectContent>
                    {symbols.map((symbol: string) => (
                      <SelectItem key={symbol} value={symbol}>
                        {symbol}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Dialog open={showAddSymbol} onOpenChange={setShowAddSymbol}>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="icon">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add New Symbol</DialogTitle>
                      <DialogDescription>
                        Add a new trading symbol to your portfolio
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Symbol</label>
                        <Input
                          placeholder="e.g., AAPL"
                          value={newSymbol}
                          onChange={(e) => setNewSymbol(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">
                          Name (Optional)
                        </label>
                        <Input
                          placeholder="e.g., Apple Inc."
                          value={symbolName}
                          onChange={(e) => setSymbolName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">
                          Description (Optional)
                        </label>
                        <Input
                          placeholder="Brief description"
                          value={symbolDescription}
                          onChange={(e) => setSymbolDescription(e.target.value)}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => setShowAddSymbol(false)}
                      >
                        Cancel
                      </Button>
                      <Button onClick={handleAddSymbol}>Add Symbol</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Strategy</label>
              <Select
                value={backtestStrategy}
                onValueChange={(value) => {
                  setBacktestConfig({ strategy: value });
                  setTradingConfig({ strategy: value });
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((strategy: any) => (
                    <SelectItem key={strategy.name} value={strategy.name}>
                      {strategy.display_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Timeframe</label>
              <Select
                value={backtestTimeframe}
                onValueChange={(value) => {
                  setBacktestConfig({ timeframe: value });
                  setTradingConfig({ timeframe: value });
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select timeframe" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1Day">1 Day</SelectItem>
                  <SelectItem value="1Hour">1 Hour</SelectItem>
                  <SelectItem value="15Min">15 Minutes</SelectItem>
                  <SelectItem value="5Min">5 Minutes</SelectItem>
                  <SelectItem value="1Min">1 Minute</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Days Back: {backtestDays}
              </label>
              <input
                type="range"
                min="30"
                max="365"
                value={backtestDays}
                onChange={(e) =>
                  setBacktestConfig({ days: parseInt(e.target.value) })
                }
                step="30"
                className="w-full"
              />
            </div>
          </div>

          <div className="flex justify-center gap-4 mt-6">
            <Button
              onClick={handleRunBacktest}
              disabled={backtestLoading}
              className="flex items-center gap-2"
            >
              <Activity className="h-4 w-4" />
              {backtestLoading ? "Running..." : "Run Backtest"}
            </Button>
            <Button
              onClick={handleStartLiveTrading}
              disabled={isTrading || tradingLoading}
              variant="default"
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              {tradingLoading ? "Starting..." : "Start Live Trading"}
            </Button>
            <Button
              onClick={handleStopLiveTrading}
              disabled={!isTrading || tradingLoading}
              variant="destructive"
              className="flex items-center gap-2"
            >
              <Square className="h-4 w-4" />
              {tradingLoading ? "Stopping..." : "Stop Live Trading"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Backtest Results */}
      {backtestResults && (
        <Card>
          <CardHeader>
            <CardTitle>Backtest Results</CardTitle>
            <CardDescription>Performance metrics and analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
              <div className="text-center">
                <div
                  className={`text-2xl font-bold ${
                    backtestResults.summary.performance.total_return >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {formatPercentage(
                    backtestResults.summary.performance.total_return
                  )}
                </div>
                <div className="text-sm text-muted-foreground">
                  Total Return
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {backtestResults.summary.performance.sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Sharpe Ratio
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {formatPercentage(
                    backtestResults.summary.performance.max_drawdown
                  )}
                </div>
                <div className="text-sm text-muted-foreground">
                  Max Drawdown
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {formatPercentage(
                    backtestResults.summary.performance.win_rate
                  )}
                </div>
                <div className="text-sm text-muted-foreground">Win Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {backtestResults.summary.trade_statistics.total_trades}
                </div>
                <div className="text-sm text-muted-foreground">
                  Total Trades
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {formatPercentage(
                    backtestResults.summary.risk_metrics.volatility
                  )}
                </div>
                <div className="text-sm text-muted-foreground">Volatility</div>
              </div>
            </div>

            {/* Charts would go here - simplified for now */}
            <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">
                Charts will be displayed here
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Live Trading Dashboard */}
      {isTrading && liveStatus && (
        <Card>
          <CardHeader>
            <CardTitle>Live Trading Dashboard</CardTitle>
            <CardDescription>Real-time portfolio performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(liveStatus.portfolio.portfolio_value)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Portfolio Value
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(liveStatus.portfolio.cash)}
                </div>
                <div className="text-sm text-muted-foreground">Cash</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {liveStatus.portfolio.position.toFixed(2)}
                </div>
                <div className="text-sm text-muted-foreground">Position</div>
              </div>
              <div className="text-center">
                <div
                  className={`text-2xl font-bold ${
                    liveStatus.performance.total_return >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {formatPercentage(liveStatus.performance.total_return)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Total Return
                </div>
              </div>
            </div>

            <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">
                Live price chart will be displayed here
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
