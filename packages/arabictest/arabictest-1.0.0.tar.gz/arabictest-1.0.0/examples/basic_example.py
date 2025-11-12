"""
Basic Example - arabictest Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

This example demonstrates basic usage of the arabictest package.
"""

import pandas as pd
import numpy as np
from arabictest import quick_test, UnitRootTester

# Set random seed for reproducibility
np.random.seed(42)

print("="*80)
print("Basic Example: Unit Root Testing with Arabic Support")
print("="*80)

# Create sample economic data
print("\n1. Creating sample data...")
n_obs = 120  # 10 years of monthly data

data = pd.DataFrame({
    'GDP': np.random.randn(n_obs).cumsum() + 1000,  # Non-stationary (random walk)
    'Inflation': np.random.randn(n_obs) * 0.5 + 2,  # Stationary around mean
    'Exchange_Rate': np.abs(np.random.randn(n_obs).cumsum()) + 100,  # Non-stationary
    'Interest_Rate': np.random.randn(n_obs) * 0.3 + 5  # Stationary around mean
})

print(f"Created dataset with {len(data)} observations")
print(f"Variables: {', '.join(data.columns)}")

# Example 1: Quick test with Arabic output
print("\n" + "="*80)
print("Example 1: Quick Test (Arabic Output)")
print("="*80)

tester_arabic = quick_test(data, use_arabic=True, tablefmt='fancy_grid')

# Example 2: Quick test with English output
print("\n" + "="*80)
print("Example 2: Quick Test (English Output)")
print("="*80)

tester_english = quick_test(data, use_arabic=False, tablefmt='grid')

# Example 3: Test specific variable only
print("\n" + "="*80)
print("Example 3: Test Single Variable (GDP)")
print("="*80)

tester = UnitRootTester(data, use_arabic=True)
result = tester.test_single_variable('GDP', tests=['ADF', 'KPSS', 'PP'])
tester.print_summary_table(var_name='GDP', tablefmt='fancy_grid')

# Example 4: Get results as DataFrame
print("\n" + "="*80)
print("Example 4: Export Results to DataFrame")
print("="*80)

results_df = tester_arabic.get_summary_dataframe(include_critical_values=False)
print("\nSummary DataFrame (first 10 rows):")
print(results_df.head(10))

# Example 5: Export results
print("\n" + "="*80)
print("Example 5: Export Results to Files")
print("="*80)

# Export to Excel
tester_arabic.export_to_excel('arabic_test_results.xlsx')

# Export to CSV
tester_arabic.export_to_csv('arabic_test_results.csv')

print("\n" + "="*80)
print("Examples completed successfully!")
print("="*80)
print("\nFiles created:")
print("  - arabic_test_results.xlsx")
print("  - arabic_test_results.csv")
