from django.forms import widgets,MultiValueField, DateField


class DatePickerWidget(widgets.DateInput):
    class Media:
        css = {
            'all': (
                'css/bootstrap-datetimepicker.min.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.3/moment-with-locales.min.js',  # noqa
            'js/bootstrap-datetimepicker.min.js',
            'datetime_picker.js'
        )

class DateRangeWidget(widgets.MultiWidget):
    def __init__(self, **kwargs):
        super(DateRangeWidget, self).__init__(
            widgets=[DatePickerWidget, DatePickerWidget],
            attrs = {'class': 'date_picker'},
        )

    def decompress(self, value):
        return value

class RangeField(MultiValueField):
    def __init__(self, field_class=DateField, widget=None, **kwargs):
        if 'initial'  not in kwargs:
            kwargs['initial'] = ['','']
        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
            fields=fields,
            widget=DateRangeWidget(),
            **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [
                self.fields[0].clean(data_list[0]),
                self.fields[1].clean(data_list[1])
            ]
        return None