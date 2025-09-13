#!/usr/bin/env python3
"""
Generate comprehensive pattern detection report
"""

import json
import pandas as pd
from datetime import datetime
from pattern_detector import PatternDetector
from enhanced_patterns import EnhancedPatternDetector

def generate_report():
    """Generate comprehensive pattern analysis report"""
    
    print("Generating Pattern Detection Report...")
    
    # Symbols to analyze
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
    intervals = ['1h', '4h']
    
    report_data = []
    pattern_summary = {}
    
    for symbol in symbols:
        for interval in intervals:
            print(f"\nAnalyzing {symbol} ({interval})...")
            
            # Initialize detectors
            detector = PatternDetector(symbol, interval)
            enhanced = EnhancedPatternDetector()
            
            # Fetch and process data
            klines = detector.get_data(limit=500)
            if klines is None:
                continue
            
            prices = detector.binance_to_df(klines)
            max_min = detector.get_max_min(prices)
            
            # Detect patterns
            basic_patterns = detector.find_patterns(max_min)
            enhanced_patterns = enhanced.detect_all_patterns(prices, max_min)
            all_patterns = {**basic_patterns, **enhanced_patterns}
            
            # Calculate statistics
            total_patterns = sum(len(v) for v in all_patterns.values())
            
            # Store results
            entry = {
                'symbol': symbol,
                'interval': interval,
                'data_points': len(prices),
                'extrema_points': len(max_min),
                'total_patterns': total_patterns
            }
            
            # Add pattern counts
            for pattern_name in all_patterns:
                count = len(all_patterns[pattern_name])
                entry[f'pattern_{pattern_name}'] = count
                
                # Update summary
                if pattern_name not in pattern_summary:
                    pattern_summary[pattern_name] = 0
                pattern_summary[pattern_name] += count
            
            report_data.append(entry)
            print(f"  Found {total_patterns} patterns")
    
    # Create DataFrame
    df = pd.DataFrame(report_data)
    
    # Generate markdown report
    report = f"""# Crypto Chart Pattern Detection Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Symbols Analyzed**: {len(symbols)}
- **Intervals**: {', '.join(intervals)}
- **Total Patterns Detected**: {df['total_patterns'].sum()}

## Pattern Distribution

| Pattern Type | Total Occurrences |
|-------------|-------------------|
"""
    
    for pattern, count in sorted(pattern_summary.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            report += f"| {pattern} | {count} |\n"
    
    report += f"""

## Detailed Results by Symbol

| Symbol | Interval | Data Points | Extrema | Total Patterns |
|--------|----------|-------------|---------|----------------|
"""
    
    for _, row in df.iterrows():
        report += f"| {row['symbol']} | {row['interval']} | {row['data_points']} | {row['extrema_points']} | {row['total_patterns']} |\n"
    
    report += """

## Pattern Types Explained

### Basic Patterns
- **IHS** (Inverse Head and Shoulders): Bullish reversal pattern
- **HS** (Head and Shoulders): Bearish reversal pattern
- **DT** (Double Top): Bearish reversal pattern
- **DB** (Double Bottom): Bullish reversal pattern

### Enhanced Patterns
- **ASCENDING_TRIANGLE**: Bullish continuation pattern with flat top resistance
- **DESCENDING_TRIANGLE**: Bearish continuation pattern with flat bottom support
- **SYMMETRICAL_TRIANGLE**: Neutral pattern, breakout determines direction
- **RISING_WEDGE**: Bearish reversal pattern with converging upward trend
- **FALLING_WEDGE**: Bullish reversal pattern with converging downward trend
- **BULL_FLAG**: Bullish continuation after strong upward move
- **BEAR_FLAG**: Bearish continuation after strong downward move
- **ASCENDING_CHANNEL**: Upward trending parallel channel
- **DESCENDING_CHANNEL**: Downward trending parallel channel
- **HORIZONTAL_CHANNEL**: Sideways trading range
- **CUP_AND_HANDLE**: Bullish continuation pattern

## Notes
- Pattern detection uses local extrema with smoothing
- Returns are calculated for forward periods of 1, 5, 10, and 20 candles
- Data sourced from Binance API
"""
    
    # Save report
    with open('report.md', 'w') as f:
        f.write(report)
    print(f"\n✓ Report saved to report.md")
    
    # Save CSV
    df.to_csv('pattern_analysis.csv', index=False)
    print(f"✓ Data saved to pattern_analysis.csv")
    
    # Save JSON
    with open('pattern_summary.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'intervals': intervals,
            'pattern_summary': pattern_summary,
            'total_patterns': df['total_patterns'].sum()
        }, f, indent=2)
    print(f"✓ Summary saved to pattern_summary.json")

if __name__ == "__main__":
    generate_report()