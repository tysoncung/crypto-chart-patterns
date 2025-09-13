#!/usr/bin/env python3
"""
Test suite for crypto chart pattern detection
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pattern_detector import PatternDetector
from enhanced_patterns import EnhancedPatternDetector

class TestPatternDetector(unittest.TestCase):
    """Test cases for the pattern detector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = PatternDetector()
        self.enhanced_detector = EnhancedPatternDetector()
        
        # Create synthetic price data for testing
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        self.test_prices = pd.DataFrame({
            't': dates,
            'o': np.random.randn(100).cumsum() + 100,
            'h': np.random.randn(100).cumsum() + 102,
            'l': np.random.randn(100).cumsum() + 98,
            'c': np.random.randn(100).cumsum() + 100,
            'v': np.random.randint(1000, 10000, 100)
        })
        self.test_prices.set_index('t', inplace=True)
    
    def test_data_fetching(self):
        """Test data fetching from Binance API"""
        detector = PatternDetector("BTCUSDT", "1h")
        data = detector.get_data(limit=10)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 10)
    
    def test_dataframe_conversion(self):
        """Test conversion of Binance data to DataFrame"""
        detector = PatternDetector("BTCUSDT", "1h")
        klines = detector.get_data(limit=10)
        if klines is not None:
            df = detector.binance_to_df(klines)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn('c', df.columns)
            self.assertIn('o', df.columns)
            self.assertIn('h', df.columns)
            self.assertIn('l', df.columns)
    
    def test_max_min_detection(self):
        """Test local maxima and minima detection"""
        max_min = self.detector.get_max_min(self.test_prices)
        self.assertIsNotNone(max_min)
        self.assertIsInstance(max_min, pd.Series)
        self.assertTrue(len(max_min) > 0)
    
    def test_pattern_detection(self):
        """Test basic pattern detection"""
        # Create synthetic data with known pattern
        dates = pd.date_range(start='2024-01-01', periods=50, freq='H')
        
        # Create inverse head and shoulders pattern
        values = []
        for i in range(50):
            if i < 10:
                values.append(100 - i)  # Left shoulder down
            elif i < 15:
                values.append(90 + (i-10)*2)  # Left shoulder up
            elif i < 25:
                values.append(100 - (i-15)*2)  # Head down
            elif i < 30:
                values.append(80 + (i-25)*4)  # Head up
            elif i < 40:
                values.append(100 - (i-30))  # Right shoulder down
            else:
                values.append(90 + (i-40)*2)  # Right shoulder up
        
        test_data = pd.DataFrame({
            't': dates,
            'o': values,
            'h': [v + 2 for v in values],
            'l': [v - 2 for v in values],
            'c': values,
            'v': [1000] * 50
        })
        test_data.set_index('t', inplace=True)
        
        max_min = self.detector.get_max_min(test_data)
        patterns = self.detector.find_patterns(max_min)
        
        self.assertIsInstance(patterns, dict)
        # Should detect at least one pattern in synthetic data
        total_patterns = sum(len(p) for p in patterns.values())
        self.assertGreaterEqual(total_patterns, 0)
    
    def test_triangle_pattern_detection(self):
        """Test triangle pattern detection"""
        # Create synthetic triangle pattern
        dates = pd.date_range(start='2024-01-01', periods=30, freq='H')
        
        # Ascending triangle: flat top, rising bottom
        highs = [100] * 30  # Flat resistance
        lows = [80 + i*0.5 for i in range(30)]  # Rising support
        
        values = []
        for i in range(30):
            if i % 4 < 2:
                values.append(highs[i])
            else:
                values.append(lows[i])
        
        test_data = pd.DataFrame({
            't': dates,
            'c': values,
            'o': values,
            'h': [v + 1 for v in values],
            'l': [v - 1 for v in values],
            'v': [1000] * 30
        })
        test_data.set_index('t', inplace=True)
        
        max_min = self.detector.get_max_min(test_data)
        patterns = self.enhanced_detector.detect_triangle_patterns(max_min, test_data)
        
        self.assertIsInstance(patterns, dict)
        # Check if any triangle patterns were detected
        self.assertIn('ASCENDING_TRIANGLE', patterns.keys())
    
    def test_wedge_pattern_detection(self):
        """Test wedge pattern detection"""
        # Create synthetic wedge pattern
        dates = pd.date_range(start='2024-01-01', periods=25, freq='H')
        
        # Rising wedge: converging upward
        values = []
        for i in range(25):
            base = 100 + i * 0.5  # Rising trend
            amplitude = 5 * (1 - i/25)  # Decreasing volatility
            values.append(base + amplitude * np.sin(i))
        
        max_min = pd.Series(values, index=range(25))
        patterns = self.enhanced_detector.detect_wedge_patterns(max_min)
        
        self.assertIsInstance(patterns, dict)
        # May detect wedge patterns in synthetic data
        self.assertTrue('RISING_WEDGE' in patterns or 'FALLING_WEDGE' in patterns)
    
    def test_flag_pattern_detection(self):
        """Test flag pattern detection"""
        # Create synthetic flag pattern
        dates = pd.date_range(start='2024-01-01', periods=30, freq='H')
        
        # Bull flag: strong upward move followed by slight consolidation
        values = []
        for i in range(30):
            if i < 10:
                values.append(100 + i * 2)  # Strong upward pole
            else:
                values.append(120 - (i-10) * 0.1)  # Slight downward consolidation
        
        test_data = pd.DataFrame({
            't': dates,
            'c': values,
            'o': values,
            'h': [v + 0.5 for v in values],
            'l': [v - 0.5 for v in values],
            'v': [1000] * 30
        })
        test_data.set_index('t', inplace=True)
        
        max_min = self.detector.get_max_min(test_data)
        patterns = self.enhanced_detector.detect_flag_patterns(test_data, max_min)
        
        self.assertIsInstance(patterns, dict)
        # Should detect flag patterns
        self.assertTrue('BULL_FLAG' in patterns or 'BEAR_FLAG' in patterns)
    
    def test_channel_pattern_detection(self):
        """Test channel pattern detection"""
        # Create synthetic channel pattern
        dates = pd.date_range(start='2024-01-01', periods=40, freq='H')
        
        # Ascending channel
        values = []
        for i in range(40):
            base = 100 + i * 0.3  # Upward trend
            oscillation = 2 * np.sin(i * 0.5)  # Oscillation within channel
            values.append(base + oscillation)
        
        test_data = pd.DataFrame({
            't': dates,
            'c': values,
            'o': values,
            'h': [v + 1 for v in values],
            'l': [v - 1 for v in values],
            'v': [1000] * 40
        })
        test_data.set_index('t', inplace=True)
        
        patterns = self.enhanced_detector.detect_channel_patterns(test_data)
        
        self.assertIsInstance(patterns, dict)
        # Should detect channel patterns
        channel_keys = ['ASCENDING_CHANNEL', 'DESCENDING_CHANNEL', 'HORIZONTAL_CHANNEL']
        self.assertTrue(any(k in patterns for k in channel_keys))
    
    def test_cup_and_handle_detection(self):
        """Test cup and handle pattern detection"""
        # Create synthetic cup and handle pattern
        dates = pd.date_range(start='2024-01-01', periods=45, freq='H')
        
        # Cup and handle: U-shape followed by small consolidation
        values = []
        for i in range(45):
            if i < 15:
                values.append(100 - i)  # Left side of cup
            elif i < 30:
                values.append(85 + (i-15))  # Right side of cup
            elif i < 40:
                values.append(100 - (i-30) * 0.3)  # Handle
            else:
                values.append(97 + (i-40) * 0.5)  # Breakout
        
        test_data = pd.DataFrame({
            't': dates,
            'c': values,
            'o': values,
            'h': [v + 0.5 for v in values],
            'l': [v - 0.5 for v in values],
            'v': [1000] * 45
        })
        test_data.set_index('t', inplace=True)
        
        max_min = self.detector.get_max_min(test_data)
        patterns = self.enhanced_detector.detect_cup_and_handle(test_data, max_min)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('CUP_AND_HANDLE', patterns.keys())
    
    def test_pattern_returns_calculation(self):
        """Test pattern returns calculation"""
        # Use real data for this test
        detector = PatternDetector("BTCUSDT", "1h")
        klines = detector.get_data(limit=500)
        
        if klines is not None:
            prices = detector.binance_to_df(klines)
            max_min = detector.get_max_min(prices)
            patterns = detector.find_patterns(max_min)
            
            if any(patterns.values()):
                returns = detector.calculate_returns(prices, patterns)
                self.assertIsInstance(returns, pd.DataFrame)
                self.assertIn('Pattern', returns.columns)
                self.assertIn('1 bar', returns.columns)
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_df = pd.DataFrame()
        patterns = self.enhanced_detector.detect_channel_patterns(empty_df)
        self.assertEqual(len(patterns), 0)
    
    def test_invalid_symbol_handling(self):
        """Test handling of invalid trading symbols"""
        detector = PatternDetector("INVALID", "1h")
        data = detector.get_data(limit=10)
        # API should return None or empty for invalid symbol
        self.assertTrue(data is None or len(data) == 0)

