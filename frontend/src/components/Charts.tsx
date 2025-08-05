import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";

interface ChartData {
  type: string;
  data: {
    x: string[];
    y: number[];
    percentage?: number[];
  };
  layout: {
    title: string;
    xaxis: { title: string };
    yaxis: { title: string };
  };
}

interface ChartsProps {
  equityChart?: ChartData;
  priceChart?: ChartData;
}

const Charts: React.FC<ChartsProps> = ({ equityChart, priceChart }) => {
  const [equityView, setEquityView] = useState<'balance' | 'percentage'>('balance');

  // Transform chart data for recharts
  const transformChartData = (chartData: ChartData) => {
    if (!chartData?.data?.x || !chartData?.data?.y) return [];

    return chartData.data.x.map((x, index) => ({
      date: x,
      value: chartData.data.y[index],
      percentage: chartData.data.percentage?.[index] || 0,
    }));
  };

  const equityData = equityChart ? transformChartData(equityChart) : [];
  const priceData = priceChart ? transformChartData(priceChart) : [];

  return (
    <div className="space-y-6">
      {/* Equity Chart */}
      {equityChart && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Equity Curve</CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={equityView === 'balance' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEquityView('balance')}
                >
                  Balance ($)
                </Button>
                <Button
                  variant={equityView === 'percentage' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEquityView('percentage')}
                >
                  Percentage (%)
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => [
                    equityView === 'balance' 
                      ? `$${value.toFixed(2)}` 
                      : `${value.toFixed(2)}%`,
                    equityView === 'balance' ? "Equity" : "Return",
                  ]}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey={equityView === 'balance' ? 'value' : 'percentage'}
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Price Chart */}
      {priceChart && (
        <Card>
          <CardHeader>
            <CardTitle>Price Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => [
                    `$${value.toFixed(2)}`,
                    "Price",
                  ]}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* No charts available */}
      {!equityChart && !priceChart && (
        <Card>
          <CardContent className="pt-6">
            <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">
                No chart data available. Run a backtest to see charts.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Charts;
