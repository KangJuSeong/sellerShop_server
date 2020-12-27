from cryptography.fernet import InvalidToken
from django.db import models

from utils.functions import encrypt, decrypt


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SerializeQuerySet(models.query.QuerySet):
    def serialize(self):
        results = []
        for obj in self:
            results.append(obj.serialize())
        return results


class SerializeModel(BaseModel):

    objects = SerializeQuerySet.as_manager()

    class Meta:
        abstract = True

    def serialize(self, excludes=None, force_includes=None):
        if force_includes is None:
            force_includes = []
        if excludes is None:
            excludes = ['updated_at']
        results = {}
        fields = self._meta.get_fields()
        for field in fields:
            key = field.name
            if key in excludes and key not in force_includes:
                continue
            value = getattr(self, key)
            if field.choices:
                value = getattr(self, 'get_%s_display' % key)()
            results[key] = value
        return results


def encrypt_field_value(current_fields, base_fields):
    for field in base_fields:
        try:
            current_fields[field] = encrypt(current_fields[field])
        except KeyError:
            pass
    return current_fields


class CryptoModelQuerySet(models.query.QuerySet):
    def get(self, *args, **kwargs):
        kwargs = encrypt_field_value(kwargs, self.model.CRYPTO_FIELDS)
        return super().get(**kwargs)

    def filter(self, *args, **kwargs):
        kwargs = encrypt_field_value(kwargs, self.model.CRYPTO_FIELDS)
        return super().filter(**kwargs)

    def update(self, *args, **kwargs):
        kwargs = encrypt_field_value(kwargs, self.model.CRYPTO_FIELDS)
        return super().update(**kwargs)


class CryptoModelManager(models.Manager.from_queryset(CryptoModelQuerySet)):
    def create(self, *args, **kwargs):
        kwargs = encrypt_field_value(kwargs, self.model.CRYPTO_FIELDS)
        return super(CryptoModelManager, self).create(*args, **kwargs)


class CryptoModel(BaseModel):
    objects = CryptoModelManager()

    CRYPTO_FIELDS = tuple()

    def __init__(self, *args, **kwargs):
        super(CryptoModel, self).__init__(*args, **kwargs)
        for field in self.CRYPTO_FIELDS:
            setattr(self, '_%s' % field, getattr(self, field))

    def __getattribute__(self, item):
        crypto_fields = super(CryptoModel, self).__getattribute__('CRYPTO_FIELDS')
        if item[1:] in crypto_fields:
            try:
                return decrypt(super(CryptoModel, self).__getattribute__(item[1:]))
            except InvalidToken:
                pass
        return super(CryptoModel, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if value and key in self.CRYPTO_FIELDS:
            try:
                _ = decrypt(value)
            except InvalidToken:
                value = encrypt(value)
        super(CryptoModel, self).__setattr__(key, value)

    class Meta:
        abstract = True
