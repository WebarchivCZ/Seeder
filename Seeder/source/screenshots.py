import os
import requests

from logging import getLogger
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from source import constants
from source.models import Source


logger = getLogger('screenshots.generator')


def take_screenshots():
    """
    Downloads screenshots for sources that need them

    Args:
        max_sources (int): Maximum number of sources to process in one run
    """

    now = timezone.now()
    sources = Source.objects.filter(
        Q(screenshot_date__lte=now - constants.SCREENSHOT_MAX_AGE) |
        Q(screenshot__isnull=True)
    )

    msg = (f'[{timezone.now().isoformat()}] Processing {sources.count()} '
           f'sources for screenshots.')
    print(msg)
    logger.info(msg)

    for source in sources:
        msg = (f'[{timezone.now().isoformat()}] Generating screenshot for '
               f'{source.id}')
        print(msg)

        logger.info(msg)
        screenshot_name = '{pk}_{date}.png'.format(
            pk=source.pk, date=now.strftime('%d%m%Y')
        )

        # relative path is expected in FileField.name
        relative_path = os.path.join(constants.SCREENSHOT_DIR,
                                     screenshot_name)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        try:
            r = requests.get(settings.MANET_URL, params={
                'url': source.main_seed.url,
                'width': constants.SCREENSHOT_RESOLUTION_X,
                'height': constants.SCREENSHOT_RESOLUTION_Y,
                'clipRect': constants.SCREENSHOT_RECTANGLE,
                'format': 'png',
                'delay': 1000,
            }, timeout=15)  # 15 second timeout
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            msg = (f'[{timezone.now().isoformat()}] Screenshot timeout/error '
                   f'for {source.id}: {str(e)}')
            print(msg)
            logger.warning(msg)
            continue  # Skip this source and continue with the next one

        if r.status_code == requests.codes.ok:
            try:
                with open(absolute_path, 'wb') as screen:
                    screen.write(r.content)

                source.screenshot.name = relative_path
                source.screenshot_date = now
                source.save()
            except (OSError, IOError) as e:
                msg = (f'[{timezone.now().isoformat()}] Failed to save '
                       f'screenshot for {source.id}: {str(e)}')
                print(msg)
                logger.error(msg)
        else:
            msg = (f'[{timezone.now().isoformat()}] Screenshot request failed '
                   f'for {source.id}: HTTP {r.status_code}')
            print(msg)
            logger.warning(msg)

    msg = (f'[{timezone.now().isoformat()}] Screenshot processing completed')
    print(msg)
    logger.info(msg)
