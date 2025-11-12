"""
Advanced Example - arabictest Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

This example demonstrates advanced features of the arabictest package.
"""

import pandas as pd
import numpy as np
from arabictest import UnitRootTester, compare_transformations

# Set random seed for reproducibility
np.random.seed(123)

print("="*80)
print("Advanced Example: Comprehensive Unit Root Analysis")
print("="*80)

# Create more complex economic data with different characteristics
n_obs = 150

print("\n1. Creating diverse time series...")

# Create different types of series
data = pd.DataFrame({
    # Random walk with drift (DS process)
    'Price_Index': np.random.randn(n_obs).cumsum() + np.arange(n_obs) * 0.5 + 100,
    
    # Stationary around trend (TS process)
    'Output_Gap': np.sin(np.arange(n_obs) * 2 * np.pi / 12) * 2 + np.random.randn(n_obs) * 0.5,
    
    # Random walk (DS process)
    'Money_Supply': np.abs(np.random.randn(n_obs).cumsum() * 10 + 1000),
    
    # Stationary (I(0))
    'Real_Interest_Rate': np.random.randn(n_obs) * 0.8 + 3,
    
    # Integrated of order 2 - needs two differences
    'Stock_Price': np.random.randn(n_obs).cumsum().cumsum() + 1000
})

print(f"Created {len(data)} observations with 5 variables")

# Example 1: Comprehensive testing with all options
print("\n" + "="*80)
print("Example 1: Comprehensive Testing (All Tests)")
print("="*80)

tester = UnitRootTester(data, use_arabic=True)

# Run all available tests
tester.test_all_variables(
    tests=['ADF', 'KPSS', 'PP', 'DFGLS'],
    test_log=True,
    trend='ct'  # Constant and trend
)

tester.print_summary_table(tablefmt='fancy_grid', show_critical_values=True)

# Example 2: Compare different trend specifications
print("\n" + "="*80)
print("Example 2: Testing with Different Trend Specifications")
print("="*80)

# Test with constant only
print("\nA) With Constant Only:")
tester_c = UnitRootTester(data[['Price_Index']], use_arabic=False)
tester_c.test_all_variables(tests=['ADF'], trend='c')
tester_c.print_summary_table(tablefmt='simple')

# Test with constant and trend
print("\nB) With Constant and Trend:")
tester_ct = UnitRootTester(data[['Price_Index']], use_arabic=False)
tester_ct.test_all_variables(tests=['ADF'], trend='ct')
tester_ct.print_summary_table(tablefmt='simple')

# Example 3: Compare transformations for a single series
print("\n" + "="*80)
print("Example 3: Detailed Transformation Comparison")
print("="*80)

comparison = compare_transformations(
    data['Money_Supply'],
    var_name='Money_Supply',
    use_arabic=False
)

print("\nComparison across all transformations:")
print(comparison.to_string())

# Example 4: Analyze log vs. level for positive series
print("\n" + "="*80)
print("Example 4: Log vs. Level Analysis (Money Supply)")
print("="*80)

tester_log = UnitRootTester(data[['Money_Supply']], use_arabic=False)
tester_log.test_all_variables(tests=['ADF', 'KPSS'], test_log=True, trend='ct')
tester_log.print_summary_table(tablefmt='fancy_grid')

# Example 5: Batch analysis with selective variables
print("\n" + "="*80)
print("Example 5: Selective Variable Analysis")
print("="*80)

# Select only stationary variables for demonstration
stationary_data = data[['Real_Interest_Rate', 'Output_Gap']]
tester_stat = UnitRootTester(stationary_data, use_arabic=True)
tester_stat.test_all_variables(tests=['ADF', 'KPSS', 'PP'])
tester_stat.print_summary_table(tablefmt='fancy_grid')

# Example 6: Export detailed results with critical values
print("\n" + "="*80)
print("Example 6: Export Detailed Results")
print("="*80)

# Get detailed DataFrame
detailed_results = tester.get_summary_dataframe(include_critical_values=True)

print("\nDetailed results (first 15 rows):")
print(detailed_results.head(15).to_string())

# Export to files
tester.export_to_excel('advanced_results.xlsx')
tester.export_to_csv('advanced_results.csv')

# Example 7: Process type analysis
print("\n" + "="*80)
print("Example 7: Process Type Classification Summary")
print("="*80)

for var_name, result in tester.results.items():
    print(f"\n{var_name}:")
    print(f"  Process Type: {result['process_type']}")
    print(f"  Observations: {result['n_obs']}")
    
    # Show ADF p-values at different transformations
    if 'ADF' in result['level']:
        print(f"  ADF (Level) p-value: {result['level']['ADF']['p_value']:.4f}")
    if 'ADF' in result['first_diff']:
        print(f"  ADF (1st Diff) p-value: {result['first_diff']['ADF']['p_value']:.4f}")

print("\n" + "="*80)
print("Advanced examples completed successfully!")
print("="*80)
print("\nFiles created:")
print("  - advanced_results.xlsx")
print("  - advanced_results.csv")

print("\nKey Insights:")
print("- Price_Index: Likely DS process (non-stationary with drift)")
print("- Output_Gap: Likely TS process (stationary around trend)")
print("- Money_Supply: DS process (random walk)")
print("- Real_Interest_Rate: Stationary (I(0) process)")
print("- Stock_Price: May need second difference (I(2) process)")
