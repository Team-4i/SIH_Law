from django.db import migrations

def add_initial_articles(apps, schema_editor):
    Article = apps.get_model('matching_card', 'Article')
    articles_data = [
        {
            'number': 14,
            'title': 'Equality before law',
            'description': 'The State shall not deny to any person equality before the law'
        },
        {
            'number': 15,
            'title': 'Prohibition of discrimination',
            'description': 'The State shall not discriminate against any citizen on grounds of religion, race, caste, sex'
        },
        {
            'number': 16,
            'title': 'Equality of opportunity',
            'description': 'There shall be equality of opportunity for all citizens in matters relating to employment'
        },
        {
            'number': 17,
            'title': 'Abolition of Untouchability',
            'description': 'Untouchability is abolished and its practice in any form is forbidden'
        },
        {
            'number': 18,
            'title': 'Abolition of titles',
            'description': 'No title, not being a military or academic distinction, shall be conferred by the State'
        },
        {
            'number': 19,
            'title': 'Protection of certain rights',
            'description': 'All citizens shall have the right to freedom of speech and expression'
        },
        {
            'number': 20,
            'title': 'Protection in respect of conviction for offences',
            'description': 'No person shall be convicted of any offence except for violation of the law in force'
        }
    ]
    
    for article_data in articles_data:
        Article.objects.create(**article_data)

class Migration(migrations.Migration):
    dependencies = [
        ('matching_card', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_articles),
    ]