"""
Unit Root Testing Module
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/arabictest

This module provides comprehensive unit root testing functionality with support for:
- Multiple tests: ADF, KPSS, Phillips-Perron, DF-GLS
- Automatic testing at levels and first differences
- Log transformation for positive variables
- Distinction between TS and DS processes
- Beautiful output tables in Arabic
"""

import numpy as np
import pandas as pd
import warnings
from typing import Union, List, Dict, Tuple, Optional
from datetime import datetime

# Unit root tests
from statsmodels.tsa.stattools import adfuller, kpss
from arch.unitroot import ADF, KPSS, PhillipsPerron, DFGLS

# Formatting
from tabulate import tabulate
from colorama import Fore, Style, init

# Arabic text support
from .arabic_utils import format_arabic_text, get_arabic_label, ARABIC_LABELS

# Initialize colorama
init(autoreset=True)

warnings.filterwarnings('ignore')


class UnitRootTester:
    """
    Comprehensive unit root testing class with Arabic language support.
    
    This class performs multiple unit root tests and provides detailed results
    in beautifully formatted tables with proper Arabic text rendering.
    """
    
    def __init__(self, data: Union[pd.DataFrame, pd.Series], 
                 variable_names: Optional[List[str]] = None,
                 use_arabic: bool = True):
        """
        Initialize the Unit Root Tester.
        
        Parameters:
        -----------
        data : pd.DataFrame or pd.Series
            The time series data to test
        variable_names : list of str, optional
            Names of variables (will use column names if DataFrame)
        use_arabic : bool, default True
            Whether to display results in Arabic
        """
        self.use_arabic = use_arabic
        
        # Convert data to DataFrame if Series
        if isinstance(data, pd.Series):
            self.data = pd.DataFrame({data.name or 'Variable': data})
        else:
            self.data = data.copy()
            
        # Set variable names
        if variable_names is not None:
            self.variable_names = variable_names
        else:
            self.variable_names = list(self.data.columns)
            
        self.results = {}
        
    def _perform_adf_test(self, series: pd.Series, trend: str = 'c') -> Dict:
        """Perform Augmented Dickey-Fuller test."""
        try:
            adf_result = adfuller(series.dropna(), regression=trend, autolag='AIC')
            
            return {
                'test_name': 'ADF',
                'statistic': adf_result[0],
                'p_value': adf_result[1],
                'lags': adf_result[2],
                'nobs': adf_result[3],
                'critical_values': adf_result[4],
                'trend': trend
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _perform_kpss_test(self, series: pd.Series, trend: str = 'c') -> Dict:
        """Perform KPSS stationarity test."""
        try:
            kpss_result = kpss(series.dropna(), regression=trend, nlags='auto')
            
            return {
                'test_name': 'KPSS',
                'statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'lags': kpss_result[2],
                'critical_values': kpss_result[3],
                'trend': trend
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _perform_pp_test(self, series: pd.Series, trend: str = 'c') -> Dict:
        """Perform Phillips-Perron test."""
        try:
            pp = PhillipsPerron(series.dropna(), trend=trend, lags=None)
            
            return {
                'test_name': 'PP',
                'statistic': pp.stat,
                'p_value': pp.pvalue,
                'lags': pp.lags,
                'critical_values': {
                    '1%': pp.critical_values['1%'],
                    '5%': pp.critical_values['5%'],
                    '10%': pp.critical_values['10%']
                },
                'trend': trend
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _perform_dfgls_test(self, series: pd.Series, trend: str = 'c') -> Dict:
        """Perform Dickey-Fuller GLS test."""
        try:
            dfgls = DFGLS(series.dropna(), trend=trend)
            
            return {
                'test_name': 'DF-GLS',
                'statistic': dfgls.stat,
                'p_value': dfgls.pvalue,
                'lags': dfgls.lags,
                'critical_values': {
                    '1%': dfgls.critical_values['1%'],
                    '5%': dfgls.critical_values['5%'],
                    '10%': dfgls.critical_values['10%']
                },
                'trend': trend
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _interpret_adf_pp_dfgls(self, result: Dict, alpha: float = 0.05) -> str:
        """
        Interpret ADF, PP, or DF-GLS test results.
        H0: Unit root exists (non-stationary)
        H1: No unit root (stationary)
        """
        if 'error' in result:
            return 'خطأ في الاختبار' if self.use_arabic else 'Test Error'
            
        if result['p_value'] < alpha:
            if self.use_arabic:
                return format_arabic_text('مستقر - لا يحتوي على جذر وحدة')
            else:
                return 'Stationary - No unit root'
        else:
            if self.use_arabic:
                return format_arabic_text('غير مستقر - يحتوي على جذر وحدة')
            else:
                return 'Non-stationary - Unit root'
                
    def _interpret_kpss(self, result: Dict, alpha: float = 0.05) -> str:
        """
        Interpret KPSS test results.
        H0: Series is stationary
        H1: Unit root present
        """
        if 'error' in result:
            return 'خطأ في الاختبار' if self.use_arabic else 'Test Error'
            
        if result['p_value'] > alpha:
            if self.use_arabic:
                return format_arabic_text('مستقر')
            else:
                return 'Stationary'
        else:
            if self.use_arabic:
                return format_arabic_text('غير مستقر - يحتوي على جذر وحدة')
            else:
                return 'Non-stationary - Unit root'
    
    def _determine_process_type(self, level_results: Dict, 
                                diff_results: Dict) -> str:
        """
        Determine if series is TS (Trend Stationary) or DS (Difference Stationary).
        
        Logic:
        - If stationary at level: TS process
        - If non-stationary at level but stationary at first difference: DS process
        """
        # Check ADF results at level and difference
        adf_level = level_results.get('ADF', {})
        adf_diff = diff_results.get('ADF', {})
        
        kpss_level = level_results.get('KPSS', {})
        
        # Interpret results
        level_stationary = (adf_level.get('p_value', 1) < 0.05 and 
                           kpss_level.get('p_value', 0) > 0.05)
        diff_stationary = adf_diff.get('p_value', 1) < 0.05
        
        if level_stationary:
            if self.use_arabic:
                return format_arabic_text('سلسلة مستقرة حول الاتجاه (TS)')
            else:
                return 'Trend Stationary (TS)'
        elif diff_stationary and not level_stationary:
            if self.use_arabic:
                return format_arabic_text('سلسلة مستقرة بالفروق (DS)')
            else:
                return 'Difference Stationary (DS)'
        else:
            if self.use_arabic:
                return format_arabic_text('غير محدد - يحتاج مزيد من التحليل')
            else:
                return 'Indeterminate - Requires further analysis'
    
    def test_single_variable(self, var_name: str, 
                            tests: List[str] = ['ADF', 'KPSS', 'PP'],
                            test_log: bool = True,
                            trend: str = 'c') -> Dict:
        """
        Perform comprehensive unit root tests on a single variable.
        
        Parameters:
        -----------
        var_name : str
            Name of the variable to test
        tests : list of str
            List of tests to perform ['ADF', 'KPSS', 'PP', 'DFGLS']
        test_log : bool, default True
            Whether to test log transformation (if all values are positive)
        trend : str, default 'c'
            Trend specification: 'c' (constant), 'ct' (constant+trend), 'n' (none)
            
        Returns:
        --------
        dict
            Dictionary containing all test results
        """
        series = self.data[var_name].dropna()
        
        results = {
            'variable': var_name,
            'n_obs': len(series),
            'level': {},
            'first_diff': {},
            'process_type': None
        }
        
        # Check if we can test log transformation
        can_use_log = test_log and (series > 0).all()
        
        if can_use_log:
            results['log_level'] = {}
            results['log_diff'] = {}
        
        # Test at level
        if 'ADF' in tests:
            results['level']['ADF'] = self._perform_adf_test(series, trend)
        if 'KPSS' in tests:
            results['level']['KPSS'] = self._perform_kpss_test(series, trend)
        if 'PP' in tests:
            results['level']['PP'] = self._perform_pp_test(series, trend)
        if 'DFGLS' in tests and trend in ['c', 'ct']:
            results['level']['DFGLS'] = self._perform_dfgls_test(series, trend)
        
        # Test first difference
        diff_series = series.diff().dropna()
        if 'ADF' in tests:
            results['first_diff']['ADF'] = self._perform_adf_test(diff_series, trend)
        if 'KPSS' in tests:
            results['first_diff']['KPSS'] = self._perform_kpss_test(diff_series, trend)
        if 'PP' in tests:
            results['first_diff']['PP'] = self._perform_pp_test(diff_series, trend)
        if 'DFGLS' in tests and trend in ['c', 'ct']:
            results['first_diff']['DFGLS'] = self._perform_dfgls_test(diff_series, trend)
        
        # Test log transformation if applicable
        if can_use_log:
            log_series = np.log(series)
            log_diff_series = log_series.diff().dropna()
            
            if 'ADF' in tests:
                results['log_level']['ADF'] = self._perform_adf_test(log_series, trend)
                results['log_diff']['ADF'] = self._perform_adf_test(log_diff_series, trend)
            if 'KPSS' in tests:
                results['log_level']['KPSS'] = self._perform_kpss_test(log_series, trend)
                results['log_diff']['KPSS'] = self._perform_kpss_test(log_diff_series, trend)
            if 'PP' in tests:
                results['log_level']['PP'] = self._perform_pp_test(log_series, trend)
                results['log_diff']['PP'] = self._perform_pp_test(log_diff_series, trend)
        
        # Determine process type
        results['process_type'] = self._determine_process_type(
            results['level'], results['first_diff']
        )
        
        return results
    
    def test_all_variables(self, tests: List[str] = ['ADF', 'KPSS', 'PP'],
                          test_log: bool = True,
                          trend: str = 'c') -> Dict:
        """
        Perform unit root tests on all variables in the dataset.
        
        Parameters:
        -----------
        tests : list of str
            List of tests to perform
        test_log : bool, default True
            Whether to test log transformation
        trend : str, default 'c'
            Trend specification
            
        Returns:
        --------
        dict
            Dictionary with results for all variables
        """
        all_results = {}
        
        for var_name in self.variable_names:
            all_results[var_name] = self.test_single_variable(
                var_name, tests=tests, test_log=test_log, trend=trend
            )
        
        self.results = all_results
        return all_results
    
    def _format_test_result_row(self, test_name: str, result: Dict, 
                                transformation: str = 'level') -> List:
        """Format a single test result as a table row."""
        if 'error' in result:
            return [test_name, 'Error', '-', '-', '-', result['error']]
        
        # Get interpretation
        if test_name == 'KPSS':
            interpretation = self._interpret_kpss(result)
        else:
            interpretation = self._interpret_adf_pp_dfgls(result)
        
        # Format critical values
        cv_str = ', '.join([f"{k}: {v:.3f}" for k, v in result['critical_values'].items()])
        
        return [
            test_name,
            f"{result['statistic']:.4f}",
            f"{result['p_value']:.4f}",
            result.get('lags', '-'),
            cv_str,
            interpretation
        ]
    
    def print_summary_table(self, var_name: str = None, 
                           tablefmt: str = 'fancy_grid',
                           show_critical_values: bool = True):
        """
        Print beautiful formatted summary table for unit root tests.
        
        Parameters:
        -----------
        var_name : str, optional
            Variable name (if None, prints all variables)
        tablefmt : str, default 'fancy_grid'
            Table format for tabulate
        show_critical_values : bool, default True
            Whether to show critical values in the table
        """
        if not self.results:
            print("No results available. Please run tests first.")
            return
        
        variables_to_print = [var_name] if var_name else list(self.results.keys())
        
        for var in variables_to_print:
            if var not in self.results:
                continue
                
            result = self.results[var]
            
            # Print header
            print("\n" + "="*80)
            if self.use_arabic:
                header = f"{format_arabic_text('نتائج اختبار جذر الوحدة للمتغير')}: {var}"
            else:
                header = f"Unit Root Test Results for: {var}"
            print(Fore.CYAN + Style.BRIGHT + header.center(80))
            print("="*80)
            
            # Print summary info
            if self.use_arabic:
                print(f"{format_arabic_text('عدد المشاهدات')}: {result['n_obs']}")
                print(f"{format_arabic_text('نوع السلسلة')}: {result['process_type']}")
            else:
                print(f"Observations: {result['n_obs']}")
                print(f"Process Type: {result['process_type']}")
            print("-"*80)
            
            # Prepare table headers
            if self.use_arabic:
                headers = [
                    format_arabic_text('الاختبار'),
                    format_arabic_text('الإحصائية'),
                    format_arabic_text('القيمة الاحتمالية'),
                    format_arabic_text('التأخيرات'),
                    format_arabic_text('القيم الحرجة') if show_critical_values else '',
                    format_arabic_text('النتيجة')
                ]
            else:
                headers = ['Test', 'Statistic', 'P-Value', 'Lags', 
                          'Critical Values' if show_critical_values else '', 'Result']
            
            if not show_critical_values:
                headers = [h for h in headers if h != '']
            
            # Level tests
            level_data = []
            for test_name, test_result in result['level'].items():
                row = self._format_test_result_row(test_name, test_result, 'level')
                if not show_critical_values:
                    row = row[:4] + [row[-1]]  # Remove critical values column
                level_data.append(row)
            
            if level_data:
                print("\n" + Fore.GREEN + (format_arabic_text('المستوى') if self.use_arabic else "LEVEL"))
                print(tabulate(level_data, headers=headers, tablefmt=tablefmt))
            
            # First difference tests
            diff_data = []
            for test_name, test_result in result['first_diff'].items():
                row = self._format_test_result_row(test_name, test_result, 'diff')
                if not show_critical_values:
                    row = row[:4] + [row[-1]]
                diff_data.append(row)
            
            if diff_data:
                print("\n" + Fore.YELLOW + (format_arabic_text('الفرق الأول') if self.use_arabic else "FIRST DIFFERENCE"))
                print(tabulate(diff_data, headers=headers, tablefmt=tablefmt))
            
            # Log level tests (if applicable)
            if 'log_level' in result and result['log_level']:
                log_level_data = []
                for test_name, test_result in result['log_level'].items():
                    row = self._format_test_result_row(test_name, test_result, 'log')
                    if not show_critical_values:
                        row = row[:4] + [row[-1]]
                    log_level_data.append(row)
                
                if log_level_data:
                    print("\n" + Fore.MAGENTA + (format_arabic_text('اللوغاريتم') if self.use_arabic else "LOG LEVEL"))
                    print(tabulate(log_level_data, headers=headers, tablefmt=tablefmt))
            
            # Log difference tests (if applicable)
            if 'log_diff' in result and result['log_diff']:
                log_diff_data = []
                for test_name, test_result in result['log_diff'].items():
                    row = self._format_test_result_row(test_name, test_result, 'log_diff')
                    if not show_critical_values:
                        row = row[:4] + [row[-1]]
                    log_diff_data.append(row)
                
                if log_diff_data:
                    print("\n" + Fore.BLUE + (format_arabic_text('لوغاريتم الفرق الأول') if self.use_arabic else "LOG FIRST DIFFERENCE"))
                    print(tabulate(log_diff_data, headers=headers, tablefmt=tablefmt))
            
            print("\n")
    
    def get_summary_dataframe(self, include_critical_values: bool = False) -> pd.DataFrame:
        """
        Get a summary DataFrame of all test results.
        
        Parameters:
        -----------
        include_critical_values : bool, default False
            Whether to include critical values in the DataFrame
            
        Returns:
        --------
        pd.DataFrame
            Summary of all test results
        """
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        
        for var_name, result in self.results.items():
            for transformation in ['level', 'first_diff', 'log_level', 'log_diff']:
                if transformation not in result or not result[transformation]:
                    continue
                
                for test_name, test_result in result[transformation].items():
                    if 'error' in test_result:
                        continue
                    
                    # Get interpretation
                    if test_name == 'KPSS':
                        interpretation = self._interpret_kpss(test_result)
                    else:
                        interpretation = self._interpret_adf_pp_dfgls(test_result)
                    
                    row = {
                        'Variable': var_name,
                        'Transformation': transformation,
                        'Test': test_name,
                        'Statistic': test_result['statistic'],
                        'P-Value': test_result['p_value'],
                        'Lags': test_result.get('lags', None),
                        'Result': interpretation,
                        'Process_Type': result['process_type']
                    }
                    
                    if include_critical_values:
                        for level, value in test_result['critical_values'].items():
                            row[f'CV_{level}'] = value
                    
                    summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        
        # Translate column names if using Arabic
        if self.use_arabic:
            column_mapping = {
                'Variable': format_arabic_text('المتغير'),
                'Transformation': format_arabic_text('التحويل'),
                'Test': format_arabic_text('الاختبار'),
                'Statistic': format_arabic_text('الإحصائية'),
                'P-Value': format_arabic_text('القيمة الاحتمالية'),
                'Lags': format_arabic_text('التأخيرات'),
                'Result': format_arabic_text('النتيجة'),
                'Process_Type': format_arabic_text('نوع السلسلة')
            }
            df = df.rename(columns=column_mapping)
        
        return df
    
    def export_to_excel(self, filename: str, include_critical_values: bool = True):
        """
        Export test results to Excel file.
        
        Parameters:
        -----------
        filename : str
            Output filename (should end with .xlsx)
        include_critical_values : bool, default True
            Whether to include critical values
        """
        df = self.get_summary_dataframe(include_critical_values=include_critical_values)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create separate sheets for each variable
            for var_name in self.results.keys():
                var_df = df[df.iloc[:, 0] == var_name].copy()
                safe_name = var_name[:31]  # Excel sheet name limit
                var_df.to_excel(writer, sheet_name=safe_name, index=False)
        
        print(f"\n{Fore.GREEN}Results exported to: {filename}")
    
    def export_to_csv(self, filename: str, include_critical_values: bool = True):
        """
        Export test results to CSV file.
        
        Parameters:
        -----------
        filename : str
            Output filename (should end with .csv)
        include_critical_values : bool, default True
            Whether to include critical values
        """
        df = self.get_summary_dataframe(include_critical_values=include_critical_values)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
        print(f"\n{Fore.GREEN}Results exported to: {filename}")


# Convenience functions for quick testing
def quick_test(data: Union[pd.DataFrame, pd.Series], 
               tests: List[str] = ['ADF', 'KPSS', 'PP'],
               use_arabic: bool = True,
               test_log: bool = True,
               trend: str = 'c',
               tablefmt: str = 'fancy_grid') -> UnitRootTester:
    """
    Quickly perform unit root tests and display results.
    
    Parameters:
    -----------
    data : pd.DataFrame or pd.Series
        Data to test
    tests : list of str
        Tests to perform
    use_arabic : bool, default True
        Display in Arabic
    test_log : bool, default True
        Test log transformation
    trend : str, default 'c'
        Trend specification
    tablefmt : str, default 'fancy_grid'
        Table format
        
    Returns:
    --------
    UnitRootTester
        Tester object with results
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> import numpy as np
    >>> data = pd.DataFrame({'GDP': np.random.randn(100).cumsum()})
    >>> tester = quick_test(data)
    """
    tester = UnitRootTester(data, use_arabic=use_arabic)
    tester.test_all_variables(tests=tests, test_log=test_log, trend=trend)
    tester.print_summary_table(tablefmt=tablefmt)
    return tester


def compare_transformations(series: pd.Series, 
                           var_name: str = 'Variable',
                           use_arabic: bool = True) -> pd.DataFrame:
    """
    Compare unit root test results across different transformations.
    
    Parameters:
    -----------
    series : pd.Series
        Time series to test
    var_name : str
        Name of the variable
    use_arabic : bool
        Use Arabic labels
        
    Returns:
    --------
    pd.DataFrame
        Comparison table
    """
    data = pd.DataFrame({var_name: series})
    tester = UnitRootTester(data, use_arabic=use_arabic)
    tester.test_all_variables()
    
    return tester.get_summary_dataframe()


def batch_test_from_excel(filepath: str, 
                          use_arabic: bool = True,
                          output_file: str = None) -> UnitRootTester:
    """
    Perform unit root tests on all columns in an Excel file.
    
    Parameters:
    -----------
    filepath : str
        Path to Excel file
    use_arabic : bool
        Display in Arabic
    output_file : str, optional
        Output filename for results
        
    Returns:
    --------
    UnitRootTester
        Tester object with results
    """
    data = pd.read_excel(filepath)
    tester = UnitRootTester(data, use_arabic=use_arabic)
    tester.test_all_variables()
    tester.print_summary_table()
    
    if output_file:
        if output_file.endswith('.xlsx'):
            tester.export_to_excel(output_file)
        elif output_file.endswith('.csv'):
            tester.export_to_csv(output_file)
    
    return tester


def batch_test_from_csv(filepath: str, 
                       use_arabic: bool = True,
                       output_file: str = None) -> UnitRootTester:
    """
    Perform unit root tests on all columns in a CSV file.
    
    Parameters:
    -----------
    filepath : str
        Path to CSV file
    use_arabic : bool
        Display in Arabic
    output_file : str, optional
        Output filename for results
        
    Returns:
    --------
    UnitRootTester
        Tester object with results
    """
    data = pd.read_csv(filepath)
    tester = UnitRootTester(data, use_arabic=use_arabic)
    tester.test_all_variables()
    tester.print_summary_table()
    
    if output_file:
        if output_file.endswith('.xlsx'):
            tester.export_to_excel(output_file)
        elif output_file.endswith('.csv'):
            tester.export_to_csv(output_file)
    
    return tester
