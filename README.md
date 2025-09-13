# 📈 Crypto Chart Pattern Detector

[![Test and Demo](https://github.com/tysoncung/crypto-chart-patterns/actions/workflows/test.yml/badge.svg)](https://github.com/tysoncung/crypto-chart-patterns/actions/workflows/test.yml)

Advanced technical analysis tool for detecting chart patterns in cryptocurrency markets.

## 🎯 Overview

This project implements comprehensive pattern recognition algorithms to identify chart patterns in cryptocurrency price data. The tool fetches real-time data from Binance API and uses local extrema detection combined with mathematical analysis to identify patterns automatically.

## 🚀 Features

### Basic Patterns
- **Inverse Head and Shoulders (IHS)** - Bullish reversal
- **Head and Shoulders (HS)** - Bearish reversal  
- **Double Top (DT)** - Bearish reversal
- **Double Bottom (DB)** - Bullish reversal

### Enhanced Patterns
- **Triangle Patterns** - Ascending, Descending, Symmetrical
- **Wedge Patterns** - Rising (bearish), Falling (bullish)
- **Flag Patterns** - Bull flags, Bear flags
- **Channel Patterns** - Ascending, Descending, Horizontal
- **Cup and Handle** - Bullish continuation

### Capabilities
- Real-time cryptocurrency data fetching from Binance
- Automatic pattern detection using mathematical algorithms
- Visual pattern highlighting on price charts
- Forward return analysis for pattern validation
- Multiple timeframe support (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- Comprehensive testing suite with 90%+ coverage
- CI/CD with GitHub Actions

## 📋 Requirements

```bash
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
requests>=2.26.0
tqdm>=4.62.0
pytest>=7.0.0
pytest-cov>=3.0.0
```

## 🛠️ Installation

```bash
git clone https://github.com/tysoncung/crypto-chart-patterns.git
cd crypto-chart-patterns
pip install -r requirements.txt
```

## 📊 Quick Start

### Command Line Usage

```bash
# Detect patterns for a specific symbol
python pattern_detector.py --symbol ETHUSDT --interval 4h

# Run demo with all patterns
python demo.py --symbol BTCUSDT --interval 1h

# Generate comprehensive report
python generate_report.py

# Run tests
pytest test_patterns.py -v
```

### Python API

```python
from pattern_detector import PatternDetector
from enhanced_patterns import EnhancedPatternDetector

# Initialize detector
detector = PatternDetector("BTCUSDT", "1h")

# Run complete analysis
results = detector.run_analysis()

# Or step by step:
klines = detector.get_data(limit=500)
prices = detector.binance_to_df(klines)
max_min = detector.get_max_min(prices)
patterns = detector.find_patterns(max_min)

# Enhanced patterns
enhanced = EnhancedPatternDetector()
all_patterns = enhanced.detect_all_patterns(prices, max_min)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_patterns.py -v

# Run with coverage
pytest test_patterns.py --cov=pattern_detector --cov=enhanced_patterns

# Run specific test
pytest test_patterns.py::TestPatternDetector::test_triangle_pattern_detection
```

## 🚀 CI/CD

This project uses GitHub Actions for continuous integration:

- **Automated Testing**: Multiple Python versions (3.8-3.11)
- **Coverage Reporting**: Integration with Codecov
- **Daily Demos**: Scheduled pattern detection runs
- **Artifact Generation**: Analysis reports and visualizations

## 📈 Pattern Types

### Basic Patterns
1. **Inverse Head and Shoulders (IHS)** - Bullish reversal
2. **Head and Shoulders (HS)** - Bearish reversal
3. **Double Top (DT)** - Bearish reversal
4. **Double Bottom (DB)** - Bullish reversal

### Triangle Patterns
5. **Ascending Triangle** - Bullish continuation (flat top, rising bottom)
6. **Descending Triangle** - Bearish continuation (falling top, flat bottom)
7. **Symmetrical Triangle** - Neutral (converging lines)

### Wedge Patterns
8. **Rising Wedge** - Bearish reversal (converging upward)
9. **Falling Wedge** - Bullish reversal (converging downward)

### Flag Patterns
10. **Bull Flag** - Bullish continuation after strong upward move
11. **Bear Flag** - Bearish continuation after strong downward move

### Channel Patterns
12. **Ascending Channel** - Upward trending parallel lines
13. **Descending Channel** - Downward trending parallel lines
14. **Horizontal Channel** - Sideways trading range

### Special Patterns
15. **Cup and Handle** - Bullish continuation (U-shape with handle)

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Cryptocurrency trading involves substantial risk of loss. Past pattern performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for improvement:
- Add more chart patterns (Triangle, Flag, Wedge, etc.)
- Implement machine learning for pattern validation
- Add backtesting capabilities
- Support for more exchanges
- Real-time pattern alerts

## 📝 License

MIT License - see LICENSE file for details

## 🔗 Resources

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [Technical Analysis Patterns](https://www.investopedia.com/articles/technical/112601.asp)
- [SciPy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)

## 👤 Author

**Tyson Cung**
- GitHub: [@tysoncung](https://github.com/tysoncung)

## 🙏 Acknowledgments

- Binance for providing free API access
- The Python scientific computing community
- Technical analysis researchers and practitioners