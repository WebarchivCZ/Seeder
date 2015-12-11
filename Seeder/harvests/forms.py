from django.forms import BaseModelFormSet
from .models import Harvest


class HarvestFormset(BaseModelFormSet):
    model = Harvest
