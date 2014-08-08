# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255, verbose_name=b'Request Type', choices=[(b'feature', b'Feature'), (b'bug', b'Bug'), (b'comment', b'Comment')])),
                ('comment', models.TextField(verbose_name=b'Comment Details')),
                ('submitted', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Submitted')),
                ('is_complete', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': (b'-submitted',),
                'db_table': b'feature_requests',
            },
            bases=(models.Model,),
        ),
    ]
