# Generated by Django 3.2.12 on 2022-05-03 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_alter_imagestorage_imagefile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagestorage',
            name='imagefile',
            field=models.FileField(null=True, upload_to='media'),
        ),
    ]
