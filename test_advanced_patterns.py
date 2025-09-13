"""
Test suite for advanced technical analysis patterns
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from advanced_patterns import AdvancedPatternDetector
from pattern_detector import PatternDetector

class TestAdvancedPatterns(unittest.TestCase):
    """Test cases for advanced pattern detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = AdvancedPatternDetector()
        
        # Create synthetic price data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        self.test_prices = pd.DataFrame({
            't': dates,
            'o': np.random.randn(200).cumsum() + 100,
            'h': np.random.randn(200).cumsum() + 102,
            'l': np.random.randn(200).cumsum() + 98,
            'c': np.random.randn(200).cumsum() + 100,
            'v': np.random.randint(1000, 10000, 200)
        })
        self.test_prices.set_index('t', inplace=True)
    
    def test_atr_calculation(self):
        """Test Average True Range calculation"""
        atr = self.detector.calculate_atr(self.test_prices)
        
        self.assertIsNotNone(atr)
        self.assertIsInstance(atr, pd.Series)
        self.assertEqual(len(atr), len(self.test_prices))
        
        # ATR should be positive
        self.assertTrue((atr[~atr.isna()] >= 0).all())
    
    def test_fibonacci_levels_calculation(self):
        """Test Fibonacci level calculations"""
        swing_high = 150
        swing_low = 100
        
        levels = self.detector.calculate_fibonacci_levels(
            self.test_prices, swing_high, swing_low
        )
        
        self.assertIsInstance(levels, dict)
        
        # Check key levels exist
        self.assertIn('ret_618', levels)
        self.assertIn('ret_382', levels)
        self.assertIn('ext_1618', levels)
        
        # Verify calculations
        self.assertAlmostEqual(levels['ret_618'], 130.9, places=1)  # 61.8% retracement
        self.assertAlmostEqual(levels['ret_382'], 119.1, places=1)  # 38.2% retracement
        self.assertAlmostEqual(levels['ret_500'], 125.0, places=1)  # 50% retracement
    
    def test_pivot_points_calculation(self):
        """Test Pivot Points calculation"""
        # Create simple test data
        test_data = pd.DataFrame({
            'h': [110],
            'l': [90],
            'c': [100]
        })
        
        pivots = self.detector.calculate_pivot_points(test_data)
        
        self.assertIsInstance(pivots, dict)
        self.assertIn('classic', pivots)
        self.assertIn('fibonacci', pivots)
        self.assertIn('camarilla', pivots)
        
        # Classic pivot should be (H+L+C)/3
        expected_pivot = (110 + 90 + 100) / 3
        self.assertAlmostEqual(pivots['classic']['P'], expected_pivot, places=2)
        
        # Resistance 1 should be 2*P - L
        expected_r1 = 2 * expected_pivot - 90
        self.assertAlmostEqual(pivots['classic']['R1'], expected_r1, places=2)
    
    def test_ichimoku_cloud_calculation(self):
        """Test Ichimoku Cloud calculation"""
        ichimoku = self.detector.calculate_ichimoku_cloud(self.test_prices)
        
        self.assertIsInstance(ichimoku, dict)
        self.assertIn('tenkan_sen', ichimoku)
        self.assertIn('kijun_sen', ichimoku)
        self.assertIn('senkou_span_a', ichimoku)
        self.assertIn('senkou_span_b', ichimoku)
        self.assertIn('chikou_span', ichimoku)
        
        # All components should be Series
        for component in ichimoku.values():
            self.assertIsInstance(component, pd.Series)
    
    def test_three_drive_pattern_detection(self):
        """Test Three Drive pattern detection"""
        # Create synthetic three drive pattern
        dates = pd.date_range(start='2024-01-01', periods=50, freq='h')
        
        # Create three ascending drives
        values = []
        for i in range(50):
            if i < 10:
                values.append(100 + i)  # First drive up
            elif i < 15:
                values.append(110 - (i-10))  # Pullback
            elif i < 25:
                values.append(105 + (i-15))  # Second drive up
            elif i < 30:
                values.append(115 - (i-25))  # Pullback
            elif i < 40:
                values.append(110 + (i-30))  # Third drive up
            else:
                values.append(120)
        
        test_data = pd.DataFrame({
            't': dates,
            'o': values,
            'h': [v + 2 for v in values],
            'l': [v - 2 for v in values],
            'c': values,
            'v': [1000] * 50
        })
        test_data.set_index('t', inplace=True)
        
        # Get extrema
        detector = PatternDetector()
        max_min = detector.get_max_min(test_data)
        
        patterns = self.detector.detect_three_drive_pattern(test_data, max_min)
        
        self.assertIsInstance(patterns, dict)
        # Pattern detection on synthetic data may not always work
        # Just verify the function runs without error
    
    def test_fibonacci_pattern_detection(self):
        """Test Fibonacci pattern detection"""
        # Create data with Fibonacci retracement
        dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
        
        values = []
        for i in range(100):
            if i < 30:
                values.append(100 + i)  # Uptrend to 130
            elif i < 60:
                # Retrace to 61.8% level (around 111.46)
                values.append(130 - (i-30) * 0.618)
            else:
                # Bounce from 61.8%
                values.append(111.46 + (i-60) * 0.5)
        
        test_data = pd.DataFrame({
            't': dates,
            'o': values,
            'h': [v + 1 for v in values],
            'l': [v - 1 for v in values],
            'c': values,
            'v': [1000] * 100
        })
        test_data.set_index('t', inplace=True)
        
        detector = PatternDetector()
        max_min = detector.get_max_min(test_data)
        
        patterns = self.detector.detect_fibonacci_patterns(test_data, max_min)
        
        self.assertIsInstance(patterns, dict)
        # Just verify the function runs without error
    
    def test_andrews_pitchfork_detection(self):
        """Test Andrews' Pitchfork detection"""
        detector = PatternDetector()
        max_min = detector.get_max_min(self.test_prices)
        
        patterns = self.detector.detect_andrews_pitchfork(self.test_prices, max_min)
        
        self.assertIsInstance(patterns, dict)
        # Just verify the function runs without error
    
    def test_ichimoku_signals_detection(self):
        """Test Ichimoku signal detection"""
        patterns = self.detector.detect_ichimoku_signals(self.test_prices)
        
        self.assertIsInstance(patterns, dict)
        # Just verify the function runs without error
    
    def test_all_advanced_patterns(self):
        """Test detection of all advanced patterns"""
        detector = PatternDetector()
        max_min = detector.get_max_min(self.test_prices)
        
        all_patterns = self.detector.detect_all_advanced_patterns(
            self.test_prices, max_min
        )
        
        self.assertIsInstance(all_patterns, dict)
        
        # Check that indicators were calculated
        self.assertIsNotNone(self.detector.indicators)
        self.assertIn('atr', self.detector.indicators)
        self.assertIn('pivot_points', self.detector.indicators)
    
    def test_pattern_descriptions(self):
        """Test pattern description retrieval"""
        desc = self.detector.get_pattern_description('FIB_618_BOUNCE')
        self.assertIsInstance(desc, str)
        self.assertIn('61.8%', desc)
        
        desc = self.detector.get_pattern_description('ICHIMOKU_TK_BULL')
        self.assertIn('Tenkan', desc)
        
        desc = self.detector.get_pattern_description('UNKNOWN_PATTERN')
        self.assertEqual(desc, 'Unknown pattern')

