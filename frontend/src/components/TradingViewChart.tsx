import React, { useEffect, useRef } from "react";
import { createChart, LineSeries, CandlestickSeries } from "lightweight-charts";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface CandlestickChartData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface IndicatorData {
  time: string;
  value: number;
}

interface TradingViewChartProps {
  data: CandlestickChartData[];
  indicators?: {
    name: string;
    data: IndicatorData[];
    color?: string;
  }[];
  title?: string;
  height?: number;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  data,
  indicators = [],
  title = "Price Chart",
  height = 400,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);

  // Debug logging
  console.log("TradingViewChart render:", {
    dataLength: data?.length,
    indicatorsLength: indicators?.length,
    title,
    height,
    sampleData: data?.slice(0, 2),
  });

  // Helper function to convert ISO string to timestamp
  const convertTimeToTimestamp = (timeStr: string): number => {
    try {
      // v5 API expects UTC timestamp in seconds
      return Math.floor(new Date(timeStr).getTime() / 1000) as any;
    } catch (error) {
      console.error("Error converting time:", timeStr, error);
      return 0 as any;
    }
  };

  // Helper function to validate and format candlestick data
  const formatCandlestickData = (data: CandlestickChartData[]) => {
    const formatted = data
      .filter(
        (item) =>
          item.time &&
          typeof item.open === "number" &&
          typeof item.high === "number" &&
          typeof item.low === "number" &&
          typeof item.close === "number"
      )
      .map((item) => ({
        time: convertTimeToTimestamp(item.time),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }))
      .filter((item) => item.time > 0);

    console.log("Formatted candlestick data:", formatted.slice(0, 3));
    return formatted;
  };

  useEffect(() => {
    if (!chartContainerRef.current) {
      console.log("Chart container not ready");
      return;
    }

    console.log("Creating chart...");

    try {
      // Create chart
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height,
        layout: {
          background: { color: "#ffffff" },
          textColor: "#333",
        },
        grid: {
          vertLines: { color: "#f0f0f0" },
          horzLines: { color: "#f0f0f0" },
        },
        crosshair: {
          mode: 1,
        },
        rightPriceScale: {
          borderColor: "#cccccc",
        },
        timeScale: {
          borderColor: "#cccccc",
          timeVisible: true,
          secondsVisible: false,
        },
      });

      console.log("Chart created successfully");

      chartRef.current = chart;

      // Try to create candlestick series using the correct v5 API
      try {
        console.log("Trying to create candlestick series with v5 API...");
        const candlestickSeries = chart.addSeries(CandlestickSeries);
        candlestickSeries.applyOptions({
          upColor: "#26a69a",
          downColor: "#ef5350",
          borderVisible: false,
          wickUpColor: "#26a69a",
          wickDownColor: "#ef5350",
        });

        // Set the data
        const formattedData = formatCandlestickData(data) as any;
        candlestickSeries.setData(formattedData);
        candlestickSeriesRef.current = candlestickSeries;
        console.log("Candlestick series added successfully");

        // Helper function to normalize indicator data to price range
        const normalizeIndicatorData = (
          indicatorData: any[],
          priceData: any[]
        ) => {
          if (indicatorData.length === 0 || priceData.length === 0)
            return indicatorData;

          // Get price range
          const prices = priceData
            .map((item) => [item.open, item.high, item.low, item.close])
            .flat();
          const priceMin = Math.min(...prices);
          const priceMax = Math.max(...prices);
          const priceRange = priceMax - priceMin;

          // Get indicator range
          const indicatorValues = indicatorData
            .map((item) => item.value)
            .filter((v) => !isNaN(v) && isFinite(v));
          if (indicatorValues.length === 0) return indicatorData;

          const indicatorMin = Math.min(...indicatorValues);
          const indicatorMax = Math.max(...indicatorValues);
          const indicatorRange = indicatorMax - indicatorMin;

          // Skip normalization if indicator is already in price range (like moving averages)
          if (indicatorMin > priceMin * 0.5 && indicatorMax < priceMax * 1.5) {
            console.log(
              `Skipping normalization for indicator in price range: ${indicatorMin}-${indicatorMax} vs price ${priceMin}-${priceMax}`
            );
            return indicatorData;
          }

          // Normalize to price range (using 80% of price range to avoid overlap)
          const targetMin = priceMin + priceRange * 0.1;
          const targetMax = priceMax - priceRange * 0.1;
          const targetRange = targetMax - targetMin;

          console.log(
            `Normalizing indicator: ${indicatorMin}-${indicatorMax} -> ${targetMin.toFixed(
              2
            )}-${targetMax.toFixed(2)}`
          );

          return indicatorData.map((item) => ({
            ...item,
            value:
              indicatorRange > 0
                ? targetMin +
                  ((item.value - indicatorMin) / indicatorRange) * targetRange
                : targetMin,
          }));
        };

        // Add indicator series with labels and normalization
        indicators.forEach((indicator) => {
          try {
            console.log(`Adding indicator: ${indicator.name}`);
            const indicatorSeries = chart.addSeries(LineSeries);
            indicatorSeries.applyOptions({
              color: indicator.color || "#2196f3",
              lineWidth: 1,
              title: indicator.name, // Add title for labeling
              priceLineVisible: false,
              lastValueVisible: false,
            });

            // Format and normalize indicator data
            const rawIndicatorData = indicator.data.map((item) => ({
              time: convertTimeToTimestamp(item.time),
              value: item.value,
            }));

            const normalizedData = normalizeIndicatorData(
              rawIndicatorData,
              data
            ) as any;

            indicatorSeries.setData(normalizedData);
            console.log(
              `Indicator ${indicator.name} added successfully (${normalizedData.length} points)`
            );
          } catch (indicatorError) {
            console.error(
              `Failed to add indicator ${indicator.name}:`,
              indicatorError
            );
          }
        });
      } catch (error) {
        console.error("Failed to create candlestick series:", error);

        // Fallback: try line series
        try {
          console.log("Trying line series as fallback...");
          const lineSeries = chart.addSeries(LineSeries);
          lineSeries.applyOptions({
            color: "#2196f3",
            lineWidth: 2,
          });

          // Convert candlestick data to line data (using close prices)
          const lineData = formatCandlestickData(data).map((item) => ({
            time: item.time,
            value: item.close,
          })) as any;

          lineSeries.setData(lineData);
          candlestickSeriesRef.current = lineSeries;
          console.log("Line series added successfully as fallback");
        } catch (lineError) {
          console.error("Line series also failed:", lineError);
        }
      }

      // Handle resize
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener("resize", handleResize);

      return () => {
        console.log("Cleaning up chart");
        window.removeEventListener("resize", handleResize);
        if (chartRef.current) {
          chartRef.current.remove();
        }
      };
    } catch (error) {
      console.error("Error creating chart:", error);
    }
  }, [height]);

  useEffect(() => {
    if (candlestickSeriesRef.current && data.length > 0) {
      try {
        console.log("Setting candlestick data...");
        const formattedData = formatCandlestickData(data);
        if (formattedData.length > 0) {
          candlestickSeriesRef.current.setData(formattedData);
          console.log("Candlestick data set successfully");
        } else {
          console.warn("No valid candlestick data to display");
        }
      } catch (error) {
        console.error("Error setting candlestick data:", error);
      }
    } else {
      console.log("Cannot set data:", {
        hasSeries: !!candlestickSeriesRef.current,
        dataLength: data?.length,
      });
    }
  }, [data]);

  // Show loading state if no data
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            style={{
              width: "100%",
              height,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: "#f5f5f5",
              color: "#666",
            }}
          >
            Loading chart data...
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show debug info
  const sampleData = data.slice(0, 3);
  const formattedSample = formatCandlestickData(sampleData);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {/* Indicator Legend */}
        {indicators && indicators.length > 0 && (
          <div className="space-y-2 mt-2">
            <div className="flex flex-wrap gap-4">
              {indicators.map((indicator, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: indicator.color || "#2196f3" }}
                  />
                  <span className="text-sm text-muted-foreground">
                    {indicator.name}
                  </span>
                </div>
              ))}
            </div>
            <div className="text-xs text-muted-foreground">
              * CDC ActionZone uses only Fast EMA (12) and Slow EMA (26). Both
              show actual price levels.
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {/* Debug info */}
        <div
          style={{
            backgroundColor: "#f0f0f0",
            padding: "10px",
            marginBottom: "10px",
            fontSize: "12px",
            fontFamily: "monospace",
          }}
        >
          <div>Data length: {data.length}</div>
          <div>Sample data: {JSON.stringify(sampleData[0])}</div>
          <div>Formatted sample: {JSON.stringify(formattedSample[0])}</div>
          <div>Has series: {!!candlestickSeriesRef.current}</div>
        </div>

        <div
          ref={chartContainerRef}
          style={{
            width: "100%",
            height,
            border: "1px solid #ccc",
            backgroundColor: "#f9f9f9",
          }}
        />
      </CardContent>
    </Card>
  );
};

export default TradingViewChart;
