"""
arabictest - Professional Unit Root Testing Package with Arabic Language Support

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/arabictest

This package provides comprehensive unit root testing functionality for econometric
research with beautiful Arabic language output support.

Features:
---------
- Multiple unit root tests: ADF, KPSS, Phillips-Perron, DF-GLS
- Automatic testing at levels and first differences
- Log transformation testing for positive variables
- Distinction between TS (Trend Stationary) and DS (Difference Stationary) processes
- Beautiful formatted tables with proper Arabic text rendering
- Export results to Excel and CSV
- Professional output for academic research

Example Usage:
--------------
>>> import pandas as pd
>>> import numpy as np
>>> from arabictest import UnitRootTester, quick_test
>>> 
>>> # Create sample data
>>> data = pd.DataFrame({
>>>     'GDP': np.random.randn(100).cumsum(),
>>>     'Inflation': np.random.randn(100).cumsum()
>>> })
>>> 
>>> # Quick test (with Arabic output)
>>> tester = quick_test(data)
>>> 
>>> # Or use the class for more control
>>> tester = UnitRootTester(data, use_arabic=True)
>>> tester.test_all_variables()
>>> tester.print_summary_table()
>>> 
>>> # Export results
>>> tester.export_to_excel('results.xlsx')
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
__github__ = "https://github.com/merwanroudane/arabictest"

from .unit_root_tests import (
    UnitRootTester,
    quick_test,
    compare_transformations,
    batch_test_from_excel,
    batch_test_from_csv
)

from .arabic_utils import (
    format_arabic_text,
    get_arabic_label,
    ARABIC_LABELS
)

__all__ = [
    'UnitRootTester',
    'quick_test',
    'compare_transformations',
    'batch_test_from_excel',
    'batch_test_from_csv',
    'format_arabic_text',
    'get_arabic_label',
    'ARABIC_LABELS'
]
