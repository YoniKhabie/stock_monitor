from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

from Stock.custom_dataclasses import Gap, Island, KeyLevel


class StockData:
    SMA_PERIODS = [1, 20, 94]  # Simple moving average periods to calculate

    def __init__(self, ticker: str, period_days: int, interval: str):
        self.ticker = ticker.upper()
        self.period_days = period_days
        self.interval = interval.lower()
        self.data = None
        self.gaps = []
        self.key_levels = []
        self.islands = []

    def fetch_data(self) -> None:
        """Download and clean stock data"""
        self.data = yf.download(
            self.ticker, 
            period=f"{self.period_days}d", 
            interval=self.interval, 
            auto_adjust=True
        )
        
        if self.data.empty:
            raise ValueError(f"No data found for {self.ticker}")
        
        # Flatten multi-index columns if present
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)
        
        self.data = self.data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

    def calculate_sma(self) -> None:
        """Calculate all moving averages"""
        for period in self.SMA_PERIODS:
            self.data[f'SMA_{period}'] = self.data['Close'].rolling(window=period).mean()

    def analyze_gaps(self) -> None:
        """Identify and analyze price gaps"""
        min_gap_size = 0.002 * self.data['Close'].mean()
        
        for i in range(1, len(self.data)):
            prev, curr = self.data.iloc[i-1], self.data.iloc[i]
            
            gap_up = curr['Low'] - prev['High'] > min_gap_size
            gap_down = prev['Low'] - curr['High'] > min_gap_size
            
            if gap_up:
                ref_price = min(prev['Open'], prev['Close'])
                self.gaps.append(Gap(
                    index=i,
                    price_level=prev['High'],
                    gap_from=prev['High'],
                    gap_to=curr['Low'],
                    gap_type='up',
                    volume=curr['Volume'],
                    ref_price=ref_price
                ))
            elif gap_down:
                ref_price = max(prev['Open'], prev['Close'])
                self.gaps.append(Gap(
                    index=i,
                    price_level=prev['Low'],
                    gap_from=prev['Low'],
                    gap_to=curr['High'],
                    gap_type='down',
                    volume=curr['Volume'],
                    ref_price=ref_price
                ))
        
        self._check_gap_fill_status()

    def _check_gap_fill_status(self) -> None:
        """Determine if gaps have been filled by subsequent price action"""
        for gap in self.gaps:
            for j in range(gap.index, len(self.data)):
                current = self.data.iloc[j]
                if (gap.gap_type == 'up' and current['Low'] <= gap.gap_from) or \
                   (gap.gap_type == 'down' and current['High'] >= gap.gap_from):
                    gap.filled = True
                    break

    def identify_key_levels(self) -> None:
        """Cluster gaps to identify significant price levels"""
        if not self.gaps:
            return
        
        price_tolerance = 0.01 * self.data['Close'].mean()
        gap_prices = [{'price': g.price_level, 'index': g.index} for g in self.gaps]
        gap_prices.sort(key=lambda x: x['price'])
        
        clusters = []
        current_cluster = [gap_prices[0]]
        
        for price_data in gap_prices[1:]:
            if abs(price_data['price'] - current_cluster[-1]['price']) <= price_tolerance:
                current_cluster.append(price_data)
            else:
                clusters.append(current_cluster)
                current_cluster = [price_data]
        clusters.append(current_cluster)
        
        self.key_levels = [
            KeyLevel(
                price=np.mean([g['price'] for g in cluster]),
                start_index=min(g['index'] for g in cluster),
                gap_count=len(cluster)
            ) for cluster in clusters if len(cluster) > 1
        ]

    def find_island_reversals(self) -> None:
        """Detect island reversal patterns in gap data"""
        for i in range(1, len(self.gaps)):
            prev_gap, curr_gap = self.gaps[i-1], self.gaps[i]
            
            # Check if gaps form a reversal pattern within 13 periods
            if curr_gap.index - prev_gap.index > 13:
                continue
                
            is_reversal = (
                (prev_gap.gap_type == 'up' and curr_gap.gap_type == 'down') or
                (prev_gap.gap_type == 'down' and curr_gap.gap_type == 'up')
            )
            
            if is_reversal:
                island_data = self.data.iloc[prev_gap.index:curr_gap.index]
                self.islands.append(Island(
                    high=island_data['High'].max(),
                    low=island_data['Low'].min(),
                    start_index=prev_gap.index,
                    end_index=curr_gap.index
                ))
    
    def get_last(self, column: str) -> Optional[float]:
        """Return the last value of the specified column in the stock data"""
        if self.data is None or column not in self.data.columns:
            return None
        return self.data[column].iloc[-1]
    
    def get_surrounding_key_levels(self) -> list[float]:
        """Find the two KeyLevel prices that are closest above and below the current close"""
        if not self.key_levels or self.data is None:
            return []

        close_price = self.data['Close'].iloc[-1]

        # Separate key levels into those below and above the current close
        below = [kl.price for kl in self.key_levels if kl.price < close_price]
        above = [kl.price for kl in self.key_levels if kl.price > close_price]

        lower = max(below) if below else None
        upper = min(above) if above else None

        return [p for p in (lower, upper) if p is not None]


    def get_open_gaps(self) -> list[Gap]:
        """Return a list of gaps that are not filled yet"""
        return [gap for gap in self.gaps if not getattr(gap, 'filled', False)]


    def analyze_pipline(self) -> None:
        """Run complete analysis pipeline"""
        self.fetch_data()
        self.calculate_sma()
        self.analyze_gaps()
        self.identify_key_levels()
        self.find_island_reversals()
