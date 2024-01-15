from time import time
from .models import ExtinctWebsite as EW


def reload_extinct_websites(per_page=EW.PER_PAGE):
    """ Simply run ExtinctWebsite reloader with time measurement. """
    t0 = time()
    created = EW.reload_objects(per_page=per_page)
    tf = time()
    print(f"Reloaded {len(created)} Extinct Websites in {tf-t0:.2f} seconds.")
