"""
Simple Chart class that renders lightweight-charts using inline HTML/JavaScript
"""

from IPython.display import HTML, display
import json
import random


class Chart:
    """
    Simple lightweight-charts wrapper that renders charts inline using HTML/JS.
    No widget infrastructure required - just pure HTML rendering.
    """

    def __init__(self, chart_type='candlestick', width='100%', height=400):
        """
        Create a new chart.

        Args:
            chart_type: Type of chart ('candlestick', 'line', 'area', 'histogram', 'bar')
            width: Chart width in pixels or '100%' for full width (default: '100%')
            height: Chart height in pixels
        """
        self.chart_type = chart_type
        self.width = width
        self.height = height
        self.data = []
        self.chart_options = {
            'layout': {
                'background': {'color': '#FFFFFF'},
                'textColor': '#333',
            },
            'grid': {
                'vertLines': {'color': '#f0f0f0'},
                'horzLines': {'color': '#f0f0f0'},
            },
            'rightPriceScale': {
                'visible': True,
                'borderVisible': True,
                'scaleMargins': {
                    'top': 0.15,
                    'bottom': 0.15,
                },
            },
            'timeScale': {
                'visible': True,
                'borderVisible': True,
                'timeVisible': True,
                'secondsVisible': False,
                'rightOffset': 10,
                'barSpacing': 10,
                'minBarSpacing': 0.5,
                'minimumHeight': 40,
                'fixLeftEdge': True,
                'fixRightEdge': True,
            },
        }
        self.series_options = {}

    def _get_series_options(self):
        """Get default series options based on chart type"""
        defaults = {
            'line': {
                'color': '#2962FF',
                'lineWidth': 2,
            },
            'area': {
                'lineColor': '#2962FF',
                'topColor': 'rgba(41, 98, 255, 0.4)',
                'bottomColor': 'rgba(41, 98, 255, 0.0)',
            },
            'candlestick': {
                'upColor': '#26a69a',
                'downColor': '#ef5350',
                'borderVisible': False,
                'wickUpColor': '#26a69a',
                'wickDownColor': '#ef5350',
            },
            'histogram': {
                'color': '#26a69a',
            },
            'bar': {
                'upColor': '#26a69a',
                'downColor': '#ef5350',
            },
        }

        options = defaults.get(self.chart_type, {})
        options.update(self.series_options)
        return options

    def _get_series_method(self):
        """Get the chart series method name"""
        methods = {
            'line': 'addLineSeries',
            'area': 'addAreaSeries',
            'candlestick': 'addCandlestickSeries',
            'histogram': 'addHistogramSeries',
            'bar': 'addBarSeries',
        }
        return methods.get(self.chart_type, 'addLineSeries')

    def _calculate_price_scale_width(self):
        """Calculate appropriate minimum width for price scale based on data"""
        if not self.data:
            return 100

        max_val = 0
        max_decimals = 0

        for point in self.data:
            # Handle different data formats (line: 'value', candlestick: 'high', etc.)
            values = []
            if isinstance(point, dict):
                if 'value' in point:
                    values.append(point['value'])
                if 'high' in point:
                    values.extend([point.get('high', 0), point.get('low', 0)])

            for val in values:
                max_val = max(max_val, abs(val))

                # Count actual decimal places in the data
                val_str = str(val)
                if '.' in val_str:
                    decimals = len(val_str.split('.')[1])
                    max_decimals = max(max_decimals, decimals)

        # If no decimals found, use defaults based on magnitude
        if max_decimals == 0:
            if max_val < 1:
                max_decimals = 6
            elif max_val < 100:
                max_decimals = 5
            else:
                max_decimals = 2

        # Format the largest value with actual decimal places to measure width
        example_str = f"{max_val:,.{max_decimals}f}"
        char_count = len(example_str)

        # Very generous estimate: 15px per character + 70px padding for margins/internal spacing
        # The chart library adds significant internal padding that we need to account for
        estimated_width = char_count * 15 + 70

        # Ensure reasonable bounds: 120px minimum, 350px maximum
        return max(120, min(350, estimated_width))

    def _repr_html_(self):
        """Return HTML representation for Jupyter display"""
        chart_id = f"lwc-{random.randint(10000, 99999)}"
        data_json = json.dumps(self.data)
        series_options_json = json.dumps(self._get_series_options())

        # Calculate appropriate price scale width
        price_scale_width = self._calculate_price_scale_width()

        # Update chart options with calculated width
        chart_options = self.chart_options.copy()

        # Ensure rightPriceScale exists (user might have overridden chart_options)
        if 'rightPriceScale' not in chart_options:
            chart_options['rightPriceScale'] = {}

        chart_options['rightPriceScale'] = {
            **chart_options.get('rightPriceScale', {}),
            'minimumWidth': price_scale_width
        }

        chart_options_json = json.dumps(chart_options)

        # Determine if width is percentage or pixel value
        width_style = self.width if isinstance(self.width, str) and '%' in self.width else f"{self.width}px"
        height_style = f"{self.height}px"

        html = f"""
<div id="{chart_id}" style="width: {width_style}; height: {height_style}; position: relative;"></div>

<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>

<script>
(function() {{
    const container = document.getElementById('{chart_id}');
    if (!container) return;

    const chartOptions = {{
        ...{chart_options_json},
        autoSize: true
    }};

    const chart = LightweightCharts.createChart(container, chartOptions);

    const seriesOptions = {series_options_json};
    const series = chart.{self._get_series_method()}(seriesOptions);

    const data = {data_json};
    series.setData(data);

    // Fit content to show all data
    chart.timeScale().fitContent();
}})();
</script>
"""
        return html

    def _convert_dataframe(self, df):
        """
        Convert pandas DataFrame to chart data format.

        Args:
            df: pandas DataFrame with columns:
                - For candlestick/bar: 'time', 'open', 'high', 'low', 'close'
                - For line/area: 'time', 'value'
                - For histogram: 'time', 'value', optional 'color'

        Returns:
            List of dictionaries in lightweight-charts format
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for DataFrame support. Install with: pip install pandas")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        # Determine required columns based on chart type
        if self.chart_type in ['candlestick', 'bar']:
            required_cols = ['open', 'high', 'low', 'close']
        elif self.chart_type in ['line', 'area', 'histogram']:
            required_cols = ['value']
        else:
            required_cols = ['value']

        # Check for time column
        time_col = None
        for col in ['time', 'timestamp', 'date', 'datetime']:
            if col in df.columns:
                time_col = col
                break

        if time_col is None and df.index.name in ['time', 'timestamp', 'date', 'datetime']:
            # Use index as time
            df = df.reset_index()
            time_col = df.columns[0]
        elif time_col is None:
            # Use index as time
            df = df.reset_index()
            time_col = df.columns[0]

        # Verify required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns for {self.chart_type} chart: {missing_cols}")

        # Convert DataFrame to list of dicts
        chart_data = []
        for idx, row in df.iterrows():
            point = {}

            # Handle time conversion
            time_val = row[time_col]

            # Check if it's a pandas Timestamp or datetime object
            if hasattr(time_val, 'timestamp'):
                # It's a datetime-like object (pandas Timestamp, datetime, etc.)
                if hasattr(time_val, 'hour') and time_val.hour == 0 and time_val.minute == 0 and time_val.second == 0:
                    # Daily data - use string format
                    point['time'] = time_val.strftime('%Y-%m-%d')
                else:
                    # Intraday data - use Unix timestamp
                    point['time'] = int(time_val.timestamp())
            elif isinstance(time_val, str):
                # Already a string
                point['time'] = time_val
            elif isinstance(time_val, (int, float)):
                # Numeric timestamp
                point['time'] = int(time_val)
            else:
                # Fallback - convert to string
                point['time'] = str(time_val)

            # Add price data
            for col in required_cols:
                point[col] = float(row[col])

            # Add optional color for histogram
            if self.chart_type == 'histogram' and 'color' in df.columns:
                point['color'] = row['color']

            chart_data.append(point)

        return chart_data

    def display(self):
        """Explicitly display the chart"""
        display(HTML(self._repr_html_()))

    def set_data(self, data):
        """
        Set chart data from list or pandas DataFrame.

        Args:
            data: Either a list of dictionaries or a pandas DataFrame

                  For list format:
                  - Candlestick/Bar: [{'time': '2025-01-01', 'open': 100, 'high': 105, 'low': 98, 'close': 102}, ...]
                  - Line/Area: [{'time': '2025-01-01', 'value': 100}, ...]
                  - Histogram: [{'time': '2025-01-01', 'value': 100, 'color': '#26a69a'}, ...]

                  For DataFrame format:
                  - Must have a time column (or datetime index)
                  - Candlestick/Bar: columns 'open', 'high', 'low', 'close'
                  - Line/Area: column 'value'
                  - Time column will be auto-detected from: 'time', 'timestamp', 'date', 'datetime', or index
                  - Timestamps are automatically converted (daily data → string, intraday → Unix timestamp)

        Examples:
            # From list
            chart.set_data([{'time': '2025-01-01', 'value': 100}, ...])

            # From DataFrame
            df = pd.DataFrame({
                'time': pd.date_range('2025-01-01', periods=100, freq='1h'),
                'open': [...],
                'high': [...],
                'low': [...],
                'close': [...]
            })
            chart.set_data(df)
        """
        # Check if data is a DataFrame
        try:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                self.data = self._convert_dataframe(data)
                return
        except ImportError:
            pass

        # Otherwise treat as list
        self.data = data

    def add_data_point(self, point):
        """Add a single data point"""
        self.data.append(point)
