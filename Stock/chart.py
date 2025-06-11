from datetime import datetime
from io import BytesIO
from typing import Optional

import matplotlib.pyplot as plt
import mplfinance as mpf
from PIL import Image
from Stock.data import StockData


class StockChart:
    def __init__(self, analyzer: StockData):
        self.analyzer = analyzer
        self.fig = None
        self.ax = None

    def create_base_chart(self) -> None:
        """Create the base candlestick chart with moving averages"""
        add_plots = [
            mpf.make_addplot(self.analyzer.data['SMA_1'], color='blue', width=0.2),
            mpf.make_addplot(self.analyzer.data['SMA_20'], color='green', width=1.0),
            mpf.make_addplot(self.analyzer.data['SMA_94'], color='red', width=1.0)
        ]
        
        self.fig, axlist = mpf.plot(
            self.analyzer.data,
            type='candle',
            style='yahoo',
            addplot=add_plots,
            title=f'{self.analyzer.ticker} Chart ({self.analyzer.period_days}d, {self.analyzer.interval}) - Gaps & Key Levels',
            ylabel='',
            figsize=(20, 10),
            returnfig=True
        )
        
        self.ax = axlist[0]
        self._add_current_price_info()

    def _add_current_price_info(self) -> None:
        """Add current price and timestamp to chart"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_price = self.analyzer.data['Close'].iloc[-1]
        self.ax.text(
            0.98, 0.98,
            f"As of: {current_time} | Price: ${current_price:.2f}",
            transform=self.ax.transAxes,
            ha='right', va='top',
            color='gray',
            fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )

    def plot_gaps(self) -> None:
        """Visualize gaps on the chart"""
        y_min, y_max = self.ax.get_ylim()
        y_range = y_max - y_min
        
        for gap in self.analyzer.gaps:
            # Calculate normalized y-coordinates
            y_from = (gap.gap_from - y_min) / y_range
            y_to = (gap.gap_to - y_min) / y_range
            
            # Draw gap rectangle
            self.ax.axvspan(
                gap.index - 0.5, gap.index + 0.5,
                ymin=y_from,
                ymax=y_to,
                facecolor='none',
                alpha=0.3 if gap.filled else 0.6,
                edgecolor='none'
            )
            
            # Add gap status label
            self.ax.text(
                gap.index - 0.4,
                (gap.gap_from + gap.gap_to) / 2,
                "Filled" if gap.filled else "Open",
                ha='left', va='center',
                color='black' if gap.filled else 'red',
                fontsize=7,
                bbox=dict(facecolor='none', alpha=0.7, edgecolor='none')
            )
            
            # Mark unfilled gaps with reference lines
            if not gap.filled:
                self.ax.hlines(
                    y=gap.ref_price,
                    xmin=gap.index - 0.5,
                    xmax=gap.index + 0.5,
                    colors='lightcoral' if gap.gap_type == 'down' else 'green',
                    linestyles='dashed',
                    alpha=0.7,
                    linewidth=1.2
                )

    def plot_key_levels(self) -> None:
        """Draw significant price levels on chart"""
        for level in self.analyzer.key_levels:
            self.ax.hlines(
                y=level.price,
                xmin=level.start_index - 0.5,
                xmax=len(self.analyzer.data) + 10,
                color='blue',
                linestyle='--',
                alpha=0.5,
                linewidth=1.5
            )
            self.ax.text(
                level.start_index - 0.5,
                level.price,
                f'{level.price:.2f} ({level.gap_count})',
                ha='right', va='center',
                color='blue',
                fontsize=8,
                bbox=dict(facecolor='none', alpha=0, edgecolor='none')
            )

    def plot_islands(self) -> None:
        """Highlight island reversal patterns on chart"""
        for island in self.analyzer.islands:
            x = [island.start_index - 0.5, island.end_index + 0.5, 
                 island.end_index + 0.5, island.start_index - 0.5]
            y = [island.low, island.low, island.high, island.high]
            
            self.ax.fill(
                x, y,
                facecolor='purple',
                alpha=0.1,
                edgecolor='none'
            )
            
            self.ax.text(
                island.start_index, 
                island.high,
                'Island',
                rotation=0,
                va='bottom',
                color='black',
                fontsize=8,
                bbox=dict(facecolor='none', alpha=0)
            )

    def add_sma_labels(self) -> None:
        """Add SMA and price labels to the right of the chart"""
        last_idx = len(self.analyzer.data) - 1
        current_price = self.analyzer.data['Close'].iloc[-1]
        
        sma_labels = [
            (self.analyzer.data['SMA_1'].iloc[-1], '1 SMA', 'blue'),
            (self.analyzer.data['SMA_20'].iloc[-1], '20 SMA', 'green'),
            (self.analyzer.data['SMA_94'].iloc[-1], '94 SMA', 'red'),
            (current_price, 'Price', 'black')
        ]
        
        for value, label, color in sma_labels:
            self.ax.text(
                last_idx + 15,
                value,
                f'{value:.2f} {label}',
                ha='left', va='center',
                color=color,
                fontsize=9,
                bbox=dict(facecolor='none', alpha=0.7, edgecolor='none')
            )

    def finalize_chart(self) -> None:
        """Configure final chart layout"""
        self.ax.set_xlim(left=-10, right=len(self.analyzer.data)+10)
        plt.tight_layout()

    def save_chart(self) -> str:
        """Save chart and optimize image file size"""
        image_path = f"{self.analyzer.ticker}_{datetime.now().strftime('%Y-%m-%d_%H:%M')}.png"
        self.fig.savefig(image_path, dpi=600, bbox_inches='tight')
        plt.close(self.fig)
        
        # Optimize image size
        with Image.open(image_path) as img:
            img.save(image_path, optimize=True, quality=85)
        
        return image_path
    
    def save_chart_to_buffer(self) -> BytesIO:
        """Save high-quality chart to in-memory buffer with 600 DPI"""
        buffer = BytesIO()
        
        # Save the matplotlib figure to the buffer
        self.fig.savefig(buffer, format='PNG', dpi=600, bbox_inches='tight')
        plt.close(self.fig)  # Close the figure to free memory

        # Optimize image with PIL
        buffer.seek(0)
        img = Image.open(buffer)

        resized_img = img.resize((1920, 1080), Image.LANCZOS)

        # Save resized image to new buffer
        optimized_buffer = BytesIO()
        resized_img.save(optimized_buffer, format='PNG', optimize=True, quality=95)
        optimized_buffer.seek(0)

        return optimized_buffer

    def visualize_pipline(self) -> Optional[BytesIO]:
        """Run complete visualization pipeline with high-quality output"""
        try:
            self.create_base_chart()
            self.plot_gaps()
            self.plot_key_levels()
            self.plot_islands()
            self.add_sma_labels()
            self.finalize_chart()
            return self.save_chart_to_buffer()
        except Exception as e:
            print(f"Visualization failed: {str(e)}")
            return None