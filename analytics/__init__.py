"""
Analytics package for pair trading calculations.
"""
from analytics.core import get_pair_analytics
from analytics.data_processing import get_pair_analytics_from_uploaded_csv

__all__ = [
    'get_pair_analytics',
    'get_pair_analytics_from_uploaded_csv'
]
