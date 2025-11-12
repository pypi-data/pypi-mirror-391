"""
Batch Processing Example - arabictest Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

This example demonstrates batch processing capabilities.
"""

import pandas as pd
import numpy as np
from arabictest import batch_test_from_excel, batch_test_from_csv

print("="*80)
print("Batch Processing Example")
print("="*80)

# First, create sample data files
print("\n1. Creating sample data files...")

np.random.seed(42)
n_obs = 100

# Create sample economic data
economic_data = pd.DataFrame({
    'GDP_Growth': np.random.randn(n_obs) * 0.5 + 2,
    'Unemployment': np.random.randn(n_obs).cumsum() + 5,
    'CPI': np.abs(np.random.randn(n_obs).cumsum() * 2 + 100),
    'Interest_Rate': np.random.randn(n_obs) * 0.3 + 4,
    'Exchange_Rate': np.abs(np.random.randn(n_obs).cumsum() + 50)
})

# Save to Excel
economic_data.to_excel('sample_economic_data.xlsx', index=False)
print("✓ Created: sample_economic_data.xlsx")

# Save to CSV
economic_data.to_csv('sample_economic_data.csv', index=False)
print("✓ Created: sample_economic_data.csv")

# Example 1: Batch test from Excel with Arabic output
print("\n" + "="*80)
print("Example 1: Batch Testing from Excel (Arabic Output)")
print("="*80)

tester_excel = batch_test_from_excel(
    'sample_economic_data.xlsx',
    use_arabic=True,
    output_file='excel_batch_results.xlsx'
)

# Example 2: Batch test from CSV with English output
print("\n" + "="*80)
print("Example 2: Batch Testing from CSV (English Output)")
print("="*80)

tester_csv = batch_test_from_csv(
    'sample_economic_data.csv',
    use_arabic=False,
    output_file='csv_batch_results.csv'
)

# Example 3: Process multiple files
print("\n" + "="*80)
print("Example 3: Processing Multiple Files")
print("="*80)

# Create additional data files
file_names = ['dataset1.xlsx', 'dataset2.xlsx', 'dataset3.xlsx']

for i, filename in enumerate(file_names):
    # Create different data for each file
    np.random.seed(i * 100)
    data = pd.DataFrame({
        f'Variable_{j+1}': np.random.randn(80).cumsum() + 10*j
        for j in range(3)
    })
    data.to_excel(filename, index=False)
    print(f"✓ Created: {filename}")

# Process all files
print("\nProcessing all files...")
all_results = {}

for filename in file_names:
    print(f"\nTesting {filename}...")
    tester = batch_test_from_excel(
        filename,
        use_arabic=False,
        output_file=None  # Don't save individual results
    )
    all_results[filename] = tester.get_summary_dataframe()

# Combine results
print("\n" + "="*80)
print("Combining Results from Multiple Files")
print("="*80)

# Add file source to each DataFrame
for filename, df in all_results.items():
    df['Source_File'] = filename

# Concatenate all results
combined_results = pd.concat(all_results.values(), ignore_index=True)

print(f"\nCombined results shape: {combined_results.shape}")
print("\nFirst 10 rows of combined results:")
print(combined_results.head(10))

# Save combined results
combined_results.to_excel('combined_batch_results.xlsx', index=False)
print("\n✓ Saved combined results to: combined_batch_results.xlsx")

# Example 4: Summary statistics
print("\n" + "="*80)
print("Example 4: Summary Statistics Across All Files")
print("="*80)

# Count stationary vs non-stationary by transformation
result_counts = combined_results.groupby(['Transformation', 'Test', 'Result']).size()
print("\nResult counts by transformation and test:")
print(result_counts)

# Process type distribution
if 'Process_Type' in combined_results.columns:
    process_dist = combined_results.groupby('Variable')['Process_Type'].first().value_counts()
    print("\nProcess type distribution:")
    print(process_dist)

print("\n" + "="*80)
print("Batch processing completed successfully!")
print("="*80)

print("\nFiles created:")
print("  - sample_economic_data.xlsx")
print("  - sample_economic_data.csv")
print("  - excel_batch_results.xlsx")
print("  - csv_batch_results.csv")
print("  - dataset1.xlsx, dataset2.xlsx, dataset3.xlsx")
print("  - combined_batch_results.xlsx")
