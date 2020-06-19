from django.forms import widgets, MultiValueField, DateField


class DatePickerWidget(widgets.DateInput):
    def __init__(self, attrs=None, format='%Y-%m-%d'):
        # Use the HTML date widget
        if attrs is not None:
            attrs.update({'type': 'date'})
        else:
            attrs = {'type': 'date'}
        super().__init__(attrs=attrs, format=format)


class DateRangeWidget(widgets.MultiWidget):
    def __init__(self, **kwargs):
        super().__init__(
            widgets=[DatePickerWidget, DatePickerWidget],
        )

    def decompress(self, value):
        return value


class RangeField(MultiValueField):
    def __init__(self, field_class=DateField, widget=None, **kwargs):
        if 'initial' not in kwargs:
            kwargs['initial'] = ['', '']
        fields = (field_class(), field_class())

        super().__init__(fields=fields, widget=DateRangeWidget(), **kwargs)

    def compress(self, data_list):
        if data_list:
            return [
                self.fields[0].clean(data_list[0]),
                self.fields[1].clean(data_list[1])
            ]
        return None
