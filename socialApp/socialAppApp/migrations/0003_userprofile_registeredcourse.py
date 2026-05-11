from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialAppApp', '0002_savedpost_postvote'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('major', models.CharField(blank=True, max_length=100)),
                ('year', models.CharField(blank=True, choices=[('freshman', 'Freshman'), ('sophomore', 'Sophomore'), ('junior', 'Junior'), ('senior', 'Senior'), ('graduate', 'Graduate'), ('phd', 'PhD'), ('other', 'Other')], max_length=20)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('research_interests', models.CharField(blank=True, max_length=300)),
                ('linkedin', models.URLField(blank=True)),
                ('github', models.URLField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RegisteredCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=20)),
                ('course_name', models.CharField(max_length=150)),
                ('semester', models.CharField(blank=True, max_length=30)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['course_code'],
                'unique_together': {('user', 'course_code', 'semester')},
            },
        ),
    ]
