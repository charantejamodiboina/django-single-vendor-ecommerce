from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Payment

def generate_Transaction_id(model_class, prefix='TRANSID'):
    # Retrieve the latest object
    latest_object = model_class.objects.order_by('-Transaction_id').first()

    if latest_object and latest_object.Transaction_id is not None:
        latest_id = latest_object.Transaction_id
    else:
        latest_id = f"{prefix}0000"

    # Extract the numeric part of the latest ID and increment it
    numeric_part = int(latest_id[len(prefix):])
    new_numeric_part = numeric_part + 1

    # Generate the new ID by combining the prefix and the new numeric part
    new_id = f"{prefix}{str(new_numeric_part).zfill(4)}"
    # The zfill method is used to pad the numeric part with zeros to ensure it has the specified length.
    return new_id


@receiver(pre_save, sender=Payment)
def assign_Transaction_id(sender, instance, **kwargs):
    if not instance.Transaction_id:
        instance.Transaction_id = generate_Transaction_id(sender)
