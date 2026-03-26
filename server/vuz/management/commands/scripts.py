import pandas as pd
import os
from django.core.management.base import BaseCommand

from ...models import (
    Main, Vuz, Regions, Districts, Ministries, 
    Program, Training, Discount, Knowledge, UGNP
)


class Command(BaseCommand):
    help = "Загрузка данных из Excel файлов в базу с возможностью дополнения"

    def _check_file_exists(self, file_path, table_name):
        """Проверяет наличие файла и выводит сообщение"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(
                f"Файл не найден, пропускаем: {table_name} ({os.path.basename(file_path)})"
            ))
            return False
        
        self.stdout.write(self.style.NOTICE(
            f"Файл найден: {os.path.basename(file_path)} → загружаем {table_name}"
        ))
        return True

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(__file__)
        data_path = os.path.join(current_dir, "..", "..", "..", "data")

        self.stdout.write(self.style.WARNING("=== Начало загрузки данных ==="))

        # === 1. Справочники (get_or_create — безопасно дополняются) ===
        self.load_ministries(os.path.join(data_path, "Министерства.xlsx"))
        self.load_districts(os.path.join(data_path, "Округа.xlsx"))
        self.load_regions(os.path.join(data_path, "Регионы.xlsx"))
        self.load_programs(os.path.join(data_path, "Программы.xlsx"))
        self.load_training(os.path.join(data_path, "Направления подготовки.xlsx"))
        self.load_vuz(os.path.join(data_path, "Вузы.xlsx"))
        self.load_knowledge(os.path.join(data_path, "Области знаний.xlsx"))
        self.load_ugpn(os.path.join(data_path, "УГНП.xlsx"))

        # === 2. Основные таблицы (дополняются новыми записями) ===
        self.load_main(os.path.join(data_path, "main.xlsx"))
        self.load_discount(os.path.join(data_path, "Скидки.xlsx"))

        self.stdout.write(self.style.SUCCESS("=== Загрузка данных успешно завершена ==="))

    # ====================== СПРАВОЧНИКИ ======================
    def load_ministries(self, file_path):
        if not self._check_file_exists(file_path, "Ministries"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            data = row.dropna().to_dict()
            _, created_flag = Ministries.objects.get_or_create(
                id_ministry=data["id_ministry"], defaults=data
            )
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Ministries: +{created} новых"))

    def load_districts(self, file_path):
        if not self._check_file_exists(file_path, "Districts"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            data = row.dropna().to_dict()
            _, created_flag = Districts.objects.get_or_create(
                id_district=data["id_district"], defaults=data
            )
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Districts: +{created} новых"))

    def load_regions(self, file_path):
        if not self._check_file_exists(file_path, "Regions"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            try:
                district = Districts.objects.get(id_district=row["id_district"])
                data = row.dropna().to_dict()
                data["id_district"] = district
                _, created_flag = Regions.objects.get_or_create(
                    id_region=data["id_region"], defaults=data
                )
                if created_flag:
                    created += 1
            except Districts.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"District не найден: {row.get('id_district')}"))
        self.stdout.write(self.style.SUCCESS(f"Regions: +{created} новых"))

    def load_programs(self, file_path):
        if not self._check_file_exists(file_path, "Programs"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            data = row.dropna().to_dict()
            _, created_flag = Program.objects.get_or_create(
                progid=data["progid"], defaults=data
            )
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Programs: +{created} новых"))

    def load_training(self, file_path):
        if not self._check_file_exists(file_path, "Training"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            try:
                program = Program.objects.get(progid=row["progid"])
                data = row.dropna().to_dict()
                data["progid"] = program
                _, created_flag = Training.objects.get_or_create(
                    fieldid=data["fieldid"], defaults=data
                )
                if created_flag:
                    created += 1
            except Program.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Program не найден: progid={row.get('progid')}"))
        self.stdout.write(self.style.SUCCESS(f"Training: +{created} новых"))

    def load_vuz(self, file_path):
        if not self._check_file_exists(file_path, "Vuz"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            try:
                district = Districts.objects.get(id_district=row["id_district"])
                region = Regions.objects.get(id_region=row["id_region"])
                ministry = Ministries.objects.get(id_ministry=row["id_ministry"])

                data = row.dropna().to_dict()
                data["id_district"] = district
                data["id_region"] = region
                data["id_ministry"] = ministry

                _, created_flag = Vuz.objects.get_or_create(
                    id_listedu=data["id_listedu"],
                    id_parent=data["id_parent"],
                    defaults=data
                )
                if created_flag:
                    created += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Ошибка Vuz {row.get('id_listedu')}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"Vuz: +{created} новых"))

    def load_knowledge(self, file_path):
        if not self._check_file_exists(file_path, "Knowledge"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            data = row.dropna().to_dict()
            _, created_flag = Knowledge.objects.get_or_create(
                fieldeduid=data["fieldeduid"], defaults=data
            )
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Knowledge: +{created} новых"))

    def load_ugpn(self, file_path):
        if not self._check_file_exists(file_path, "UGNP"):
            return
        df = pd.read_excel(file_path)
        created = 0
        for _, row in df.iterrows():
            try:
                knowledge = Knowledge.objects.get(fieldeduid=row["fieldeduid"])
                data = row.dropna().to_dict()
                data["fieldeduid"] = knowledge
                _, created_flag = UGNP.objects.get_or_create(
                    ugnp=data["ugnp"], defaults=data
                )
                if created_flag:
                    created += 1
            except Knowledge.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Knowledge не найден: fieldeduid={row.get('fieldeduid')}"))
        self.stdout.write(self.style.SUCCESS(f"UGNP: +{created} новых"))

    # ====================== ОСНОВНЫЕ ТАБЛИЦЫ ======================
    def load_main(self, file_path):
        """Дополняет таблицу Main только новыми записями"""
        if not self._check_file_exists(file_path, "Main"):
            return

        df = pd.read_excel(file_path)
        main_objects = []
        created_count = 0
        skipped_count = 0
        error_count = 0

        existing_ids = set(Main.objects.values_list('id', flat=True))

        for _, row in df.iterrows():
            try:
                vuz_instance = Vuz.objects.get(
                    id_listedu=row["id_listedu"], 
                    id_parent=row["id_parent"]
                )
                prog_instance = Program.objects.get(progid=row["progid"])
                training_instance = Training.objects.get(fieldid=row["fieldid"])

                main_data = row.dropna().to_dict()

                del main_data["id_listedu"]
                del main_data["id_parent"]

                main_data["id_vuz"] = vuz_instance
                main_data["progid"] = prog_instance
                main_data["fieldid"] = training_instance

                main_obj = Main(**main_data)

                if main_obj.id not in existing_ids:
                    main_objects.append(main_obj)
                    created_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"Ошибка Main (id={row.get('id')}): {e}"
                ))
                error_count += 1

        if main_objects:
            Main.objects.bulk_create(main_objects, batch_size=2000)

        self.stdout.write(self.style.SUCCESS(
            f"Main: +{created_count} новых | {skipped_count} пропущено | {error_count} ошибок"
        ))

    def load_discount(self, file_path):
        """Дополняет таблицу Discount только новыми записями"""
        if not self._check_file_exists(file_path, "Discount"):
            return

        df = pd.read_excel(file_path)
        
        discount_objects = []
        created_count = 0
        skipped_count = 0
        error_count = 0

        # Множество id_main, для которых уже есть запись в Discount
        existing_id_main = set(Discount.objects.values_list('id_main_id', flat=True))

        for _, row in df.iterrows():
            try:
                # Находим Main по полю id_main из Excel
                main_id = int(row["id_main"])                    # важно: приводим к int
                main_instance = Main.objects.get(id=main_id)

                # Подготавливаем данные
                discount_data = row.dropna().to_dict()

                # Удаляем id_main из данных, т.к. мы его передаём через ForeignKey
                discount_data.pop("id_main", None)

                discount_data["id_main"] = main_instance

                # Создаём объект модели
                discount_obj = Discount(**discount_data)

                # Проверяем, есть ли уже скидка для этого id_main
                if main_id not in existing_id_main:
                    discount_objects.append(discount_obj)
                    created_count += 1
                else:
                    skipped_count += 1

            except Main.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Main не найден для id_main = {row.get('id_main')}")
                )
                error_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Ошибка при обработке Discount (id_main={row.get('id_main')}): {e}")
                )
                error_count += 1

        # Массовое добавление новых записей
        if discount_objects:
            Discount.objects.bulk_create(discount_objects, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f"bulk_create Discount: добавлено {len(discount_objects)} записей"))

        self.stdout.write(self.style.SUCCESS(
            f"Discount: +{created_count} новых | {skipped_count} уже существовало | {error_count} ошибок"
        ))