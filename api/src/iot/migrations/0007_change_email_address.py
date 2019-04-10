from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0006_auto_20190116_1544'),
    ]

    operations = [
        migrations.RunSQL("""
UPDATE iot_person SET email='secretariaatcto@amsterdam.nl' WHERE email='ddjonge@ggd.amsterdam.nl';
"""), ]
