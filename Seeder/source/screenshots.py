import os

from sh import capturejs
from datetime import datetime
from django.db.models import Q
from django.conf import settings

from source import constants
from source.models import Seed


def take_screenshots():
    """
    Downloads all the screenshots
    """

    now = datetime.now()
    seeds = Seed.archiving.filter(
        Q(screenshot_date__lte=now - constants.SCREENSHOT_MAX_AGE) |
        Q(screenshot__isnull=True)
    )

    for seed in seeds:
        screenshot_name = '{pk}_{date}.png'.format(
            pk=seed.pk, date=now.strftime('%d%m%Y')
        )

        # relative path is expected in FileField.name
        relative_path = os.path.join(constants.SCREENSHOT_DIR,
                                     screenshot_name)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        capturejs(
            uri=seed.url, output=absolute_path,
            viewportsize=constants.SCREENSHOT_RESOLUTION,
        )
        if os.path.isfile(absolute_path):
            seed.screenshot.name = relative_path
            seed.screenshot_date = now
            seed.save()
