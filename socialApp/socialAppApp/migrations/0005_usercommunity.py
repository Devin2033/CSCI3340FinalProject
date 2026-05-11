from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialAppApp', '0004_comment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCommunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='socialAppApp.community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_communities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'community')},
            },
        ),
    ]
