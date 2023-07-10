import uuid
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Generate random URLs and append to a file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url', type=str, help=(
                'Base URL, specify incl. http:// and without an ending slash. '
                'E.g. "http://google.com"'
            ), required=False)
        parser.add_argument(
            '-n', '--num', type=int, help='Number of seeds to generate',
              required=True)
        parser.add_argument(
            '-o', '--output', type=str, help=(
                'Output file path with reference to the Seeder/Seeder folder. '
                'E.g. "testseeds.txt"'
            ), required=True)

    def handle(self, *args, **options):
        base_url = (options['base_url'] if options['base_url']
                    else f"http://{uuid.uuid4()}.com")
        num = options['num']
        output_file = options['output']

        try:
            with open(output_file, 'a') as f:
                for i in range(num):
                    f.write(f"{base_url}/{i}\n")
        except IOError as e:
            raise CommandError('Could not write to file') from e

        self.stdout.write(self.style.SUCCESS(
            f'Successfully generated {num} seeds to {output_file}'))