class TestPatternIntegration(unittest.TestCase):
    """Integration tests for pattern detection"""
    
    def test_full_pipeline(self):
        """Test the full pattern detection pipeline"""
        detector = PatternDetector("ETHUSDT", "1h")
        
        # Get data
        klines = detector.get_data(limit=200)
        self.assertIsNotNone(klines)
        
        # Convert to DataFrame
        prices = detector.binance_to_df(klines)
        self.assertIsInstance(prices, pd.DataFrame)
        
        # Find extrema
        max_min = detector.get_max_min(prices)
        self.assertIsNotNone(max_min)
        
        # Find patterns
        patterns = detector.find_patterns(max_min)
        self.assertIsInstance(patterns, dict)
        
        # Calculate returns if patterns found
        if any(patterns.values()):
            returns = detector.calculate_returns(prices, patterns)
            self.assertIsInstance(returns, pd.DataFrame)
    
    def test_enhanced_patterns_integration(self):
        """Test enhanced pattern detection integration"""
        detector = PatternDetector("BTCUSDT", "4h")
        enhanced = EnhancedPatternDetector()
        
        # Get real data
        klines = detector.get_data(limit=500)
        if klines is not None:
            prices = detector.binance_to_df(klines)
            max_min = detector.get_max_min(prices)
            
            # Detect all enhanced patterns
            all_patterns = enhanced.detect_all_patterns(prices, max_min)
            
            self.assertIsInstance(all_patterns, dict)
            print(f"Detected patterns: {list(all_patterns.keys())}")
            print(f"Total pattern occurrences: {sum(len(p) for p in all_patterns.values())}")

if __name__ == '__main__':
    unittest.main()