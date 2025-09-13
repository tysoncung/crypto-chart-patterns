#!/usr/bin/env python3
"""
Enhanced Chart Pattern Detector
Adds more advanced patterns to the crypto chart pattern detection
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

class EnhancedPatternDetector:
    """Enhanced pattern detector with additional chart patterns"""
    
    def __init__(self):
        self.patterns = {}
        
    def detect_triangle_patterns(self, max_min, prices):
        """
        Detect triangle patterns (ascending, descending, symmetrical)
        """
        patterns = defaultdict(list)
        
        for i in range(4, len(max_min)):
            window = max_min.iloc[i-4:i]
            
            if window.index[-1] - window.index[0] > 50:
                continue
            
            # Get highs and lows
            highs = []
            lows = []
            for idx in window.index:
                if idx > 0:
                    prev_val = max_min.iloc[idx-1] if idx-1 in max_min.index else None
                    next_val = max_min.iloc[idx+1] if idx+1 < len(max_min) else None
                    
                    if prev_val is not None and next_val is not None:
                        if max_min.iloc[idx] > prev_val and max_min.iloc[idx] > next_val:
                            highs.append(max_min.iloc[idx])
                        elif max_min.iloc[idx] < prev_val and max_min.iloc[idx] < next_val:
                            lows.append(max_min.iloc[idx])
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Ascending Triangle: flat top, rising bottom
                if abs(highs[-1] - highs[0]) < highs[0] * 0.02 and lows[-1] > lows[0] * 1.02:
                    patterns['ASCENDING_TRIANGLE'].append((window.index[0], window.index[-1]))
                
                # Descending Triangle: falling top, flat bottom
                if highs[-1] < highs[0] * 0.98 and abs(lows[-1] - lows[0]) < lows[0] * 0.02:
                    patterns['DESCENDING_TRIANGLE'].append((window.index[0], window.index[-1]))
                
                # Symmetrical Triangle: converging highs and lows
                if highs[-1] < highs[0] * 0.98 and lows[-1] > lows[0] * 1.02:
                    patterns['SYMMETRICAL_TRIANGLE'].append((window.index[0], window.index[-1]))
        
        return patterns
    
    def detect_wedge_patterns(self, max_min):
        """
        Detect wedge patterns (rising and falling)
        """
        patterns = defaultdict(list)
        
        for i in range(5, len(max_min)):
            window = max_min.iloc[i-5:i]
            
            if window.index[-1] - window.index[0] > 60:
                continue
            
            values = window.values
            indices = np.arange(len(values))
            
            # Fit trend lines
            z = np.polyfit(indices, values, 1)
            slope = z[0]
            
            # Calculate variance from trend
            trend = np.poly1d(z)
            residuals = values - trend(indices)
            variance = np.std(residuals)
            
            # Rising Wedge: upward slope with decreasing volatility
            if slope > 0 and variance < np.mean(values) * 0.05:
                if max(residuals[:2]) > max(residuals[-2:]):  # Converging
                    patterns['RISING_WEDGE'].append((window.index[0], window.index[-1]))
            
            # Falling Wedge: downward slope with decreasing volatility
            if slope < 0 and variance < np.mean(values) * 0.05:
                if abs(min(residuals[:2])) > abs(min(residuals[-2:])):  # Converging
                    patterns['FALLING_WEDGE'].append((window.index[0], window.index[-1]))
        
        return patterns
    
    def detect_flag_patterns(self, prices, max_min):
        """
        Detect flag and pennant patterns
        """
        patterns = defaultdict(list)
        
        for i in range(10, len(prices)-5):
            # Look for strong trend (pole)
            pole_start = max(0, i-10)
            pole = prices.iloc[pole_start:i]
            pole_change = (pole['c'].iloc[-1] - pole['c'].iloc[0]) / pole['c'].iloc[0]
            
            # Flag should have significant pole (>5% move)
            if abs(pole_change) < 0.05:
                continue
            
            # Check consolidation after pole
            flag = prices.iloc[i:min(i+10, len(prices))]
            flag_volatility = flag['c'].std() / flag['c'].mean()
            
            # Bull Flag: upward pole, slight downward consolidation
            if pole_change > 0.05 and flag_volatility < 0.02:
                flag_slope = (flag['c'].iloc[-1] - flag['c'].iloc[0]) / len(flag)
                if -0.001 < flag_slope < 0:
                    patterns['BULL_FLAG'].append((pole_start, i+len(flag)-1))
            
            # Bear Flag: downward pole, slight upward consolidation
            if pole_change < -0.05 and flag_volatility < 0.02:
                flag_slope = (flag['c'].iloc[-1] - flag['c'].iloc[0]) / len(flag)
                if 0 < flag_slope < 0.001:
                    patterns['BEAR_FLAG'].append((pole_start, i+len(flag)-1))
        
        return patterns
    
    def detect_channel_patterns(self, prices):
        """
        Detect channel patterns (ascending, descending, horizontal)
        """
        patterns = defaultdict(list)
        window_size = 20
        
        for i in range(window_size, len(prices)-window_size):
            window = prices.iloc[i-window_size:i]
            
            # Calculate upper and lower bounds
            highs = window['h'].rolling(5).max()
            lows = window['l'].rolling(5).min()
            
            # Fit lines to highs and lows
            x = np.arange(len(highs.dropna()))
            if len(x) < 10:
                continue
                
            high_slope = np.polyfit(x, highs.dropna().values, 1)[0]
            low_slope = np.polyfit(x, lows.dropna().values, 1)[0]
            
            # Check if slopes are parallel (within 20% of each other)
            if abs(high_slope - low_slope) < abs(high_slope) * 0.2:
                avg_slope = (high_slope + low_slope) / 2
                
                if avg_slope > 0.001:
                    patterns['ASCENDING_CHANNEL'].append((i-window_size, i))
                elif avg_slope < -0.001:
                    patterns['DESCENDING_CHANNEL'].append((i-window_size, i))
                else:
                    patterns['HORIZONTAL_CHANNEL'].append((i-window_size, i))
        
        return patterns
    
    def detect_cup_and_handle(self, prices, max_min):
        """
        Detect cup and handle pattern (bullish)
        """
        patterns = defaultdict(list)
        
        for i in range(30, len(prices)-10):
            cup_window = prices.iloc[i-30:i]
            
            # Check for U-shape (cup)
            mid_point = len(cup_window) // 2
            left_high = cup_window.iloc[:5]['c'].max()
            right_high = cup_window.iloc[-5:]['c'].max()
            bottom = cup_window.iloc[mid_point-5:mid_point+5]['c'].min()
            
            # Cup should have similar highs and lower middle
            if abs(left_high - right_high) < left_high * 0.05:
                if bottom < left_high * 0.85:
                    # Look for handle
                    handle = prices.iloc[i:min(i+10, len(prices))]
                    if len(handle) > 5:
                        handle_high = handle['c'].max()
                        handle_low = handle['c'].min()
                        
                        # Handle should be small retracement
                        if handle_low > right_high * 0.95 and handle_high < right_high * 1.02:
                            patterns['CUP_AND_HANDLE'].append((i-30, i+len(handle)-1))
        
        return patterns
    
    def detect_all_patterns(self, prices, max_min):
        """
        Detect all enhanced patterns
        """
        all_patterns = {}
        
        # Get triangle patterns
        triangle_patterns = self.detect_triangle_patterns(max_min, prices)
        all_patterns.update(triangle_patterns)
        
        # Get wedge patterns
        wedge_patterns = self.detect_wedge_patterns(max_min)
        all_patterns.update(wedge_patterns)
        
        # Get flag patterns
        flag_patterns = self.detect_flag_patterns(prices, max_min)
        all_patterns.update(flag_patterns)
        
        # Get channel patterns
        channel_patterns = self.detect_channel_patterns(prices)
        all_patterns.update(channel_patterns)
        
        # Get cup and handle
        cup_patterns = self.detect_cup_and_handle(prices, max_min)
        all_patterns.update(cup_patterns)
        
        return all_patterns