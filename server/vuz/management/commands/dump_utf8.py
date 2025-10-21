# management/commands/dump_utf8.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Dump data with correct UTF-8 encoding'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', default='db_dump.json')
        parser.add_argument('--indent', type=int, default=2)

    def handle(self, *args, **options):
        output_file = options['output']
        indent = options['indent']
        
        with open(output_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata', stdout=f, indent=indent)
        
        self.stdout.write(self.style.SUCCESS(f'Dump created: {output_file}'))