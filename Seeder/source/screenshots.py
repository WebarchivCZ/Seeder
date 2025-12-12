import os
import asyncio
from pathlib import Path

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
    Downloads screenshots for sources that need them using Playwright.
    Failed screenshots are retried at most once a month to avoid wasting
    resources on dead sites.
    """
    now = timezone.now()
    sources = Source.objects.filter(
        Q(screenshot_date__lte=now - constants.SCREENSHOT_MAX_AGE) |
        Q(screenshot__isnull=True) | Q(screenshot="")
    )

    msg = (f'[{timezone.now().isoformat()}] Processing {sources.count()} '
           f'sources for screenshots using Playwright')
    print(msg)
    logger.info(msg)

    # Create screenshots directory if it doesn't exist
    screenshots_dir = os.path.join(
        settings.MEDIA_ROOT, constants.SCREENSHOT_DIR)
    Path(screenshots_dir).mkdir(parents=True, exist_ok=True)

    # Process screenshots using asyncio for better resource management
    asyncio.run(_process_screenshots_async(sources, now))

    msg = (f'[{timezone.now().isoformat()}] Screenshot processing completed')
    print(msg)
    logger.info(msg)


async def _process_screenshots_async(sources, now):
    """
    Process screenshots asynchronously to prevent blocking
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # Launch browser with minimal resource usage
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Don't load images for faster screenshots
                '--disable-javascript',  # Disable JS for faster loading
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-ipc-flooding-protection',
                '--memory-pressure-off',
                '--max_old_space_size=128'
            ]
        )

        try:
            # Process sources with limited concurrency, max 3 concurrent
            semaphore = asyncio.Semaphore(3)

            tasks = []
            for source in sources:
                task = _take_single_screenshot(source, now, browser, semaphore)
                tasks.append(task)

            # Wait for all tasks to complete with timeout
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=1800)  # 30 minute total timeout

        finally:
            await browser.close()


async def _take_single_screenshot(source, now, browser, semaphore):
    """
    Take a single screenshot with resource limits
    """
    async with semaphore:  # Limit concurrent screenshots
        try:
            msg = (f'[{timezone.now().isoformat()}] Generating screenshot for '
                   f'{source.id} ({source.main_seed.url})')
            print(msg)
            logger.info(msg)

            screenshot_name = '{pk}_{date}.png'.format(
                pk=source.pk, date=now.strftime('%Y-%m-%d')
            )

            # relative path is expected in FileField.name
            relative_path = os.path.join(
                constants.SCREENSHOT_DIR, screenshot_name)
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            # Create browser context with specific viewport
            context = await browser.new_context(
                viewport={
                    'width': int(constants.SCREENSHOT_RESOLUTION_X),
                    'height': int(constants.SCREENSHOT_RESOLUTION_Y)
                },
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            page = await context.new_page()

            try:
                # Set timeout for navigation and wait for page load
                page.set_default_timeout(10000)  # 10 second timeout

                # Navigate to the page
                await page.goto(source.main_seed.url,
                                wait_until='domcontentloaded')

                # Take screenshot
                await page.screenshot(
                    path=absolute_path,
                    full_page=False,
                    clip={
                        'x': 0,
                        'y': 0,
                        'width': int(constants.SCREENSHOT_RESOLUTION_X),
                        'height': int(constants.SCREENSHOT_RESOLUTION_Y)
                    }
                )

                # Update source with screenshot info
                source.screenshot.name = relative_path
                source.screenshot_date = now
                source.save()

                msg = (f'[{timezone.now().isoformat()}] Screenshot OK for '
                       f'{source.id}')
                print(msg)
                logger.info(msg)

            except Exception as e:
                # Extract just the error message, not the full traceback
                error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
                msg = (f'[{timezone.now().isoformat()}] Screenshot FAILED for '
                       f'{source.id}: {error_msg}')
                print(msg)
                logger.warning(msg)
                # Set screenshot_date so it's retried after a month
                source.screenshot_date = (now - constants.SCREENSHOT_MAX_AGE
                                          + constants.SCREENSHOT_RETRY_DELTA)
                source.save()

            finally:
                await page.close()
                await context.close()

        except Exception as e:
            # Extract just the error message, not the full traceback
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            msg = (f'[{timezone.now().isoformat()}] Unexpected error for '
                   f'{source.id}: {error_msg}')
            print(msg)
            logger.error(msg)
            # Set screenshot_date so it's retried after a month
            source.screenshot_date = (now - constants.SCREENSHOT_MAX_AGE
                                      + constants.SCREENSHOT_RETRY_DELTA)
            source.save()
