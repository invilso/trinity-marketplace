# Generated by Django 4.1.7 on 2023-02-21 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_botuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blocklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=64)),
                ('ip', models.GenericIPAddressField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
