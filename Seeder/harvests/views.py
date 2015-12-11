from core import generic_views
from . import models


class HarvestView(generic_views.LoginMixin):
    view_name = 'harvests'
    model = models.Harvest
