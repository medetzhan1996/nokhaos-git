# Generated by Django 3.0.8 on 2020-11-06 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20201021_0757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]