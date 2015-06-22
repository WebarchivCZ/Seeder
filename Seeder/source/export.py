import os

import models
import constants

from django.conf import settings
from datetime import datetime


def export_seeds():
    now = datetime.now()
    now_formatted = now.strftime('%d.%m.%Y %H:%M')
    for freq, freq_name in dict(constants.SOURCE_FREQUENCY_PER_YEAR).items():
        urls = models.Seed.objects.filter(
            source__state=constants.STATE_RUNNING,
            source__frequency=freq,
            state=constants.SEED_STATE_INCLUDE).values_list('url', flat=True)
        url_list = [url.encode('utf-8') for url in urls]

        filename = 'seeds_{freq}x_{now}.txt'.format(
            freq=freq,
            now=now_formatted)

        file_path = os.path.join(settings.SEEDS_EXPORT_DIR, filename)
        abs_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        with open(abs_file_path, 'w') as export_file:
            initial_lines = [
                '# Seed list generated: {0}'.format(now_formatted),
                '# Seeds count: {0}'.format(len(urls)),
                '# Seed type: {0}'.format(freq_name)
            ]

            lines = initial_lines + url_list
            export_file.write('\n'.join(lines))

        export = models.SeedExport(frequency=freq)
        export.export_file.name = file_path
        export.save()
