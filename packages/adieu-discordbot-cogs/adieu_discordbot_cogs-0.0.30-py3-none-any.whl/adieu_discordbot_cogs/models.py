"""
App Models
Create your models in here
"""

# Django
from django.db import models


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("force_sync", "Can use force sync"), ("admin_commands", "Can use Admin commands"))
