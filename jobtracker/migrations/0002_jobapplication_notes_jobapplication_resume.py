# Generated by Django 5.2.2 on 2025-06-09 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobtracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resumes/'),
        ),
    ]
