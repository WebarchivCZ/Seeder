from django.utils import formats


format_map = {
    r'%j': 'DDD',
    r'%d': 'DD',
    r'%B': 'MMMM',
    r'%b': 'MMM',
    r'%m': 'MM',
    r'%Y': 'YYYY',
    r'%y': 'YY',
    r'%H': 'HH',
    r'%I': 'hh',
    r'%M': 'mm',
    r'%S': 'ss',
    r'%p': 'a',
    r'%z': 'ZZ',
}


def core_processor(request):
    current_formats = formats.get_format(
        "DATE_INPUT_FORMATS",
        lang=request.LANGUAGE_CODE)

    current_format = current_formats[0]
    for py_frm, dj_frm in format_map.items():
        current_format = current_format.replace(py_frm, dj_frm)

    return {
        'js_format': current_format
    }
