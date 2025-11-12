# arabictest - اختبارات جذر الوحدة

<div dir="rtl">

## حزمة اختبارات جذر الوحدة الاحترافية مع دعم اللغة العربية

**المؤلف:** د. مروان رودان  
**البريد الإلكتروني:** merwanroudane920@gmail.com  
**GitHub:** https://github.com/merwanroudane/arabictest

### نظرة عامة

حزمة Python احترافية لإجراء اختبارات جذر الوحدة الشاملة على السلاسل الزمنية الاقتصادية. تتميز الحزمة بدعم كامل للغة العربية مع عرض صحيح للنصوص من اليمين إلى اليسار (RTL) وجداول منسقة بشكل جميل.

### المميزات الرئيسية

- **اختبارات متعددة:** ADF, KPSS, Phillips-Perron, DF-GLS
- **اختبار تلقائي** للمستويات والفروق الأولى
- **تحويل لوغاريتمي** تلقائي للمتغيرات الموجبة
- **تمييز** بين سلاسل TS (مستقرة حول الاتجاه) و DS (مستقرة بالفروق)
- **جداول جميلة** بتنسيق احترافي مع دعم كامل للعربية
- **تصدير النتائج** إلى Excel و CSV
- **مخرجات احترافية** مناسبة للبحث الأكاديمي

### التثبيت

</div>

```bash
# من GitHub
pip install git+https://github.com/merwanroudane/arabictest.git

# أو محلياً
cd arabictest
pip install -e .
```

<div dir="rtl">

### الاستخدام السريع

</div>

```python
import pandas as pd
import numpy as np
from arabictest import quick_test

# إنشاء بيانات تجريبية
np.random.seed(42)
data = pd.DataFrame({
    'GDP': np.random.randn(100).cumsum(),
    'Inflation': np.random.randn(100) * 0.5 + 2,
    'Exchange_Rate': np.abs(np.random.randn(100).cumsum()) + 100
})

# اختبار سريع مع عرض النتائج بالعربية
tester = quick_test(data, use_arabic=True)
```

---

# Professional Unit Root Testing Package

**Author:** Dr. Merwan Roudane  
**Email:** merwanroudane920@gmail.com  
**GitHub:** https://github.com/merwanroudane/arabictest

## Overview

A comprehensive Python package for performing unit root tests on economic time series with full Arabic language support and beautiful RTL text rendering.

## Key Features

- **Multiple Tests:** ADF, KPSS, Phillips-Perron, DF-GLS
- **Automatic Testing:** at levels and first differences
- **Log Transformation:** automatic for positive variables
- **Process Classification:** distinguish between TS (Trend Stationary) and DS (Difference Stationary)
- **Beautiful Tables:** professional formatting with full Arabic support
- **Export Results:** to Excel and CSV formats
- **Research-Ready:** professional output for academic papers

## Installation

```bash
# From GitHub
pip install git+https://github.com/merwanroudane/arabictest.git

# Or locally
cd arabictest
pip install -e .
```

## Quick Start

```python
import pandas as pd
import numpy as np
from arabictest import quick_test, UnitRootTester

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'GDP': np.random.randn(100).cumsum(),
    'Inflation': np.random.randn(100) * 0.5 + 2,
    'Exchange_Rate': np.abs(np.random.randn(100).cumsum()) + 100
})

# Quick test with Arabic output
tester = quick_test(data, use_arabic=True)

# Or for English output
tester_en = quick_test(data, use_arabic=False)
```

## Advanced Usage

### Using the UnitRootTester Class

```python
from arabictest import UnitRootTester

# Initialize tester
tester = UnitRootTester(data, use_arabic=True)

# Run all tests
tester.test_all_variables(
    tests=['ADF', 'KPSS', 'PP', 'DFGLS'],
    test_log=True,
    trend='ct'  # constant and trend
)

# Display results
tester.print_summary_table(tablefmt='fancy_grid')

# Get results as DataFrame
results_df = tester.get_summary_dataframe()

# Export to Excel
tester.export_to_excel('unit_root_results.xlsx')

# Export to CSV
tester.export_to_csv('unit_root_results.csv')
```

### Testing a Single Variable

```python
# Test specific variable
result = tester.test_single_variable(
    'GDP',
    tests=['ADF', 'KPSS', 'PP'],
    test_log=True,
    trend='c'  # constant only
)

# Display just this variable
tester.print_summary_table(var_name='GDP')
```

### Batch Processing from Files

