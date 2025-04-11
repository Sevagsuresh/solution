from django.db import migrations

def add_districts(apps, schema_editor):
    OxygenAvailability = apps.get_model('myapp', 'OxygenAvailability')
    districts = [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Idukki", "Ernakulam", "Thrissur",
        "Palakkad", "Malappuram", "Kozhikode", "Wayanad",
        "Kannur", "Kasaragod"
    ]
    for dist in districts:
        OxygenAvailability.objects.create(
            district=dist,
            availability_percent=0,
            capacity_mt=0,
            demand_mt_per_day=0
        )

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_oxygenavailability'),  # replace with correct previous migration
    ]

    operations = [
        migrations.RunPython(add_districts),
    ]
