# 📈 Crypto Chart Patterns Detection

A Python-based tool for detecting and analyzing chart patterns in cryptocurrency markets using technical analysis.

## 🎯 Overview

This project implements pattern recognition algorithms to identify common chart patterns in cryptocurrency price data, including:
- **Inverse Head and Shoulders (IHS)** - Bullish reversal pattern
- **Double Top (DT)** - Bearish reversal pattern

The tool fetches real-time data from Binance API and uses local extrema detection to identify these patterns automatically.

## 🚀 Features

- Real-time cryptocurrency data fetching from Binance
- Automatic pattern detection using mathematical algorithms
- Visual pattern highlighting on price charts
- Forward return analysis for pattern validation
- Multiple timeframe support (1min, 5min, 1hour, etc.)
- Customizable pattern detection parameters

## 📋 Requirements

```bash
pandas
numpy
scipy 
matplotlib
tqdm 
ipython
ipykernel
requests
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/tysoncung/crypto-chart-patterns.git
cd crypto-chart-patterns
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Jupyter notebook:
```bash
jupyter notebook chart-patterns.ipynb
```

## 📊 Usage

### Basic Usage

```python
# Set the cryptocurrency pair
stock = "ETHUSDT"

# Fetch data from Binance
klines = get_data(stock)
prices = binance_to_df(klines)

# Detect patterns
min_max = get_max_min(prices, smoothing=3, window_range=3)
patterns = find_patterns(min_max)

# Visualize patterns
plot_minmax_patterns(prices, min_max, patterns, stock, window=10, ema=30)
```

### Pattern Detection Parameters

- **`smoothing`**: Moving average window for price smoothing (reduces noise)
- **`window_range`**: Range for local extrema detection
- **`ema_list`**: List of EMA periods to test [3, 10, 20, 30]
- **`window_list`**: List of window sizes to test [3, 10, 20, 30]

### Pattern Screening

Run a comprehensive pattern screen across multiple parameters:

```python
ema_list = [3, 10, 20, 30]
window_list = [3, 10, 20, 30]
results = screener(resampled_prices, ema_list, window_list, plot=True, results=True)
```

## 📈 Pattern Definitions

### Inverse Head and Shoulders (IHS)
- **Formation**: Three troughs with the middle one being the lowest
- **Condition**: `B > A > C; D > E > C`
- **Signal**: Bullish reversal pattern
- **Detection Logic**: `a<b and c<a and c<e and c<d and e<d`

### Double Top (DT)
- **Formation**: Two peaks at approximately the same level
- **Condition**: `A < C < B; D > C > E`
- **Signal**: Bearish reversal pattern
- **Detection Logic**: `a<c and c<b and c<d and c>e`

## 📉 Forward Returns Analysis

The tool calculates forward returns at different time intervals:
- 1 period forward return
- 12 periods forward return
- 24 periods forward return
- 36 periods forward return

This helps validate the predictive power of detected patterns.

## 🎨 Visualization

The tool provides two types of visualizations:
1. **Price chart with all local extrema** - Shows detected peaks and troughs
2. **Pattern overlay chart** - Highlights detected patterns on the price chart

## 🔧 Customization

### Adding New Patterns

To add a new pattern, modify the `find_patterns()` function:

```python
def find_patterns(max_min):  
    patterns = defaultdict(list)
    
    for i in range(5, len(max_min)):  
        window = max_min.iloc[i-5:i]
        a, b, c, d, e = window.iloc[0:5]
        
        # Add your pattern logic here
        if your_pattern_condition:
            patterns['YOUR_PATTERN'].append((window.index[0], window.index[-1]))
    
    return patterns
```

### Changing Data Source

Currently uses Binance API. To use another exchange:

```python
def get_data(stock):
    # Modify URL for your exchange's API
    url = f"YOUR_EXCHANGE_API_URL"
    r = requests.get(url)
    # Parse according to your exchange's format
    return data
```

## 📊 Performance Metrics

The screener provides average results grouped by:
- Window parameter
- EMA parameter
- Stock symbol
- Individual pattern performance

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