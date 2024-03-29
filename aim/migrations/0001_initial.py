# Generated by Django 3.1.4 on 2020-12-30 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('high', models.DecimalField(decimal_places=3, max_digits=12)),
                ('low', models.DecimalField(decimal_places=3, max_digits=12)),
                ('close', models.DecimalField(decimal_places=3, max_digits=12)),
                ('volume', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=10, unique=True)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('currentprice', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pricelink', to='aim.price')),
            ],
        ),
        migrations.AddField(
            model_name='price',
            name='symbol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aim.symbol'),
        ),
    ]
