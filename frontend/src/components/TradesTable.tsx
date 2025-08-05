import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface Trade {
  id: string;
  timestamp: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  value: number;
  pnl?: number;
  strategy?: string;
}

interface TradesTableProps {
  trades: Trade[];
  title?: string;
}

const TradesTable: React.FC<TradesTableProps> = ({ 
  trades, 
  title = "Trade History" 
}) => {
  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  const formatQuantity = (value: number) => value.toFixed(4);
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  if (!trades || trades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No trades available. Run a backtest to see trade history.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <div className="text-sm text-muted-foreground">
          {trades.length} trade{trades.length !== 1 ? 's' : ''} total
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2 font-medium">Date</th>
                <th className="text-left p-2 font-medium">Symbol</th>
                <th className="text-left p-2 font-medium">Side</th>
                <th className="text-right p-2 font-medium">Quantity</th>
                <th className="text-right p-2 font-medium">Price</th>
                <th className="text-right p-2 font-medium">Value</th>
                {trades.some(t => t.pnl !== undefined) && (
                  <th className="text-right p-2 font-medium">P&L</th>
                )}
                <th className="text-left p-2 font-medium">Strategy</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, index) => (
                <tr key={trade.id || index} className="border-b hover:bg-muted/50">
                  <td className="p-2 text-xs">
                    {formatDate(trade.timestamp)}
                  </td>
                  <td className="p-2 font-medium">
                    {trade.symbol}
                  </td>
                  <td className="p-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        trade.side.toLowerCase() === 'buy'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-2 text-right font-mono">
                    {formatQuantity(trade.quantity)}
                  </td>
                  <td className="p-2 text-right font-mono">
                    {formatCurrency(trade.price)}
                  </td>
                  <td className="p-2 text-right font-mono">
                    {formatCurrency(trade.value)}
                  </td>
                  {trades.some(t => t.pnl !== undefined) && (
                    <td className="p-2 text-right font-mono">
                      {trade.pnl !== undefined ? (
                        <span
                          className={
                            trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }
                        >
                          {formatCurrency(trade.pnl)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                  )}
                  <td className="p-2 text-xs text-muted-foreground">
                    {trade.strategy || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default TradesTable;