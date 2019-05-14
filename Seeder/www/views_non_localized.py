from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.utils.http import is_safe_url
from django.urls import reverse
from django.utils import translation

from urljects import U, URLView

class ChangeLanguage(View, URLView):
    url = U / 'lang' / r'(?P<code>\w+)'
    url_name = 'change_language'

    def get(self, request, code):
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
            translation.activate(code)
        return HttpResponseRedirect(reverse('www:index'))
