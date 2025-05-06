from django.db import models

# Create your models here.

# 隣接リストモデル
class Unit(models.Model):
    name = models.CharField(max_length=20)
    parent = models.ForeignKey("Unit", blank=True, null=True, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return self.name

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