from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation


class ChangeLanguage(View):
    def get(self, request, code):
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
            translation.activate(code)
        return HttpResponseRedirect(reverse('www:index'))