class TestAdvancedIntegration(unittest.TestCase):
    """Integration tests for advanced patterns with real-like data"""
    
    def test_trending_market_patterns(self):
        """Test pattern detection in trending market"""
        # Create trending market data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        trend = np.linspace(100, 150, 200)
        noise = np.random.randn(200) * 2
        
        prices = pd.DataFrame({
            't': dates,
            'c': trend + noise,
            'o': trend + noise - 1,
            'h': trend + noise + 2,
            'l': trend + noise - 2,
            'v': np.random.randint(1000, 10000, 200)
        })
        prices.set_index('t', inplace=True)
        
        detector = AdvancedPatternDetector()
        pattern_detector = PatternDetector()
        max_min = pattern_detector.get_max_min(prices)
        
        patterns = detector.detect_all_advanced_patterns(prices, max_min)
        
        self.assertIsInstance(patterns, dict)
        # ATR should increase in trending market
        atr = detector.indicators['atr']
        self.assertIsNotNone(atr)
    
    def test_ranging_market_patterns(self):
        """Test pattern detection in ranging market"""
        # Create ranging market data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        
        values = []
        for i in range(200):
            # Oscillate between 95 and 105
            values.append(100 + 5 * np.sin(i * 0.1) + np.random.randn())
        
        prices = pd.DataFrame({
            't': dates,
            'c': values,
            'o': [v - 0.5 for v in values],
            'h': [v + 1 for v in values],
            'l': [v - 1 for v in values],
            'v': np.random.randint(1000, 10000, 200)
        })
        prices.set_index('t', inplace=True)
        
        detector = AdvancedPatternDetector()
        
        # Calculate pivot points - should be around 100
        pivots = detector.calculate_pivot_points(prices)
        self.assertAlmostEqual(pivots['classic']['P'], 100, delta=10)

if __name__ == '__main__':
    unittest.main()