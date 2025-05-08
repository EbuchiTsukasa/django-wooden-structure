from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import connection

# Create your models here.

# 隣接リストモデル
class Unit(models.Model):
    name = models.CharField(max_length=20)
    parent = models.ForeignKey("Unit", blank=True, null=True, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "main_unit"

class UnitHierarchy(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    parent_id = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        managed = False  # Djangoがこのモデルを管理しないように設定
        db_table = "unit_hierarchy"  # マテリアライズドビューを参照

@receiver([post_save, post_delete], sender=Unit)
def refresh_materialized_view(sender, **kwargs):
    """
    Refresh the materialized view `unit_hierarchy` whenever
    the `main_unit` table is modified.
    """
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW unit_hierarchy;")

# 閉包テーブルモデル
class OrgChart(models.Model):
    name = models.CharField(max_length=30)
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Closure(models.Model):
    parent = models.ForeignKey(OrgChart, on_delete=models.CASCADE, related_name="closure_parent")
    child = models.ForeignKey(OrgChart, on_delete=models.CASCADE, related_name="closure_child")
    depth = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.parent}-{self.child}"