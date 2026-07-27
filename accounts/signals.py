import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.fields.files import ImageFieldFile, FileField

@receiver(post_delete)
def delete_file_on_model_delete(sender, instance, **kwargs):
    """
    Project ထဲရှိ မည်သည့် Model တွင်မဆို ImageField / FileField ပါရှိပြီး 
    Record ဖျက်လိုက်ပါက Media ဖိုင်ပါ တစ်ပါတည်း အလိုအလျောက် ပျက်စေရန်
    """
    for field in sender._meta.fields:
        if isinstance(field, (ImageFieldFile, FileField)) or isinstance(getattr(instance, field.name, None), (ImageFieldFile, FileField)):
            file_field = getattr(instance, field.name, None)
            if file_field and hasattr(file_field, 'path'):
                try:
                    if os.path.isfile(file_field.path):
                        os.remove(file_field.path)
                except Exception:
                    pass