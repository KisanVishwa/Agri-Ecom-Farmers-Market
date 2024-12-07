from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='attachment',
            field=models.FileField(
                blank=True,
                help_text='File attachment for the message',
                null=True,
                upload_to='chat_attachments/%Y/%m/%d/'
            ),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='image_url',
            field=models.URLField(
                blank=True,
                help_text='URL for image content',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='link_preview',
            field=models.JSONField(
                blank=True,
                help_text='Preview data for shared links',
                null=True
            ),
        ),
    ] 