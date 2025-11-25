from django.db import migrations, models


def create_skills(apps, schema_editor):
    Skill = apps.get_model('api', 'Skill')
    names = ['cpp', 'js', 'py', 'java', 'lua', 'rust', 'go', 'julia']
    for n in names:
        Skill.objects.get_or_create(name=n)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(create_skills, migrations.RunPython.noop),
    ]
