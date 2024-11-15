import pandas as pd
import os
from django.core.management.base import BaseCommand

from ...models import (
Main,
Vuz,
Regions,
Districts,
Ministries,
Program,
Training
)


class Command(BaseCommand):
    help = 'Load data from Excel files into database'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(__file__)
        data_path = os.path.join(current_dir, '..', '..', '..', 'data')

        # Сначала загружаем министерства, округа и регионы
        self.load_ministries(os.path.join(data_path, 'Министерства.xlsx'))
        self.load_districts(os.path.join(data_path, 'Округа.xlsx'))
        self.load_regions(os.path.join(data_path, 'Регионы.xlsx'))

        # Затем загружаем программы, направления и вузы
        self.load_programs(os.path.join(data_path, 'Программы.xlsx'))
        self.load_training(os.path.join(data_path, 'Направления подготовки.xlsx'))
        self.load_vuz(os.path.join(data_path, 'Вузы.xlsx'))

        # Наконец, загружаем главную таблицу `Main`
        self.load_main(os.path.join(data_path, 'main.xlsx'))

    def load_ministries(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            Ministries.objects.create(**row.dropna().to_dict())
        self.stdout.write(self.style.SUCCESS('Successfully loaded Ministries'))

    def load_districts(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            Districts.objects.create(**row.dropna().to_dict())
        self.stdout.write(self.style.SUCCESS('Successfully loaded Districts'))

    def load_regions(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            District = Districts.objects.get(
                id_district=row['id_district'])  # Предполагается, что id_district у вас есть в Excel
            region_data = row.dropna().to_dict()
            region_data['id_district'] = District
            Regions.objects.create(**region_data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded Regions'))

    def load_programs(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            Program.objects.create(**row.dropna().to_dict())
        self.stdout.write(self.style.SUCCESS('Successfully loaded Programs'))

    def load_training(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            program = Program.objects.get(progid=row['progid'])  # Предполагается, что progid у вас есть в Excel
            training_data = row.dropna().to_dict()
            training_data['progid'] = program
            Training.objects.create(**training_data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded Training'))

    def load_vuz(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            District = Districts.objects.get(id_district=row['id_district'])
            Region = Regions.objects.get(id_region=row['id_region'])
            Ministry = Ministries.objects.get(id_ministry=row['id_ministry'])

            vuz_data = row.dropna().to_dict()
            vuz_data['id_district'] = District
            vuz_data['id_region'] = Region
            vuz_data['id_ministry'] = Ministry
            Vuz.objects.create(**vuz_data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded Vuz'))

    def load_main(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            try:
                # Получаем необходимые ссылки из Vuz
                vuz_instance = Vuz.objects.get(id_listedu=row['id_listedu'], id_parent=row['id_parent'])
                # Получаем информацию для других полей, если нужно
                Prog = Program.objects.get(progid=row['progid'])  # Измените на соответствующее название столбца
                Training_instance = Training.objects.get(
                    fieldid=row['fieldid'])  # Измените на соответствующее название столбца

                # Подготовка данных для Main
                main_data = row.dropna().to_dict()
                main_data['id_vuz'] = vuz_instance
                del main_data['id_listedu']
                del main_data['id_parent']
                main_data['progid'] = Prog
                main_data['fieldid'] = Training_instance

                # Создаем запись в Main
                Main.objects.create(**main_data)

            except Vuz.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f'Vuz not found for id_listedu={row["id_listedu"]} and id_parent={row["id_parent"]}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error loading Main: {e} for row: {row}'))
        self.stdout.write(self.style.SUCCESS('Successfully loaded Main'))