# Generated by Django 3.2.12 on 2022-04-01 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=500)),
                ('file', models.FileField(null=True, upload_to='files/', verbose_name='')),
            ],
        ),
    ]
