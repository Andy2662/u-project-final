# Generated by Django 3.2.1 on 2021-06-15 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacion', '0021_torre_torre_measure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torre',
            name='operador',
            field=models.CharField(choices=[('Entel', 'Entel'), ('Viva', 'Viva'), ('Tigo', 'Tigo')], max_length=200),
        ),
    ]
