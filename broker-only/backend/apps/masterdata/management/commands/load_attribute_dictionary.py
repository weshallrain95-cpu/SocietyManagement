from django.core.management.base import BaseCommand, CommandError

from apps.masterdata import dictionary


class Command(BaseCommand):
    help = "Load the Unit Attribute Dictionary from the approved YAML (default) or the review spreadsheet."

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="?", default=str(dictionary.DEFAULT_PATH))
        parser.add_argument("--dict-version", dest="dict_version", default="")
        parser.add_argument("--all-rows", action="store_true", help="xlsx only: include rows not yet approved (dev)")
        parser.add_argument("--write-yaml", help="xlsx only: also write the approved rows to this YAML path")

    def handle(self, path, dict_version, all_rows, write_yaml, **_):
        version = dict_version
        if path.endswith(".xlsx"):
            rows = dictionary.rows_from_xlsx(path, approved_only=not all_rows)
            version = version or "xlsx"
            if write_yaml:
                dictionary.write_yaml(rows, write_yaml, version)
        else:
            try:
                rows, file_version = dictionary.rows_from_yaml(path)
            except FileNotFoundError as e:
                raise CommandError(
                    f"{path} not found. The dictionary is committed only after founder approval; "
                    "for local development load the review spreadsheet with --all-rows."
                ) from e
            version = version or file_version
        created, updated = dictionary.load_rows(rows, version)
        self.stdout.write(self.style.SUCCESS(f"Attribute dictionary {version}: {created} created, {updated} updated"))
