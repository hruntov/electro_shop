from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_options_alter_orderitem_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_reference',
            field=models.CharField(blank=True, null=True),
        ),
    ]
