from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_completed_and_seed_skills'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='title',
            new_name='project_name',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='open_seats',
            new_name='maximum_collaborators',
        ),
    ]






