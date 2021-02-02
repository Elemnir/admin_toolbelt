import admin_toolbelt.contrib.login_records.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoginRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField()),
                ('host', models.CharField(max_length=64)),
                ('service', models.CharField(max_length=32)),
                ('method', models.CharField(blank=True, max_length=32, null=True)),
                ('user', models.CharField(max_length=32)),
                ('fromhost', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='LoginRecordToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=32)),
                ('token', models.CharField(default=admin_toolbelt.contrib.login_records.models.generate_token, max_length=32, unique=True)),
            ],
        ),
    ]
