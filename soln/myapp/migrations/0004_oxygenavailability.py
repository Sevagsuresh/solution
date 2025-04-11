# myapp/migrations/0004_oxygenavailability.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_dislike'),
    ]

    operations = [
        migrations.CreateModel(
            name='OxygenAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district', models.CharField(choices=[('Thiruvananthapuram', 'Thiruvananthapuram'), ('Kollam', 'Kollam'), ('Pathanamthitta', 'Pathanamthitta'), ('Alappuzha', 'Alappuzha'), ('Kottayam', 'Kottayam'), ('Idukki', 'Idukki'), ('Ernakulam', 'Ernakulam'), ('Thrissur', 'Thrissur'), ('Palakkad', 'Palakkad'), ('Malappuram', 'Malappuram'), ('Kozhikode', 'Kozhikode'), ('Wayanad', 'Wayanad'), ('Kannur', 'Kannur'), ('Kasaragod', 'Kasaragod')], max_length=100, unique=True)),
                ('availability_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('capacity_mt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('demand_mt_per_day', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
