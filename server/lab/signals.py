from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
import os


@receiver(post_migrate)
def generate_api_schema(sender, **kwargs):
    """
    Generate API schema for the models in this app.
    """
    schema_path = os.path.join(os.getcwd(), "schema.yaml")
    try:
        call_command("spectacular", "--file", schema_path)
    except Exception as e:
        print(f"Error generating API schema: {e}")
