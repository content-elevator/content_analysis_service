# Generated by Django 3.0.6 on 2020-05-10 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyser', '0002_analysisjob_analysisresult_tfidfresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisjob',
            name='result',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='analyser.AnalysisResult'),
        ),
    ]