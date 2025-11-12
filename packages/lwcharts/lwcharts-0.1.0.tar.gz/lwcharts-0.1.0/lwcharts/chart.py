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

    def __init__(self, chart_type='line', width=800, height=400):
        """
        Create a new chart.

        Args:
            chart_type: Type of chart ('line', 'candlestick', 'area', 'histogram', 'bar')
            width: Chart width in pixels
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

    def _repr_html_(self):
        """Return HTML representation for Jupyter display"""
        chart_id = f"lwc-{random.randint(10000, 99999)}"
        data_json = json.dumps(self.data)
        series_options_json = json.dumps(self._get_series_options())

        chart_opts = {
            'width': self.width,
            'height': self.height,
            **self.chart_options
        }
        chart_options_json = json.dumps(chart_opts)

        html = f"""
<div id="{chart_id}" style="width: {self.width}px; height: {self.height}px; border: 1px solid #ddd;"></div>

<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>

<script>
(function() {{
    const container = document.getElementById('{chart_id}');
    if (!container) return;

    const chartOptions = {chart_options_json};
    const chart = LightweightCharts.createChart(container, chartOptions);

    const seriesOptions = {series_options_json};
    const series = chart.{self._get_series_method()}(seriesOptions);

    const data = {data_json};
    series.setData(data);

    chart.timeScale().fitContent();
}})();
</script>
"""
        return html

    def display(self):
        """Explicitly display the chart"""
        display(HTML(self._repr_html_()))

    def set_data(self, data):
        """Set chart data"""
        self.data = data

    def add_data_point(self, point):
        """Add a single data point"""
        self.data.append(point)
