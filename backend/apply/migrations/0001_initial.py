# Generated by Django 4.0.3 on 2022-03-14 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('job_key', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('is_applying', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')], max_length=5, null=True)),
                ('notes', models.TextField(null=True)),
            ],
        ),
    ]