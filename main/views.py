from django.shortcuts import render
from django.db.models import Q
from django.views.generic import ListView, TemplateView

from .models import Unit, Closure, OrgChart, UnitHierarchy

from collections import defaultdict


# Create your views here.

# class UnitView(ListView):
#     model = Unit

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         queryset = self.get_queryset()
#         context["root_unit"] = queryset.filter(parent__isnull=True).first()
#         return context

#     def get_queryset(self):
#         max_depth = 5
#         prefetch_key = self.build_prefetch_related(max_depth)
#         queryset = Unit.objects.all().prefetch_related(prefetch_key)
#         return queryset
    
#     def build_prefetch_related(self, depth, current_depth=1):
#         if current_depth > depth:
#             return ""
#         children_key = "children"
#         next_level = self.build_prefetch_related(depth, current_depth + 1)
#         if next_level:
#             return f"{children_key}__{next_level}"
#         return children_key
    
class UnitView(ListView):
    model = UnitHierarchy

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        units = list(UnitHierarchy.objects.all())

        # parent_id→子リスト
        children_dict = defaultdict(list)
        for u in units:
            children_dict[u.parent_id].append(u)

        # 再帰的なツリー構造を作る関数
        def build_tree(unit):
            return {
                'id': unit.id,
                'name': unit.name,
                'children': [build_tree(child) for child in children_dict[unit.id]]
            }

        root_unit = next(u for u in units if u.parent_id is None)
        context["root_unit"] = build_tree(root_unit)
        return context
    
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