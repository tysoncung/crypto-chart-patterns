#!/usr/bin/env python3
"""
Advanced Technical Analysis Patterns
Implements advanced trading patterns and indicators
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

class AdvancedPatternDetector:
    """Advanced technical analysis patterns and indicators"""
    
    def __init__(self):
        self.patterns = {}
        
    def calculate_atr(self, prices, period=14):
        """
        Calculate Average True Range (ATR)
        Measures market volatility
        
        Args:
            prices: DataFrame with OHLC data
            period: ATR period (default 14)
        """
        high = prices['h']
        low = prices['l']
        close = prices['c']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def detect_three_drive_pattern(self, prices, max_min):
        """
        Detect Three Drive Pattern
        A reversal pattern with three consecutive drives to new highs/lows
        """
        patterns = defaultdict(list)
        
        for i in range(10, len(max_min)-2):
            window = max_min.iloc[i-10:i+2]
            
            if len(window) < 7:
                continue
            
            # Look for three drives (peaks or troughs)
            peaks = []
            troughs = []
            
            for j in range(1, len(window)-1):
                if window.iloc[j] > window.iloc[j-1] and window.iloc[j] > window.iloc[j+1]:
                    peaks.append(j)
                elif window.iloc[j] < window.iloc[j-1] and window.iloc[j] < window.iloc[j+1]:
                    troughs.append(j)
            
            # Bullish Three Drive (three ascending lows)
            if len(troughs) >= 3:
                if window.iloc[troughs[-1]] > window.iloc[troughs[-2]] > window.iloc[troughs[-3]]:
                    # Check for Fibonacci relationships (61.8% and 127.2%)
                    drive1 = abs(window.iloc[troughs[-2]] - window.iloc[troughs[-3]])
                    drive2 = abs(window.iloc[troughs[-1]] - window.iloc[troughs[-2]])
                    
                    if 0.5 < drive2/drive1 < 0.8:  # Approximately 61.8%
                        patterns['THREE_DRIVE_BULLISH'].append((window.index[0], window.index[-1]))
            
            # Bearish Three Drive (three descending highs)
            if len(peaks) >= 3:
                if window.iloc[peaks[-1]] < window.iloc[peaks[-2]] < window.iloc[peaks[-3]]:
                    drive1 = abs(window.iloc[peaks[-2]] - window.iloc[peaks[-3]])
                    drive2 = abs(window.iloc[peaks[-1]] - window.iloc[peaks[-2]])
                    
                    if 0.5 < drive2/drive1 < 0.8:
                        patterns['THREE_DRIVE_BEARISH'].append((window.index[0], window.index[-1]))
        
        return patterns
    
    def calculate_fibonacci_levels(self, prices, swing_high, swing_low):
        """
        Calculate Fibonacci retracement and extension levels
        
        Returns dict with levels:
        - Retracements: 23.6%, 38.2%, 50%, 61.8%, 78.6%
        - Extensions: 127.2%, 161.8%, 261.8%
        """
        diff = swing_high - swing_low
        
        levels = {
            'swing_high': swing_high,
            'swing_low': swing_low,
            # Retracement levels
            'ret_0': swing_high,
            'ret_236': swing_high - diff * 0.236,
            'ret_382': swing_high - diff * 0.382,
            'ret_500': swing_high - diff * 0.500,
            'ret_618': swing_high - diff * 0.618,
            'ret_786': swing_high - diff * 0.786,
            'ret_1000': swing_low,
            # Extension levels
            'ext_1272': swing_high + diff * 0.272,
            'ext_1618': swing_high + diff * 0.618,
            'ext_2618': swing_high + diff * 1.618,
        }
        
        return levels
    
    def detect_fibonacci_patterns(self, prices, max_min):
        """
        Detect price reactions at Fibonacci levels
        """
        patterns = defaultdict(list)
        
        # Find major swings
        for i in range(20, len(prices)-20):
            window = prices.iloc[i-20:i+20]
            
            swing_high = window['h'].max()
            swing_low = window['l'].min()
            
            # Calculate Fibonacci levels
            fib_levels = self.calculate_fibonacci_levels(prices, swing_high, swing_low)
            
            # Check for bounces at key levels
            current_price = prices.iloc[i]['c']
            
            # Check 61.8% retracement (Golden Ratio)
            if abs(current_price - fib_levels['ret_618']) < (swing_high - swing_low) * 0.02:
                # Look for reversal
                next_prices = prices.iloc[i:i+5]['c']
                if len(next_prices) > 0:
                    if next_prices.iloc[-1] > current_price * 1.01:  # Bounce up
                        patterns['FIB_618_BOUNCE'].append((i, i+5))
                    elif next_prices.iloc[-1] < current_price * 0.99:  # Breakdown
                        patterns['FIB_618_BREAK'].append((i, i+5))
            
            # Check 38.2% retracement
            if abs(current_price - fib_levels['ret_382']) < (swing_high - swing_low) * 0.02:
                next_prices = prices.iloc[i:i+5]['c']
                if len(next_prices) > 0:
                    if next_prices.iloc[-1] > current_price * 1.01:
                        patterns['FIB_382_BOUNCE'].append((i, i+5))
        
        return patterns
    
    def calculate_pivot_points(self, prices, period='D'):
        """
        Calculate Pivot Points (Classic, Fibonacci, Camarilla)
        Used for support and resistance levels
        """
        high = prices['h'].iloc[-1]
        low = prices['l'].iloc[-1]
        close = prices['c'].iloc[-1]
        
        # Classic Pivot Points
        pivot = (high + low + close) / 3
        
        classic = {
            'P': pivot,
            'R1': 2 * pivot - low,
            'R2': pivot + (high - low),
            'R3': high + 2 * (pivot - low),
            'S1': 2 * pivot - high,
            'S2': pivot - (high - low),
            'S3': low - 2 * (high - pivot)
        }
        
        # Fibonacci Pivot Points
        fib_pivot = {
            'P': pivot,
            'R1': pivot + 0.382 * (high - low),
            'R2': pivot + 0.618 * (high - low),
            'R3': pivot + 1.000 * (high - low),
            'S1': pivot - 0.382 * (high - low),
            'S2': pivot - 0.618 * (high - low),
            'S3': pivot - 1.000 * (high - low)
        }
        
        # Camarilla Pivot Points
        camarilla = {
            'R4': close + 1.1 * (high - low) / 2,
            'R3': close + 1.1 * (high - low) / 4,
            'R2': close + 1.1 * (high - low) / 6,
            'R1': close + 1.1 * (high - low) / 12,
            'S1': close - 1.1 * (high - low) / 12,
            'S2': close - 1.1 * (high - low) / 6,
            'S3': close - 1.1 * (high - low) / 4,
            'S4': close - 1.1 * (high - low) / 2
        }
        
        return {
            'classic': classic,
            'fibonacci': fib_pivot,
            'camarilla': camarilla
        }
    
    def detect_andrews_pitchfork(self, prices, max_min):
        """
        Detect Andrews' Pitchfork pattern
        Three parallel trend lines based on three pivot points
        """
        patterns = defaultdict(list)
        
        for i in range(10, len(max_min)-5):
            if i < 3:
                continue
                
            # Find three significant pivot points
            pivots = []
            for j in range(i-10, i):
                if j > 0 and j < len(max_min)-1:
                    # Check if it's a pivot
                    if max_min.iloc[j] > max_min.iloc[j-1] and max_min.iloc[j] > max_min.iloc[j+1]:
                        pivots.append((j, max_min.iloc[j], 'high'))
                    elif max_min.iloc[j] < max_min.iloc[j-1] and max_min.iloc[j] < max_min.iloc[j+1]:
                        pivots.append((j, max_min.iloc[j], 'low'))
            
            if len(pivots) >= 3:
                # Take the last three pivots
                p1, p2, p3 = pivots[-3:]
                
                # Calculate median line (from P1 through midpoint of P2-P3)
                midpoint_x = (p2[0] + p3[0]) / 2
                midpoint_y = (p2[1] + p3[1]) / 2
                
                # Calculate slope
                if p1[0] != midpoint_x:
                    slope = (midpoint_y - p1[1]) / (midpoint_x - p1[0])
                    
                    # Check if price respects the median line
                    respects_line = 0
                    for k in range(int(p3[0]), min(int(p3[0])+10, len(max_min))):
                        expected_y = p1[1] + slope * (k - p1[0])
                        if abs(max_min.iloc[k] - expected_y) < abs(p2[1] - p3[1]) * 0.1:
                            respects_line += 1
                    
                    if respects_line >= 3:
                        if slope > 0:
                            patterns['ANDREWS_PITCHFORK_UP'].append((p1[0], p3[0]))
                        else:
                            patterns['ANDREWS_PITCHFORK_DOWN'].append((p1[0], p3[0]))
        
        return patterns
    
    def calculate_ichimoku_cloud(self, prices, tenkan=9, kijun=26, senkou_b=52):
        """
        Calculate Ichimoku Cloud components
        
        Components:
        - Tenkan-sen (Conversion Line): 9-period midpoint
        - Kijun-sen (Base Line): 26-period midpoint
        - Senkou Span A (Leading Span A): Average of Tenkan and Kijun, plotted 26 periods ahead
        - Senkou Span B (Leading Span B): 52-period midpoint, plotted 26 periods ahead
        - Chikou Span (Lagging Span): Close price plotted 26 periods behind
        """
        high = prices['h']
        low = prices['l']
        close = prices['c']
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (high.rolling(window=tenkan).max() + 
                     low.rolling(window=tenkan).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (high.rolling(window=kijun).max() + 
                    low.rolling(window=kijun).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(window=senkou_b).max() + 
                         low.rolling(window=senkou_b).min()) / 2).shift(kijun)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-kijun)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    def detect_ichimoku_signals(self, prices):
        """
        Detect Ichimoku Cloud trading signals
        """
        patterns = defaultdict(list)
        
        # Calculate Ichimoku components
        ichimoku = self.calculate_ichimoku_cloud(prices)
        
        for i in range(52, len(prices)-26):
            tenkan = ichimoku['tenkan_sen'].iloc[i]
            kijun = ichimoku['kijun_sen'].iloc[i]
            span_a = ichimoku['senkou_span_a'].iloc[i]
            span_b = ichimoku['senkou_span_b'].iloc[i]
            close = prices['c'].iloc[i]
            
            # Skip if any value is NaN
            if pd.isna(tenkan) or pd.isna(kijun) or pd.isna(span_a) or pd.isna(span_b):
                continue
            
            # Bullish signals
            # TK Cross: Tenkan crosses above Kijun
            if i > 0:
                prev_tenkan = ichimoku['tenkan_sen'].iloc[i-1]
                prev_kijun = ichimoku['kijun_sen'].iloc[i-1]
                if not pd.isna(prev_tenkan) and not pd.isna(prev_kijun):
                    if prev_tenkan <= prev_kijun and tenkan > kijun:
                        patterns['ICHIMOKU_TK_BULL'].append((i-1, i))
            
            # Price above cloud (Bullish)
            cloud_top = max(span_a, span_b)
            cloud_bottom = min(span_a, span_b)
            if close > cloud_top:
                patterns['ICHIMOKU_ABOVE_CLOUD'].append((i, i))
            
            # Price below cloud (Bearish)
            elif close < cloud_bottom:
                patterns['ICHIMOKU_BELOW_CLOUD'].append((i, i))
            
            # Kumo breakout (Cloud breakout)
            if i > 0:
                prev_close = prices['c'].iloc[i-1]
                prev_cloud_top = max(ichimoku['senkou_span_a'].iloc[i-1], 
                                    ichimoku['senkou_span_b'].iloc[i-1]) if not pd.isna(ichimoku['senkou_span_a'].iloc[i-1]) else None
                
                if prev_cloud_top and not pd.isna(prev_cloud_top):
                    if prev_close <= prev_cloud_top and close > cloud_top:
                        patterns['ICHIMOKU_KUMO_BREAKOUT'].append((i-1, i))
        
        return patterns
    
    def detect_all_advanced_patterns(self, prices, max_min):
        """
        Detect all advanced patterns
        """
        all_patterns = {}
        
        # Three Drive Pattern
        three_drive = self.detect_three_drive_pattern(prices, max_min)
        all_patterns.update(three_drive)
        
        # Fibonacci Patterns
        fib_patterns = self.detect_fibonacci_patterns(prices, max_min)
        all_patterns.update(fib_patterns)
        
        # Andrews' Pitchfork
        pitchfork = self.detect_andrews_pitchfork(prices, max_min)
        all_patterns.update(pitchfork)
        
        # Ichimoku Signals
        ichimoku_signals = self.detect_ichimoku_signals(prices)
        all_patterns.update(ichimoku_signals)
        
        # Calculate indicators (not patterns but useful)
        atr = self.calculate_atr(prices)
        pivot_points = self.calculate_pivot_points(prices)
        
        # Store indicators separately
        self.indicators = {
            'atr': atr,
            'pivot_points': pivot_points
        }
        
        return all_patterns
    
    def get_pattern_description(self, pattern_name):
        """
        Get description of pattern
        """
        descriptions = {
            'THREE_DRIVE_BULLISH': 'Three ascending drives indicating potential bullish reversal',
            'THREE_DRIVE_BEARISH': 'Three descending drives indicating potential bearish reversal',
            'FIB_618_BOUNCE': 'Price bounce at 61.8% Fibonacci retracement (Golden Ratio)',
            'FIB_618_BREAK': 'Price break through 61.8% Fibonacci level',
            'FIB_382_BOUNCE': 'Price bounce at 38.2% Fibonacci retracement',
            'ANDREWS_PITCHFORK_UP': 'Upward trending Andrews Pitchfork channel',
            'ANDREWS_PITCHFORK_DOWN': 'Downward trending Andrews Pitchfork channel',
            'ICHIMOKU_TK_BULL': 'Tenkan-sen crosses above Kijun-sen (bullish signal)',
            'ICHIMOKU_ABOVE_CLOUD': 'Price trading above Ichimoku cloud (bullish)',
            'ICHIMOKU_BELOW_CLOUD': 'Price trading below Ichimoku cloud (bearish)',
            'ICHIMOKU_KUMO_BREAKOUT': 'Price breaks above Ichimoku cloud'
        }
        
        return descriptions.get(pattern_name, 'Unknown pattern')