#!/usr/bin/env python3
"""
Demo script for crypto chart pattern detection
Shows how to use the pattern detector and enhanced patterns
"""

import json
import argparse
import pandas as pd
from datetime import datetime
from pattern_detector import PatternDetector
from enhanced_patterns import EnhancedPatternDetector
from advanced_patterns import AdvancedPatternDetector

def run_demo(symbol="BTCUSDT", interval="1h", save_results=True, plot=True):
    """
    Run pattern detection demo
    
    Args:
        symbol: Trading pair symbol
        interval: Time interval
        save_results: Whether to save results to file
        plot: Whether to generate plots
    """
    print(f"\n{'='*60}")
    print(f"Pattern Detection Demo - {symbol} ({interval})")
    print(f"{'='*60}\n")
    
    # Initialize detectors
    detector = PatternDetector(symbol, interval)
    enhanced = EnhancedPatternDetector()
    advanced = AdvancedPatternDetector()
    
    # Fetch data
    print("1. Fetching market data...")
    klines = detector.get_data(limit=500)
    if klines is None:
        print("Failed to fetch data")
        return None
    
    prices = detector.binance_to_df(klines)
    print(f"   ✓ Fetched {len(prices)} candles")
    
    # Find extrema
    print("\n2. Finding local extrema...")
    max_min = detector.get_max_min(prices)
    print(f"   ✓ Found {len(max_min)} extrema points")
    
    # Detect basic patterns
    print("\n3. Detecting basic patterns...")
    basic_patterns = detector.find_patterns(max_min)
    print("   Basic patterns found:")
    for pattern, occurrences in basic_patterns.items():
        if occurrences:
            print(f"   • {pattern}: {len(occurrences)} occurrences")
    
    # Detect enhanced patterns
    print("\n4. Detecting enhanced patterns...")
    enhanced_patterns = enhanced.detect_all_patterns(prices, max_min)
    print("   Enhanced patterns found:")
    for pattern, occurrences in enhanced_patterns.items():
        if occurrences:
            print(f"   • {pattern}: {len(occurrences)} occurrences")
    
    # Detect advanced patterns
    print("\n5. Detecting advanced patterns...")
    advanced_patterns = advanced.detect_all_advanced_patterns(prices, max_min)
    print("   Advanced patterns found:")
    for pattern, occurrences in advanced_patterns.items():
        if occurrences:
            desc = advanced.get_pattern_description(pattern)
            print(f"   • {pattern}: {len(occurrences)} occurrences")
            print(f"     {desc}")
    
    # Show indicators
    if hasattr(advanced, 'indicators'):
        print("\n6. Technical Indicators:")
        if 'atr' in advanced.indicators:
            current_atr = advanced.indicators['atr'].iloc[-1]
            if not pd.isna(current_atr):
                print(f"   • ATR (14): {current_atr:.2f}")
        
        if 'pivot_points' in advanced.indicators:
            pivots = advanced.indicators['pivot_points']['classic']
            print(f"   • Pivot Point: {pivots['P']:.2f}")
            print(f"   • Resistance 1: {pivots['R1']:.2f}")
            print(f"   • Support 1: {pivots['S1']:.2f}")
    
    # Calculate returns
    print("\n7. Calculating pattern returns...")
    all_patterns = {**basic_patterns, **enhanced_patterns}
    if any(all_patterns.values()):
        returns = detector.calculate_returns(prices, all_patterns)
        
        # Display average returns
        print("\n   Average returns by pattern:")
        for pattern in all_patterns:
            if all_patterns[pattern]:
                pattern_returns = returns[returns['pattern'] == pattern]
                if not pattern_returns.empty:
                    avg_1p = pattern_returns['return_1p'].mean()
                    avg_5p = pattern_returns['return_5p'].mean()
                    avg_10p = pattern_returns['return_10p'].mean()
                    print(f"   • {pattern}:")
                    print(f"     - 1 period: {avg_1p:.2f}%")
                    print(f"     - 5 periods: {avg_5p:.2f}%")
                    print(f"     - 10 periods: {avg_10p:.2f}%")
    
    # Save results
    if save_results:
        results = {
            'symbol': symbol,
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'data_points': len(prices),
            'extrema_points': len(max_min),
            'patterns': {
                'basic': {k: len(v) for k, v in basic_patterns.items()},
                'enhanced': {k: len(v) for k, v in enhanced_patterns.items()}
            },
            'total_patterns': sum(len(v) for v in all_patterns.values())
        }
        
        filename = f"{symbol}_{interval}_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n   ✓ Results saved to {filename}")
    
    # Plot if requested
    if plot and any(all_patterns.values()):
        print("\n8. Generating visualization...")
        detector.plot_patterns(prices, max_min, all_patterns, save=True)
    
    print(f"\n{'='*60}")
    print("Demo completed successfully!")
    print(f"{'='*60}\n")
    
    return all_patterns

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Demo crypto chart pattern detection')
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair symbol')
    parser.add_argument('--interval', default='1h', help='Time interval')
    parser.add_argument('--no-save', action='store_true', help='Do not save results')
    parser.add_argument('--no-plot', action='store_true', help='Do not generate plots')
    
    args = parser.parse_args()
    
    run_demo(
        symbol=args.symbol,
        interval=args.interval,
        save_results=not args.no_save,
        plot=not args.no_plot
    )

if __name__ == "__main__":
    main()