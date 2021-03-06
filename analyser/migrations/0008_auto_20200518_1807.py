# Generated by Django 3.0.6 on 2020-05-18 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyser', '0007_auto_20200511_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapingresult',
            name='is_last_google_article',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scrapingresult',
            name='analysis_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scraping_results', to='analyser.AnalysisJob'),
        ),
    ]