```python
from arabictest import batch_test_from_excel, batch_test_from_csv

# Test all variables in Excel file
tester = batch_test_from_excel(
    'economic_data.xlsx',
    use_arabic=True,
    output_file='results.xlsx'
)

# Test all variables in CSV file
tester = batch_test_from_csv(
    'economic_data.csv',
    use_arabic=True,
    output_file='results.xlsx'
)
```

### Compare Transformations

```python
from arabictest import compare_transformations

# Compare results across transformations
comparison_df = compare_transformations(
    data['GDP'],
    var_name='GDP',
    use_arabic=True
)
print(comparison_df)
```

## Test Options

### Available Tests

- **ADF**: Augmented Dickey-Fuller test
- **KPSS**: Kwiatkowski-Phillips-Schmidt-Shin test
- **PP**: Phillips-Perron test
- **DFGLS**: Dickey-Fuller GLS test

### Trend Specifications

- `'c'`: Constant only (default)
- `'ct'`: Constant and linear trend
- `'n'`: No constant or trend

### Table Formats

Choose from various table formats:
- `'fancy_grid'` (default): Beautiful box-drawing characters
- `'grid'`: Simple grid
- `'simple'`: Minimal formatting
- `'pipe'`: Markdown-style
- `'rst'`: reStructuredText
- `'html'`: HTML table

## Understanding the Results

### Process Types

The package automatically classifies series into:

- **TS Process (Trend Stationary)**: Stationary around a deterministic trend
- **DS Process (Difference Stationary)**: Non-stationary but becomes stationary after differencing
- **Indeterminate**: Requires further analysis

### Interpretation

For ADF, PP, and DF-GLS tests:
- **H₀**: Unit root exists (non-stationary)
- **H₁**: No unit root (stationary)
- If p-value < 0.05 → Reject H₀ → Series is stationary

For KPSS test:
- **H₀**: Series is stationary
- **H₁**: Unit root present
- If p-value > 0.05 → Cannot reject H₀ → Series appears stationary

## Arabic Output Examples

<div dir="rtl">

عند استخدام `use_arabic=True`، ستحصل على جداول منسقة بالعربية مثل:

```
================================================================================
                      نتائج اختبار جذر الوحدة للمتغير: GDP                      
================================================================================
عدد المشاهدات: 100
نوع السلسلة: سلسلة مستقرة بالفروق (DS)
--------------------------------------------------------------------------------

المستوى
╒═══════════╤═══════════╤═══════════════════════╤═════════════╤═══════════════════════════════╤══════════════════════════════╕
│ الاختبار │ الإحصائية │ القيمة الاحتمالية    │ التأخيرات  │ القيم الحرجة                  │ النتيجة                     │
╞═══════════╪═══════════╪═══════════════════════╪═════════════╪═══════════════════════════════╪══════════════════════════════╡
│ ADF       │ -1.2345   │ 0.6543               │ 1           │ 1%: -3.46, 5%: -2.87, 10%: -2.57│ غير مستقر - يحتوي على جذر وحدة│
│ KPSS      │ 0.8765    │ 0.0123               │ 8           │ 1%: 0.74, 5%: 0.46, 10%: 0.35  │ غير مستقر - يحتوي على جذر وحدة│
│ PP        │ -1.3456   │ 0.6123               │ 5           │ 1%: -3.46, 5%: -2.87, 10%: -2.57│ غير مستقر - يحتوي على جذر وحدة│
╘═══════════╧═══════════╧═══════════════════════╧═════════════╧═══════════════════════════════╧══════════════════════════════╛
```

</div>

## Dependencies

- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- statsmodels >= 0.13.0
- arch >= 5.0.0
- tabulate >= 0.8.9
- prettytable >= 3.0.0
- arabic-reshaper >= 2.1.0
- python-bidi >= 0.4.2
- colorama >= 0.4.4

## Examples

See the `examples/` directory for comprehensive examples:
- `basic_example.py`: Basic usage
- `advanced_example.py`: Advanced features
- `batch_processing.py`: Processing multiple files
- `custom_analysis.py`: Custom analysis workflows

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{arabictest2024,
  author = {Roudane, Merwan},
  title = {arabictest: Professional Unit Root Testing with Arabic Support},
  year = {2024},
  url = {https://github.com/merwanroudane/arabictest}
}
```

## Contact

**Dr. Merwan Roudane**  
Email: merwanroudane920@gmail.com  
GitHub: https://github.com/merwanroudane/arabictest

---

<div dir="rtl">

## الدعم والمساعدة

للحصول على المساعدة أو الإبلاغ عن مشكلة:
1. افتح issue على GitHub
2. راسلني على merwanroudane920@gmail.com

## الترخيص

هذه الحزمة مرخصة تحت رخصة MIT - انظر ملف LICENSE للتفاصيل.

</div>
