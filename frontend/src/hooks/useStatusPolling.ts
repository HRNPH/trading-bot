import { useEffect, useRef } from 'react';
import { useTradingStore } from '../stores/useTradingStore';

export const useStatusPolling = (interval: number = 5000) => {
  const { isTrading, fetchStatus } = useTradingStore();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (isTrading) {
      // Initial fetch
      fetchStatus();
      
      // Set up polling
      intervalRef.current = setInterval(() => {
        fetchStatus();
      }, interval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    } else {
      // Clear interval when not trading
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [isTrading, fetchStatus, interval]);

  return { isTrading };
}; 