
from io import BytesIO
from typing import Optional

from Stock.chart import StockChart
from Stock.data import StockData


class ImgGenerator:
    @staticmethod
    def generate_chart(analyzer:StockData) -> Optional[BytesIO]:
        """Generate and save stock chart"""
        visualizer = StockChart(analyzer)
        return visualizer.visualize_pipline()

    @classmethod
    def run(cls, analyzer:StockData) -> Optional[BytesIO]:
        """Run the complete chart generation process"""
        image_buf = cls.generate_chart(analyzer)
        if image_buf is None:
            raise ValueError("Failed to generate chart - received None buffer")
        return image_buf