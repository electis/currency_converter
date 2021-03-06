# Generated by Django 3.0 on 2019-12-10 23:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_settings_last_error'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_from', models.DecimalField(decimal_places=8, default=0, max_digits=18)),
                ('amount_to', models.DecimalField(decimal_places=8, default=0, max_digits=18)),
                ('user_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
