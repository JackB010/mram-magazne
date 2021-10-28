
import os
import random
import secrets
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from PIL import Image
from uuid import uuid4
# import pytz


def img_func_profile(instance, filename):
    ext = filename.split('.')[-1]
    upload_to = f"profile/{instance.user}/{instance.user.id}/"
    filename = f'{instance.user}_{secrets.randbits(32)}.{ext}'
    return os.path.join(upload_to, filename)


class Profile(models.Model):

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    ip = models.GenericIPAddressField(null=True, editable=False)
    first_ip = models.GenericIPAddressField(editable=False, null=True)
    country = CountryField(_('البلد'), blank=True)
    # country = models.CharField(_('البلد'), blank=True,
    #                            max_length=2, choices=pytz.country_names.items())
    # country = models.CharField( _('البلد'), blank=True, choices=COUNTRIES.items(), max_length=30)

    bio = models.TextField(_('المواصفات الشخصية'), blank=True)
    user = models.OneToOneField(get_user_model(),
                                on_delete=models.CASCADE,
                                related_name='profile'
                                )
    super_profile = models.BooleanField(default=False)
    photo = models.ImageField(_('صورة'),
                              default='default/default_profile.png', upload_to=img_func_profile)
    created = models.DateTimeField(_("كتب في "), auto_now_add=True)
    updated = models.DateTimeField(_("عدل في"), auto_now=True)
    website = models.URLField(_('موقع إلكتوني'), blank=True)

    class Meta:
        ordering = ['-created']

    def clean(self, *args, **kwargs):
        print(self.photo.height )
        if self.photo.height <= 200 and self.photo.width <= 200:
            raise ValidationError(
                _('{} size does not match').format(self.photo.name))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        size = (300, 300)
        img = Image.open(self.photo.path)
        img.thumbnail(size)
        img.save(self.photo.path)

    def __str__(self):
        return f"{self.user}--profile"


class ResetPassword(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    code = models.CharField(max_length=7, unique=True, editable=False)
    email = models.EmailField(_("Email"), max_length=254, blank=True)
    username = models.CharField(_("Username"), max_length=254, blank=True)

    created = models.DateTimeField(_("Created"), auto_now=True)
    checked = models.BooleanField(_("Checked"), default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if (self.email and self.username) is None:
            raise ValidationError(
                'Should give username or email to reset password ')
        return super().save(*args, **kwargs)

    @property
    def new_code(self):
        self.code = self.generate_code()

    def generate_code(self):
        return random.randint(1000000, 9999999)

    def __str__(self):
        if self.email:
            return f"{self.email} __ {self.username} __ {self.code}"
