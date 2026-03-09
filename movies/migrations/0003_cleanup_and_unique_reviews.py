from django.db import migrations
from django.conf import settings


def remove_duplicate_reviews(apps, schema_editor):
    """Keep only the latest review per user/movie pair."""
    Review = apps.get_model('movies', 'Review')
    seen = set()
    to_delete = []
    for r in Review.objects.order_by('-created_at'):
        key = (r.user_id, r.movie_id)
        if key in seen:
            to_delete.append(r.id)
        else:
            seen.add(key)
    deleted = Review.objects.filter(id__in=to_delete).delete()
    print(f"\nRemoved {deleted[0]} duplicate review(s).")


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_review_updated_at_alter_review_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_reviews, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('user', 'movie')},
        ),
    ]
