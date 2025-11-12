"""
Arabic Text Utilities
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

This module handles proper Arabic text formatting and display.
"""

import arabic_reshaper
from bidi.algorithm import get_display


def format_arabic_text(text):
    """
    Format Arabic text for proper display in environments that don't support RTL.
    
    Parameters:
    -----------
    text : str
        The Arabic text to format
        
    Returns:
    --------
    str
        Properly formatted Arabic text
        
    Examples:
    ---------
    >>> arabic_text = "اختبار جذر الوحدة"
    >>> formatted = format_arabic_text(arabic_text)
    """
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        # If formatting fails, return original text
        return text


def format_arabic_list(text_list):
    """
    Format a list of Arabic texts.
    
    Parameters:
    -----------
    text_list : list
        List of Arabic texts
        
    Returns:
    --------
    list
        List of formatted Arabic texts
    """
    return [format_arabic_text(text) for text in text_list]


def format_arabic_dict(data_dict, keys_to_format=None):
    """
    Format Arabic text in dictionary values.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary containing Arabic text
    keys_to_format : list, optional
        Specific keys to format (default: all string values)
        
    Returns:
    --------
    dict
        Dictionary with formatted Arabic text
    """
    formatted_dict = {}
    for key, value in data_dict.items():
        if keys_to_format is None or key in keys_to_format:
            if isinstance(value, str):
                formatted_dict[key] = format_arabic_text(value)
            elif isinstance(value, list):
                formatted_dict[key] = format_arabic_list(value)
            else:
                formatted_dict[key] = value
        else:
            formatted_dict[key] = value
    return formatted_dict


# Arabic text constants for the package
ARABIC_LABELS = {
    # Test names
    'adf': 'اختبار ديكي-فولر المُعزَّز',
    'pp': 'اختبار فيليبس-بيرون',
    'kpss': 'اختبار KPSS',
    'dfgls': 'اختبار ديكي-فولر GLS',
    
    # Table headers
    'variable': 'المتغير',
    'test': 'الاختبار',
    'statistic': 'الإحصائية',
    'p_value': 'القيمة الاحتمالية',
    'critical_values': 'القيم الحرجة',
    'lags': 'عدد التأخيرات',
    'trend': 'الاتجاه',
    'result': 'النتيجة',
    'level': 'المستوى',
    'first_difference': 'الفرق الأول',
    'log_level': 'اللوغاريتم',
    'log_diff': 'لوغاريتم الفرق الأول',
    
    # Results
    'stationary': 'مستقر',
    'non_stationary': 'غير مستقر',
    'unit_root': 'يحتوي على جذر وحدة',
    'no_unit_root': 'لا يحتوي على جذر وحدة',
    'reject_null': 'رفض الفرضية الصفرية',
    'fail_to_reject': 'عدم رفض الفرضية الصفرية',
    
    # Process types
    'ts_process': 'سلسلة مستقرة حول الاتجاه (TS)',
    'ds_process': 'سلسلة مستقرة بالفروق (DS)',
    'indeterminate': 'غير محدد',
    
    # Trend types
    'constant': 'ثابت فقط',
    'constant_trend': 'ثابت واتجاه',
    'no_trend': 'بدون ثابت أو اتجاه',
    
    # Summary labels
    'summary_title': 'ملخص نتائج اختبار جذر الوحدة',
    'test_date': 'تاريخ الاختبار',
    'n_observations': 'عدد المشاهدات',
    'tests_performed': 'الاختبارات المُنفَّذة',
    'recommendations': 'التوصيات',
}


def get_arabic_label(key):
    """
    Get formatted Arabic label for a given key.
    
    Parameters:
    -----------
    key : str
        The label key
        
    Returns:
    --------
    str
        Formatted Arabic label
    """
    if key in ARABIC_LABELS:
        return format_arabic_text(ARABIC_LABELS[key])
    return key
