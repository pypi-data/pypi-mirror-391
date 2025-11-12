"""
Comprehensive Demo - arabictest Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/arabictest

This script demonstrates all features of the arabictest package.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arabictest import UnitRootTester, quick_test, compare_transformations

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")

def create_demo_data():
    """Create comprehensive demo data with various time series characteristics."""
    np.random.seed(42)
    n = 120  # 10 years monthly data
    
    data = pd.DataFrame({
        # I(0) - Stationary series
        'Inflation_Rate': np.random.randn(n) * 0.5 + 2,
        'Interest_Rate': np.random.randn(n) * 0.8 + 5,
        
        # I(1) - Difference stationary (random walk)
        'GDP': np.random.randn(n).cumsum() + 1000,
        'Price_Level': np.abs(np.random.randn(n).cumsum() * 2 + 100),
        
        # TS - Trend stationary
        'Seasonal_Sales': (np.sin(np.arange(n) * 2 * np.pi / 12) * 10 + 
                          np.arange(n) * 0.5 + 
                          np.random.randn(n) * 2 + 100),
        
        # Random walk with drift
        'Exchange_Rate': np.random.randn(n).cumsum() + np.arange(n) * 0.1 + 50,
    })
    
    return data

def main():
    print_section("arabictest Package - Comprehensive Demonstration")
    
    print("Author: Dr. Merwan Roudane")
    print("Email: merwanroudane920@gmail.com")
    print("GitHub: https://github.com/merwanroudane/arabictest")
    
    # Create demo data
    print_section("Step 1: Creating Demo Data")
    data = create_demo_data()
    
    print("Dataset created with the following variables:")
    for col in data.columns:
        print(f"  - {col}: {len(data)} observations")
    
    print("\nData preview:")
    print(data.head())
    print("\nData statistics:")
    print(data.describe())
    
    # Demo 1: Quick test with Arabic
    print_section("Demo 1: Quick Test with Arabic Output")
    print("Using quick_test() function with default settings...")
    
    tester_ar = quick_test(
        data, 
        use_arabic=True,
        tests=['ADF', 'KPSS', 'PP'],
        tablefmt='fancy_grid'
    )
    
    # Demo 2: Quick test with English
    print_section("Demo 2: Quick Test with English Output")
    print("Same test with English output...")
    
    tester_en = quick_test(
        data,
        use_arabic=False,
        tests=['ADF', 'KPSS', 'PP'],
        tablefmt='grid'
    )
    
    # Demo 3: Detailed analysis of single variable
    print_section("Demo 3: Detailed Single Variable Analysis")
    print("Analyzing GDP with all available tests...")
    
    tester = UnitRootTester(data[['GDP']], use_arabic=False)
    result = tester.test_single_variable(
        'GDP',
        tests=['ADF', 'KPSS', 'PP', 'DFGLS'],
        test_log=True,
        trend='ct'
    )
    tester.print_summary_table(tablefmt='fancy_grid', show_critical_values=True)
    
    # Demo 4: Compare transformations
    print_section("Demo 4: Transformation Comparison")
    print("Comparing different transformations for Price_Level...")
    
    comparison_df = compare_transformations(
        data['Price_Level'],
        var_name='Price_Level',
        use_arabic=False
    )
    print(comparison_df)
    
    # Demo 5: Test with different trend specifications
    print_section("Demo 5: Different Trend Specifications")
    
    print("\nA) Constant only (c):")
    tester_c = UnitRootTester(data[['Seasonal_Sales']], use_arabic=False)
    tester_c.test_all_variables(tests=['ADF'], trend='c')
    tester_c.print_summary_table(tablefmt='simple')
    
    print("\nB) Constant and trend (ct):")
    tester_ct = UnitRootTester(data[['Seasonal_Sales']], use_arabic=False)
    tester_ct.test_all_variables(tests=['ADF'], trend='ct')
    tester_ct.print_summary_table(tablefmt='simple')
    
    # Demo 6: Export results
    print_section("Demo 6: Exporting Results")
    
    # Test all variables for export
    export_tester = UnitRootTester(data, use_arabic=True)
    export_tester.test_all_variables(
        tests=['ADF', 'KPSS', 'PP'],
        test_log=True,
        trend='ct'
    )
    
    # Export to Excel
    excel_file = 'demo_results_arabic.xlsx'
    export_tester.export_to_excel(excel_file)
    print(f"✓ Exported to Excel: {excel_file}")
    
    # Export to CSV
    csv_file = 'demo_results_arabic.csv'
    export_tester.export_to_csv(csv_file)
    print(f"✓ Exported to CSV: {csv_file}")
    
    # Also export English version
    export_tester_en = UnitRootTester(data, use_arabic=False)
    export_tester_en.test_all_variables(tests=['ADF', 'KPSS', 'PP'])
    export_tester_en.export_to_excel('demo_results_english.xlsx')
    print(f"✓ Exported to Excel: demo_results_english.xlsx")
    
    # Demo 7: Summary DataFrame
    print_section("Demo 7: Working with Results DataFrame")
    
    results_df = export_tester.get_summary_dataframe(include_critical_values=False)
    
    print(f"Results DataFrame shape: {results_df.shape}")
    print(f"Columns: {list(results_df.columns)}")
    print("\nFirst 15 rows:")
    print(results_df.head(15))
    
    # Demo 8: Process type summary
    print_section("Demo 8: Process Type Classification Summary")
    
    print("\nClassification of each variable:")
    print("-" * 60)
    for var_name, result in export_tester.results.items():
        print(f"\n{var_name}:")
        print(f"  Process Type: {result['process_type']}")
        print(f"  Observations: {result['n_obs']}")
        
        # Level stationarity
        adf_level = result['level'].get('ADF', {})
        if 'p_value' in adf_level:
            status = "Stationary" if adf_level['p_value'] < 0.05 else "Non-stationary"
            print(f"  Level: {status} (ADF p-value: {adf_level['p_value']:.4f})")
        
        # First difference stationarity
        adf_diff = result['first_diff'].get('ADF', {})
        if 'p_value' in adf_diff:
            status = "Stationary" if adf_diff['p_value'] < 0.05 else "Non-stationary"
            print(f"  1st Diff: {status} (ADF p-value: {adf_diff['p_value']:.4f})")
    
    # Demo 9: Save sample data
    print_section("Demo 9: Saving Sample Data")
    
    data.to_excel('demo_sample_data.xlsx', index=False)
    print(f"✓ Sample data saved to: demo_sample_data.xlsx")
    
    data.to_csv('demo_sample_data.csv', index=False)
    print(f"✓ Sample data saved to: demo_sample_data.csv")
    
    # Final summary
    print_section("Demonstration Complete!")
    
    print("Files created during this demonstration:")
    print("  1. demo_results_arabic.xlsx    - Arabic results in Excel")
    print("  2. demo_results_arabic.csv     - Arabic results in CSV")
    print("  3. demo_results_english.xlsx   - English results in Excel")
    print("  4. demo_sample_data.xlsx       - Sample data in Excel")
    print("  5. demo_sample_data.csv        - Sample data in CSV")
    
    print("\nKey Features Demonstrated:")
    print("  ✓ Quick testing with Arabic/English output")
    print("  ✓ Detailed single variable analysis")
    print("  ✓ Multiple unit root tests (ADF, KPSS, PP, DF-GLS)")
    print("  ✓ Testing at levels and first differences")
    print("  ✓ Log transformation for positive variables")
    print("  ✓ Different trend specifications")
    print("  ✓ Process type classification (TS vs DS)")
    print("  ✓ Beautiful formatted tables")
    print("  ✓ Export to Excel and CSV")
    print("  ✓ Working with results as DataFrames")
    
    print("\n" + "="*80)
    print("Thank you for using arabictest!")
    print("For more information: https://github.com/merwanroudane/arabictest")
    print("Contact: merwanroudane920@gmail.com")
    print("="*80)

if __name__ == "__main__":
    main()
