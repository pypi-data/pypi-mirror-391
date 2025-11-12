"""
Basic Tests for arabictest Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

Run with: pytest tests/test_basic.py
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arabictest import UnitRootTester, quick_test
from arabictest.arabic_utils import format_arabic_text, get_arabic_label


class TestArabicUtils:
    """Test Arabic text formatting utilities."""
    
    def test_format_arabic_text(self):
        """Test Arabic text formatting."""
        text = "اختبار"
        formatted = format_arabic_text(text)
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_get_arabic_label(self):
        """Test getting Arabic labels."""
        label = get_arabic_label('adf')
        assert isinstance(label, str)
        assert len(label) > 0
        
        # Test non-existent key
        label = get_arabic_label('nonexistent')
        assert label == 'nonexistent'


class TestUnitRootTester:
    """Test UnitRootTester class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        return pd.DataFrame({
            'stationary': np.random.randn(100),
            'random_walk': np.random.randn(100).cumsum(),
            'positive': np.abs(np.random.randn(100).cumsum()) + 10
        })
    
    def test_initialization(self, sample_data):
        """Test UnitRootTester initialization."""
        tester = UnitRootTester(sample_data, use_arabic=True)
        assert tester.use_arabic == True
        assert len(tester.variable_names) == 3
        assert tester.data.shape == sample_data.shape
    
    def test_initialization_with_series(self):
        """Test initialization with pandas Series."""
        series = pd.Series(np.random.randn(50), name='test_series')
        tester = UnitRootTester(series)
        assert isinstance(tester.data, pd.DataFrame)
        assert 'test_series' in tester.data.columns
    
    def test_adf_test(self, sample_data):
        """Test ADF test execution."""
        tester = UnitRootTester(sample_data)
        result = tester._perform_adf_test(sample_data['stationary'])
        
        assert 'test_name' in result
        assert result['test_name'] == 'ADF'
        assert 'statistic' in result
        assert 'p_value' in result
        assert 'lags' in result
        assert isinstance(result['statistic'], (int, float))
    
    def test_kpss_test(self, sample_data):
        """Test KPSS test execution."""
        tester = UnitRootTester(sample_data)
        result = tester._perform_kpss_test(sample_data['stationary'])
        
        assert 'test_name' in result
        assert result['test_name'] == 'KPSS'
        assert 'statistic' in result
        assert 'p_value' in result
    
    def test_pp_test(self, sample_data):
        """Test Phillips-Perron test execution."""
        tester = UnitRootTester(sample_data)
        result = tester._perform_pp_test(sample_data['stationary'])
        
        assert 'test_name' in result
        assert result['test_name'] == 'PP'
        assert 'statistic' in result
        assert 'p_value' in result
    
    def test_single_variable_testing(self, sample_data):
        """Test single variable testing."""
        tester = UnitRootTester(sample_data)
        result = tester.test_single_variable(
            'stationary',
            tests=['ADF', 'KPSS'],
            test_log=False
        )
        
        assert 'variable' in result
        assert result['variable'] == 'stationary'
        assert 'level' in result
        assert 'first_diff' in result
        assert 'process_type' in result
        assert 'ADF' in result['level']
        assert 'KPSS' in result['level']
    
    def test_all_variables_testing(self, sample_data):
        """Test testing all variables."""
        tester = UnitRootTester(sample_data)
        results = tester.test_all_variables(tests=['ADF', 'KPSS'])
        
        assert len(results) == 3
        assert 'stationary' in results
        assert 'random_walk' in results
        assert 'positive' in results
        
        for var_name, result in results.items():
            assert 'level' in result
            assert 'first_diff' in result
            assert 'process_type' in result
    
    def test_log_transformation(self, sample_data):
        """Test log transformation testing."""
        tester = UnitRootTester(sample_data[['positive']])
        result = tester.test_single_variable(
            'positive',
            tests=['ADF'],
            test_log=True
        )
        
        assert 'log_level' in result
        assert 'log_diff' in result
        assert 'ADF' in result['log_level']
    
    def test_interpretation_adf(self, sample_data):
        """Test ADF result interpretation."""
        tester = UnitRootTester(sample_data, use_arabic=False)
        
        # Create mock result
        result_stationary = {'p_value': 0.01}
        result_nonstationary = {'p_value': 0.50}
        
        interp_stat = tester._interpret_adf_pp_dfgls(result_stationary)
        interp_nonstat = tester._interpret_adf_pp_dfgls(result_nonstationary)
        
        assert 'Stationary' in interp_stat or 'stationary' in interp_stat.lower()
        assert 'Non-stationary' in interp_nonstat or 'non-stationary' in interp_nonstat.lower()
    
    def test_get_summary_dataframe(self, sample_data):
        """Test getting summary DataFrame."""
        tester = UnitRootTester(sample_data, use_arabic=False)
        tester.test_all_variables(tests=['ADF', 'KPSS'])
        
        df = tester.get_summary_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'Variable' in df.columns
        assert 'Test' in df.columns
        assert 'Statistic' in df.columns
        assert 'P-Value' in df.columns
    
    def test_export_to_csv(self, sample_data, tmp_path):
        """Test CSV export."""
        tester = UnitRootTester(sample_data)
        tester.test_all_variables(tests=['ADF'])
        
        output_file = tmp_path / "test_results.csv"
        tester.export_to_csv(str(output_file))
        
        assert output_file.exists()
        
        # Read back and verify
        df = pd.read_csv(output_file)
        assert len(df) > 0
    
    def test_export_to_excel(self, sample_data, tmp_path):
        """Test Excel export."""
        tester = UnitRootTester(sample_data)
        tester.test_all_variables(tests=['ADF'])
        
        output_file = tmp_path / "test_results.xlsx"
        tester.export_to_excel(str(output_file))
        
        assert output_file.exists()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        return pd.DataFrame({
            'var1': np.random.randn(50),
            'var2': np.random.randn(50).cumsum()
        })
    
    def test_quick_test(self, sample_data):
        """Test quick_test function."""
        tester = quick_test(
            sample_data,
            use_arabic=False,
            tests=['ADF']
        )
        
        assert isinstance(tester, UnitRootTester)
        assert len(tester.results) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
