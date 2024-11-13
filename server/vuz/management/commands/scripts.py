import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import (
Main,
Vuz,
Regions,
Districts,
Ministries,
Program,
Training
)

current_dir = os.path.dirname(__file__)
data_path = os.path.join(current_dir, '..', '..', '..', 'data')

file_names = {
    'Программы.xlsx': Program,
    'Направления подготовки.xlsx': Training,
    'Министерства.xlsx': Ministries,
    'Округа.xlsx': Districts,
    'Регионы.xlsx': Regions,
    'Вузы.xlsx': Vuz,
    'main.xlsx': Main,
}

class Command(BaseCommand):
    help = 'Load data from Excel files into the SQLite database'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for file_name, model in file_names.items():
                print(file_name, model)
                file_path = os.path.join(data_path, file_name)
                data = pd.read_excel(file_path)

                for _, row in data.iterrows():
                    row = row.fillna(value=pd.NA)

                    if model == Training:
                        program_id = row.get('progid')
                        if program_id is not None:
                            program_instance = Program.objects.get(progid=program_id)
                            instance = Training(progid=program_instance,
                                                **{k: v for k, v in row.items() if k != 'progid'})

                    elif model == Regions:
                        district_id = row.get('id_district')
                        if district_id is not None:
                            district_instance = Districts.objects.get(id_district=district_id)
                            instance = Regions(id_district=district_instance,
                                               **{k: v for k, v in row.items() if k != 'id_district'})

                    elif model == Vuz:
                        region_id = row.get('id_region')
                        district_id = row.get('id_district')
                        ministry_id = row.get('id_ministry')
                        if region_id is not None and district_id is not None and ministry_id is not None:
                            region_instance = Regions.objects.get(id_region=region_id)
                            district_instance = Districts.objects.get(id_district=district_id)
                            ministry_instance = Ministries.objects.get(id_ministry=ministry_id)
                            instance = Vuz(
                                id_region=region_instance,
                                id_district=district_instance,
                                id_ministry=ministry_instance,
                                **{k: v for k, v in row.items() if k not in ['id_region', 'id_district', 'id_ministry']}
                            )



                    elif model == Main:
                        listedu_id = row.get('id_listedu')
                        parent_id = row.get('id_parent')
                        field_id = row.get('fieldid')
                        program_id = row.get('progid')
                        # Убедитесь, что все необходимые поля не равны None
                        if listedu_id is not None and parent_id is not None and field_id is not None and program_id is not None:
                            try:
                                vuz_instance_listedu = Vuz.objects.get(id=listedu_id)
                                vuz_instance_parent = Vuz.objects.get(id=parent_id)
                                training_instance = Training.objects.get(fieldid=field_id)
                                program_instance = Program.objects.get(progid=program_id)
                                # Заполнение значений по умолчанию для курсов, если они NA
                                courses = {f'course{i}': row.get(f'course{i}', 0) for i in range(1, 8)}
                                courses = {k: (v if v is not pd.NA else 0) for k, v in
                                           courses.items()}  # Заменяем NA на 0

                                instance = Main(
                                    id_listedu=vuz_instance_listedu,
                                    id_parent=vuz_instance_parent,
                                    progid=program_instance,
                                    fieldid=training_instance,
                                    **courses  # Распаковка словаря курсов
                                )
                                instance.save()
                            except (Vuz.DoesNotExist, Training.DoesNotExist, Program.DoesNotExist) as e:
                                print(f"One of the referenced entities does not exist. Skipping this row: {e}.")
                            except Exception as e:
                                print(f"Error saving Main: {e}. Skipping this row.")
                    else:
                        instance = model(**row.to_dict())
                    instance.save()

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))