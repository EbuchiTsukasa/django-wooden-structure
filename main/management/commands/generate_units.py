from django.core.management.base import BaseCommand
from main.models import Unit

from django.db import connection

class Command(BaseCommand):
    help = 'Unitモデルにダミーデータ（10万件・多階層木構造）を作成'

    def handle(self, *args, **kwargs):
        # --- 小分け削除（修正版） ---
        batch_size = 1000
        total = Unit.objects.count()
        deleted = 0
        while True:
            ids = list(Unit.objects.values_list('id', flat=True)[:batch_size])
            if not ids:
                break
            Unit.objects.filter(id__in=ids).delete()
            deleted += len(ids)
            self.stdout.write(self.style.NOTICE(f'{deleted}/{total} 件 削除...'))
        self.stdout.write(self.style.SUCCESS('全件削除完了'))

        # --- ダミーデータ作成 ---
        total_units = 1_000_000
        nodes_per_level = 5  # 1階層ごとの子ノード数
        max_depth = 10        # 深さ

        unit_counter = 1
        parent_units = [None]  # ルートの親はNone

        for depth in range(max_depth):
            created_units = []
            for parent in parent_units:
                for _ in range(nodes_per_level):
                    if unit_counter > total_units:
                        break
                    name = f"U_d{depth}_n{unit_counter}"
                    unit = Unit(name=name, parent_id=parent)
                    created_units.append(unit)
                    unit_counter += 1
                if unit_counter > total_units:
                    break
            Unit.objects.bulk_create(created_units)
            if depth == 0:
                parent_units = list(Unit.objects.filter(parent__isnull=True).values_list('pk', flat=True))
            else:
                parent_units = list(Unit.objects.filter(parent_id__in=parent_units).values_list('pk', flat=True))
            if unit_counter > total_units:
                break

        self.stdout.write(self.style.SUCCESS('ダミーデータ作成完了'))

        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW unit_hierarchy;")
        self.stdout.write(self.style.SUCCESS('unit_hierarchyマテビューもリフレッシュ完了'))
