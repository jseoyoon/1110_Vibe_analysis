"""
서울시 따릉이 데이터 분석 패키지
"""

from .data_loader import (
    load_seoulbike_data,
    get_basic_stats,
    aggregate_by_month,
    aggregate_by_gender,
    aggregate_by_age,
    create_segment_pivot
)

from .visualizer import (
    plot_monthly_trend,
    plot_gender_distribution,
    plot_age_distribution,
    plot_segment_heatmap,
    plot_monthly_gender_trend
)

__version__ = '0.1.0'
__all__ = [
    'load_seoulbike_data',
    'get_basic_stats',
    'aggregate_by_month',
    'aggregate_by_gender',
    'aggregate_by_age',
    'create_segment_pivot',
    'plot_monthly_trend',
    'plot_gender_distribution',
    'plot_age_distribution',
    'plot_segment_heatmap',
    'plot_monthly_gender_trend'
]
