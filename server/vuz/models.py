from django.db import models
from django.db.models import UniqueConstraint


class Program(models.Model):
    progid = models.IntegerField(primary_key=True)
    progname = models.CharField(max_length=25)

    class Meta:
        db_table = 'Program'

class Training(models.Model):
    fieldid = models.CharField(max_length=8, primary_key=True)
    fieldname = models.CharField(max_length=200)
    progid = models.ForeignKey(Program, on_delete=models.CASCADE, db_column='progid')

    class Meta:
        db_table = 'Training'

class Ministries(models.Model):
    id_ministry = models.IntegerField(primary_key=True)
    ministry = models.CharField(max_length=150)

    class Meta:
        db_table = 'Ministries'


class Districts(models.Model):
    id_district = models.IntegerField(primary_key=True)
    district = models.CharField(max_length=20)

    class Meta:
        db_table = 'Districts'


class Regions(models.Model):
    id_region = models.IntegerField(primary_key=True)
    region = models.CharField(max_length=40)
    id_district = models.ForeignKey(Districts, on_delete=models.CASCADE, db_column='id_district')

    class Meta:
        db_table = 'Regions'


class Vuz(models.Model):
    id_listedu = models.IntegerField()
    id_parent = models.IntegerField()
    fullname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=200)
    rector = models.CharField(max_length=50)
    id_region = models.ForeignKey(Regions, on_delete=models.CASCADE, db_column='id_region')
    id_district = models.ForeignKey(Districts, on_delete=models.CASCADE, db_column='id_district')
    id_ministry = models.ForeignKey(Ministries, on_delete=models.CASCADE, db_column='id_ministry')

    class Meta:
        db_table = 'Vuz'
        unique_together = (('id_listedu', 'id_parent'),)

class Main(models.Model):
    id = models.AutoField(primary_key=True)
    id_vuz = models.ForeignKey(Vuz, on_delete=models.CASCADE, default=0, db_column='id_vuz')
    progid = models.ForeignKey(Program, on_delete=models.CASCADE, db_column='progid')
    fieldid = models.ForeignKey(Training, on_delete=models.CASCADE, db_column='fieldid')
    profile = models.CharField(max_length=100)
    formname = models.CharField(max_length=7)
    course1 = models.IntegerField(null=True)
    course2 = models.IntegerField(null=True)
    course3 = models.IntegerField(null=True)
    course4 = models.IntegerField(null=True)
    course5 = models.IntegerField(null=True)
    course6 = models.IntegerField(null=True)
    course7 = models.IntegerField(null=True)

    class Meta:
        db_table = 'Main'



