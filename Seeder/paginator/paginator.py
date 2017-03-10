from django.core.paginator import Paginator, Page



class CustomPaginator(Paginator):
    def _get_page(self, *args, **kwargs):
        return CustomPage(*args, **kwargs)


class CustomPage(Page):
    """
    Custom page that supports range around current page
    """

    def get_current_range(self):
        lower_bound = max((self.number-5, 1))
        return range(lower_bound, self.paginator.count)[0:10]
