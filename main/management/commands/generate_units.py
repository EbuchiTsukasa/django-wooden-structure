# main/management/commands/generate_units.py

from django.core.management.base import BaseCommand
from main.models import Unit

class Command(BaseCommand):
    help = 'Unitモデルにダミーデータ（100件・深さ5の木構造）を作成'

    def handle(self, *args, **kwargs):
        Unit.objects.all().delete()  # まず全消し（必要に応じて）

        nodes_per_level = [1, 3, 4, 5, 5]  # 各階層のノード数（例）
        unit_counter = 1
        parent_ids = [None]  # ルートのparentはNone

        all_units = []
        for depth, count in enumerate(nodes_per_level):
            new_parent_ids = []
            for parent_id in parent_ids:
                for i in range(count):
                    name = f"U_d{depth}_n{unit_counter}"
                    unit = Unit(name=name, parent_id=parent_id)
                    unit.save()
                    self.stdout.write(self.style.SUCCESS(f"Created: {name} pk={unit.pk}, parent={parent_id}"))
                    new_parent_ids.append(unit.pk)
                    unit_counter += 1
                    if unit_counter > 100:
                        break
                if unit_counter > 100:
                    break
            parent_ids = new_parent_ids
            if unit_counter > 100:
                break

        self.stdout.write(self.style.SUCCESS('ダミーデータ作成完了'))
