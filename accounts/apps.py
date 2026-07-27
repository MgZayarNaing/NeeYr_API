import sys
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # 1. Signals များကို Load လုပ်ရန် (Server run ချိန်၊ migrate ချိန် အားလုံးအတွက် အလုပ်လုပ်ရန် import ကို အပြင်ဘက်ထုတ်ထားခြင်းက ပိုကောင်းပါတယ်)
        try:
            import accounts.signals
        except ImportError:
            pass

        # 2. makemigrations သို့မဟုတ် အခြား command များ ခေါ်ချိန်တွင် Permission auto-create မဖြစ်အောင် စစ်ပေးခြင်း
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv:
            return

        from accounts.models import UUIDPermission

        DEFAULT_PERMISSIONS = [
            {"name": "Can View Users", "codename": "view_user", "description": "Can view user list"},
            {"name": "Can Create User", "codename": "add_user", "description": "Can create user"},
            {"name": "Can Edit User", "codename": "change_user", "description": "Can edit user"},
            {"name": "Can Delete User", "codename": "delete_user", "description": "Can delete user"},
            {"name": "Can View Groups", "codename": "view_group", "description": "Can view groups"},
            {"name": "Can Manage Groups", "codename": "manage_group", "description": "Can create/edit/delete groups"},
        ]

        try:
            for perm in DEFAULT_PERMISSIONS:
                UUIDPermission.objects.get_or_create(
                    codename=perm["codename"],
                    defaults={
                        "name": perm["name"],
                        "description": perm["description"]
                    }
                )
        except Exception:
            # Table မရှိသေးမီ (Migration မလုပ်ရသေးမီ) error မတက်စေရန်
            pass