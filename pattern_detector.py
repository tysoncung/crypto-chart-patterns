#!/usr/bin/env python3
"""
Crypto Chart Pattern Detector
Detects common chart patterns in cryptocurrency price data
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from collections import defaultdict
import warnings
import time
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
import json
import requests
from datetime import datetime, date, timedelta
import argparse

warnings.filterwarnings('ignore')

class PatternDetector:
    """Main class for detecting chart patterns in cryptocurrency data"""
    
    def __init__(self, symbol="ETHUSDT", interval="1h"):
        """
        Initialize the pattern detector
        
        Args:
            symbol: Trading pair symbol (e.g., "ETHUSDT", "BTCUSDT")
            interval: Time interval for candles (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        """
        self.symbol = symbol
        self.interval = interval
        self.patterns = {}
        self.prices = None
        
    def get_data(self, limit=500):
        """
        Fetch data from Binance API
        
        Args:
            limit: Number of candles to fetch (max 1000)
        """
        url = f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval={self.interval}&limit={limit}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            klines = np.array(r.json())
            return klines
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def binance_to_df(self, klines):
        """Convert Binance klines to DataFrame"""
        df = pd.DataFrame(klines.reshape(-1,12), dtype=float, 
                         columns=['t', 'o', 'h', 'l', 'c', 'v',
                                 'Close time', 'Quote asset volume',
                                 'Number of trades', 'Taker buy base asset volume',
                                 'Taker buy quote asset volume', 'Ignore'])
        
        df['t'] = pd.to_datetime(df['t'], unit='ms')
        df.set_index('t', inplace=True)
        return df
    
    def get_max_min(self, prices, smoothing=3, window_range=3):
        """
        Find local maxima and minima in price data
        
        Args:
            prices: DataFrame with OHLC data
            smoothing: Window for moving average smoothing
            window_range: Range for finding local extrema
        """
        smooth_prices = prices['c'].rolling(window=smoothing).mean().dropna()
        local_max = argrelextrema(smooth_prices.values, np.greater)[0]
        local_min = argrelextrema(smooth_prices.values, np.less)[0]
        
        price_local_max_dt = []
        for i in local_max:
            if (i > window_range) and (i < len(prices) - window_range):
                price_local_max_dt.append(prices.iloc[i-window_range:i+window_range]['c'].idxmax())
        
        price_local_min_dt = []
        for i in local_min:
            if (i > window_range) and (i < len(prices) - window_range):
                price_local_min_dt.append(prices.iloc[i-window_range:i+window_range]['c'].idxmin())
        
        maxima = pd.DataFrame(prices.loc[price_local_max_dt])
        minima = pd.DataFrame(prices.loc[price_local_min_dt])
        max_min = pd.concat([maxima, minima]).sort_index()
        max_min.index.name = 'date'
        max_min = max_min.reset_index()
        max_min = max_min[~max_min.date.duplicated()]
        
        p = prices.reset_index()
        max_min['day_num'] = p[p['t'].isin(max_min.date)].index.values
        max_min = max_min.set_index('day_num')['c']
        
        return max_min
    
    def find_patterns(self, max_min):
        """
        Find chart patterns in the extrema
        
        Patterns detected:
        - IHS: Inverse Head and Shoulders (bullish)
        - DT: Double Top (bearish)
        - DB: Double Bottom (bullish)
        - HS: Head and Shoulders (bearish)
        """
        patterns = defaultdict(list)
        
        for i in range(5, len(max_min)):
            window = max_min.iloc[i-5:i]
            
            # Pattern must play out in less than n units
            if window.index[-1] - window.index[0] > 100:
                continue
            
            a, b, c, d, e = window.iloc[0:5]
            
            # Inverse Head and Shoulders (Bullish)
            if a<b and c<a and c<e and c<d and e<d and abs(b-d)<=np.mean([b,d])*0.02:
                patterns['IHS'].append((window.index[0], window.index[-1]))
            
            # Double Top (Bearish)
            if a<c and c<b and c<d and c>e:
                patterns['DT'].append((window.index[0], window.index[-1]))
            
            # Double Bottom (Bullish)
            if a>c and c>b and c>d and c<e and abs(b-d)<=np.mean([b,d])*0.02:
                patterns['DB'].append((window.index[0], window.index[-1]))
            
            # Head and Shoulders (Bearish)
            if a>b and c>a and c>e and c>d and e>d and abs(b-d)<=np.mean([b,d])*0.02:
                patterns['HS'].append((window.index[0], window.index[-1]))
        
        return patterns
    
    def plot_patterns(self, prices, max_min, patterns, save=False):
        """
        Plot detected patterns on price chart
        
        Args:
            prices: OHLC price data
            max_min: Local extrema
            patterns: Detected patterns
            save: Whether to save the plot
        """
        colors = {'IHS': 'green', 'DT': 'red', 'DB': 'blue', 'HS': 'orange'}
        
        if len(patterns) == 0:
            print("No patterns found")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Plot 1: Price with all extrema
        prices_ = prices.reset_index()['c']
        ax1.plot(prices_, label='Price')
        ax1.scatter(max_min.index, max_min, s=100, alpha=.3, color='orange', label='Extrema')
        ax1.set_title(f'{self.symbol} - Price with Local Extrema')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Price with patterns
        ax2.plot(prices_, label='Price', alpha=0.5)
        
        for name, end_day_nums in patterns.items():
            for i, tup in enumerate(end_day_nums):
                sd, ed = tup
                ax2.plot(max_min.loc[sd:ed].index,
                        max_min.loc[sd:ed].values,
                        color=colors.get(name, 'gray'),
                        linewidth=2,
                        label=name if i == 0 else "")
        
        ax2.set_title(f'{self.symbol} - Detected Patterns')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = f"{self.symbol}_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=100)
            print(f"Plot saved as {filename}")
        
        plt.show()
    
    def calculate_returns(self, prices, patterns, periods=[1, 5, 10, 20]):
        """
        Calculate forward returns after pattern detection
        
        Args:
            prices: OHLC price data
            patterns: Detected patterns
            periods: List of forward periods to calculate returns
        """
        results = []
        
        for pattern_name, occurrences in patterns.items():
            for start, end in occurrences:
                result = {
                    'pattern': pattern_name,
                    'start_idx': start,
                    'end_idx': end,
                    'pattern_length': end - start
                }
                
                # Calculate forward returns
                for period in periods:
                    if end + period < len(prices):
                        current_price = prices.iloc[end]['c']
                        future_price = prices.iloc[end + period]['c']
                        returns = (future_price - current_price) / current_price * 100
                        result[f'return_{period}p'] = round(returns, 2)
                    else:
                        result[f'return_{period}p'] = None
                
                results.append(result)
        
        return pd.DataFrame(results)
    
    def run_analysis(self, smoothing=3, window_range=3, plot=True):
        """
        Run complete pattern detection analysis
        
        Args:
            smoothing: Moving average window
            window_range: Range for extrema detection
            plot: Whether to plot results
        """
        print(f"Fetching data for {self.symbol}...")
        klines = self.get_data()
        
        if klines is None:
            return None
        
        self.prices = self.binance_to_df(klines)
        print(f"Data fetched: {len(self.prices)} candles")
        
        print("Finding local extrema...")
        max_min = self.get_max_min(self.prices, smoothing, window_range)
        print(f"Found {len(max_min)} extrema points")
        
        print("Detecting patterns...")
        self.patterns = self.find_patterns(max_min)
        
        # Print pattern summary
        pattern_counts = {name: len(occurrences) for name, occurrences in self.patterns.items()}
        print("\nPatterns detected:")
        for name, count in pattern_counts.items():
            print(f"  {name}: {count}")
        
        if sum(pattern_counts.values()) == 0:
            print("No patterns found with current parameters")
            return None
        
        # Calculate returns
        print("\nCalculating forward returns...")
        returns_df = self.calculate_returns(self.prices, self.patterns)
        
        if not returns_df.empty:
            print("\nAverage returns by pattern:")
            avg_returns = returns_df.groupby('pattern').mean()
            print(avg_returns[[col for col in avg_returns.columns if 'return' in col]])
        
        if plot:
            self.plot_patterns(self.prices, max_min, self.patterns)
        
        return returns_df


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Detect chart patterns in cryptocurrency data')
    parser.add_argument('--symbol', default='ETHUSDT', help='Trading pair symbol (default: ETHUSDT)')
    parser.add_argument('--interval', default='1h', help='Time interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)')
    parser.add_argument('--smoothing', type=int, default=3, help='Smoothing window (default: 3)')
    parser.add_argument('--window', type=int, default=3, help='Window range for extrema (default: 3)')
    parser.add_argument('--no-plot', action='store_true', help='Disable plotting')
    parser.add_argument('--save-plot', action='store_true', help='Save plot to file')
    
    args = parser.parse_args()
    
    # Create detector
    detector = PatternDetector(args.symbol, args.interval)
    
    # Run analysis
    results = detector.run_analysis(
        smoothing=args.smoothing,
        window_range=args.window,
        plot=not args.no_plot
    )
    
    if results is not None and not results.empty:
        # Save results to CSV
        filename = f"{args.symbol}_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results.to_csv(filename, index=False)
        print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    main()