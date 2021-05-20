# Generated by Django 3.2 on 2021-05-19 13:51

from django.db import migrations
import management.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_codelisting_content_itembase_latex_pdf_picture_puretext_videolink'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('order',)},
        ),
        migrations.AlterModelOptions(
            name='coursedescriptionblock',
            options={'ordering': ('order',)},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='content',
            name='order',
            field=management.fields.OrderField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursedescriptionblock',
            name='order',
            field=management.fields.OrderField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='module',
            name='order',
            field=management.fields.OrderField(blank=True, default=0),
            preserve_default=False,
        ),
    ]