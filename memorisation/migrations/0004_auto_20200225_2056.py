# Generated by Django 3.0.3 on 2020-02-25 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0002_auto_20200208_2259'),
        ('memorisation', '0003_auto_20200205_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='practice',
            name='card',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='words.Card'),
        ),
    ]
