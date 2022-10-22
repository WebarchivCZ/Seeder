from django.core.management.base import BaseCommand
from harvests.models import Harvest


class Command(BaseCommand):
    help = ("Print an overview table of essential information about all "
            "Harvests in the database.\nTo pring the table using plaintext "
            "instead of unicode checkmarks and crosses, use the --plaintext "
            "option.")

    def add_arguments(self, parser):
        parser.add_argument(
            '--plaintext',
            action='store_true',
            help="Print 'YES' and 'X' instead of unicode checkmarks/crosses",
        )

    def handle(self, *args, **options):
        # Print the legend of what each column means
        self.stdout.write(self.style.HTTP_INFO("""
Column description:
- PK: Primary key (ID)
- TITLE: Full title of the harvest
- HAS_TC: Does the Harvest have any linked TopicCollections?
- HAS_SERIALS: Does the Harvest have any specified serials frequencies?
- HAS_TC_FREQ: Does the Harvest have any specified TopicCollection frequencies?
- ARCHIVE_IT: Does the Harvest have the ArchiveIt flag?
- TESTS: Does the Harvest have the Tests flag?
        """))
        # Decide which output to use
        if options.get("plaintext"):
            TICK = "YES"
            CROSS = "X"
        else:
            TICK = "✅"
            CROSS = "❌"
        out = ""
        harvests = Harvest.objects.all().order_by("created")
        cols = ["pk", "title", "has_tc", "has_serials", "has_tc_freq",
                "archive_it", "tests"]
        data = {x: [] for x in cols}
        for harvest in harvests:
            data["pk"].append(str(harvest.pk))
            data["title"].append(harvest.title)
            data["has_tc"].append(
                TICK if harvest.topic_collections.exists() else CROSS)
            data["has_serials"].append(
                TICK if len(harvest.target_frequency or []) > 0 else CROSS)
            data["has_tc_freq"].append(
                TICK if len(harvest.topic_collection_frequency or []) > 0
                else CROSS)
            data["archive_it"].append(
                TICK if harvest.archive_it else CROSS)
            data["tests"].append(
                TICK if harvest.tests else CROSS)
        # Compute max lengths of each column; either data or column name
        ms = {key: max(max(map(len, val)), len(key))
              for key, val in data.items()}
        LEN_UNDERLINE = sum(ms.values()) + len(cols) * 4
        # If using unicode symbols, each takes up 2 spaces instead of 1
        if not options.get("plaintext", False):
            for col in cols[2:]:  # PK and TITLE stay the same
                ms[col] -= 1
        # Print out column names and underline
        for col in cols:
            out += f"| {col.upper():^{ms[col]}} |"
        out += "\n" + LEN_UNDERLINE * "-" + "\n"
        # Print out data
        for i in range(len(data["pk"])):
            for col in cols:
                x = data[col][i]
                # Align PK and TITLE to left, rest is centered
                if col in ["pk", "title"]:
                    out += f"| {x:<{ms[col]}} |"
                else:
                    out += f"| {x:^{ms[col]}} |"
            out += "\n"
        self.stdout.write(out)
