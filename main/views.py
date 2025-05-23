from django.shortcuts import render
from django.db import connection
from django.db.models import Q
from django.views import View
from django.views.generic import ListView, TemplateView
import json

from .models import Unit, Closure, OrgChart, UnitHierarchy

from collections import defaultdict

import time


# Create your views here.

class UnitView(ListView):
    model = Unit
    template_name = "main/unit_root_prefetch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["root_unit"] = queryset.filter(parent__isnull=True).first()
        print("root_unitの構築は完了")
        return context

    def get_queryset(self):
        max_depth = 5
        prefetch_key = self.build_prefetch_related(max_depth)
        queryset = Unit.objects.all().prefetch_related(prefetch_key)
        # print("Unitを直接参照した場合の実行計画:", queryset.explain(analyze=True, verbose=True, buffers=True, timing=True, settings=True))
        return queryset
    
    def build_prefetch_related(self, depth, current_depth=1):
        if current_depth > depth:
            return ""
        children_key = "children"
        next_level = self.build_prefetch_related(depth, current_depth + 1)
        if next_level:
            return f"{children_key}__{next_level}"
        return children_key
    
class UnitRecursiveView(View):
    model = Unit
    template_name = 'main/unit_root_recursive.html'

    def get(self, request, *args, **kwargs):
        # 再帰クエリで全件を一括取得
        units = self.fetch_units_tree()
        print("ユニットの取得は完了")
        # unitsを用いてツリー構造を組み立て
        root_unit = self.build_tree(units)
        print("ツリー構造の取得は完了")
        return render(request, self.template_name, {'root_unit': root_unit})

    def fetch_units_tree(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE root AS (
                    SELECT id, name, parent_id
                    FROM main_unit
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT child.id, child.name, child.parent_id
                    FROM root
                    JOIN main_unit AS child
                        ON root.id = child.parent_id
                )
                SELECT id, name, parent_id FROM root
            """)
            rows = cursor.fetchall()
        # カラム名を合わせる
        columns = ["id", "name", "parent_id"]
        return [dict(zip(columns, row)) for row in rows]

    def build_tree(self, units):
        units_dict = {unit['id']: unit for unit in units}
        for unit in units:
            unit['children'] = []
        root = None
        for unit in units:
            if unit['parent_id'] is None:
                root = unit
            else:
                # 親を探す
                parent = units_dict.get(unit['parent_id'])
                if parent:
                    parent['children'].append(unit)
        return root

    
class UnitHierarchyView(ListView):
    model = UnitHierarchy

    def dispatch(self, request, *args, **kwargs):
        self._start_total = time.perf_counter()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        start_total = time.perf_counter()

        start = time.perf_counter()
        context = super().get_context_data(**kwargs)
        print(f"context=super().get_context_data() took {time.perf_counter() - start:.4f} seconds")
        units = list(UnitHierarchy.objects.all())


        # parent_id→子リスト
        start = time.perf_counter()
        children_dict = defaultdict(list)
        for u in units:
            children_dict[u.parent_id].append(u)
        print(f"children_dict took {time.perf_counter() - start:.4f} seconds")

        # 再帰的なツリー構造を作る関数
        def build_tree(unit):
            return {
                'id': unit.id,
                'name': unit.name,
                'children': [build_tree(child) for child in children_dict[unit.id]]
            }

        root_unit = next(u for u in units if u.parent_id is None)
        start = time.perf_counter()
        context["root_unit"] = build_tree(root_unit)
        context["root_unit_json"] = json.dumps(context["root_unit"])
        print(f"making root_unit took {time.perf_counter() - start:.4f} seconds")
        print("contextを返します")
        return context
    
    def render_to_response(self, context, **response_kwargs):
        # テンプレートレスポンスを生成（まだ描画されていない）
        response = super().render_to_response(context, **response_kwargs)

        # テンプレート描画処理を強制的に実行してタイミングを測定
        start = time.perf_counter()
        response = response.render()
        render_time = time.perf_counter() - start
        total_time = time.perf_counter() - self._start_total

        print(f"[Time] Template rendering: {render_time:.4f} sec")
        print(f"[Time] Total ListView time: {total_time:.4f} sec")

        return response
class OrgChartView(TemplateView):

    template_name = 'main/orgchart_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tree'] = self.build_tree()
        return context
    
    def build_tree(self):
        children_map = defaultdict(list)

        # 子供関係を取得
        direct_relations = Closure.objects.filter(depth=1).select_related('parent', 'child')
        for rel in direct_relations:
            children_map[rel.parent_id].append(rel.child)

        # ルートノード
        all_descendant_ids = Closure.objects.filter(depth=1).values_list('child_id', flat=True)
        root_orgcharts = OrgChart.objects.exclude(id__in=all_descendant_ids)

        def build_node(org):

            return {
                'id': org.id,
                'name': org.name,
                'children': [build_node(child) for child in children_map.get(org.id, [])]
            }
        
        
        built_node = [build_node(org) for org in root_orgcharts]
        
        return built_node