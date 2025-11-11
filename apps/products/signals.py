"""
Django Signals for automatic audit logging
Tracks all CREATE, UPDATE, DELETE operations on products models
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
import json

from apps.products.models import Brand, Category, Collection, Product
from apps.logs.models import AuditLog


def get_request_user():
    """Get current request user from middleware (if available)"""
    try:
        from threading import current_thread
        thread = current_thread()
        if hasattr(thread, 'request'):
            return thread.request.user if thread.request.user.is_authenticated else None
    except:
        pass
    return None


def model_to_dict(instance):
    """Convert model instance to dictionary"""
    from datetime import datetime, date
    from decimal import Decimal

    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        # Handle special types
        if hasattr(value, 'pk'):
            value = value.pk
        elif isinstance(value, (datetime, date)):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = float(value)
        data[field.name] = value
    return data


@receiver(post_save, sender=Brand)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Collection)
@receiver(post_save, sender=Product)
def log_model_save(sender, instance, created, **kwargs):
    """Log CREATE and UPDATE operations"""
    user = get_request_user()

    action = AuditLog.ActionChoices.CREATE if created else AuditLog.ActionChoices.UPDATE
    table_name = sender._meta.db_table

    new_data = model_to_dict(instance)

    AuditLog.objects.create(
        user=user,
        action=action,
        table_name=table_name,
        record_id=instance.pk,
        new_data=new_data,
        old_data=None if created else {}  # For UPDATE, we don't track old data by default
    )


@receiver(pre_delete, sender=Brand)
@receiver(pre_delete, sender=Category)
@receiver(pre_delete, sender=Collection)
@receiver(pre_delete, sender=Product)
def log_model_delete(sender, instance, **kwargs):
    """Log DELETE operations"""
    user = get_request_user()

    table_name = sender._meta.db_table
    old_data = model_to_dict(instance)

    AuditLog.objects.create(
        user=user,
        action=AuditLog.ActionChoices.DELETE,
        table_name=table_name,
        record_id=instance.pk,
        old_data=old_data,
        new_data=None
    )
