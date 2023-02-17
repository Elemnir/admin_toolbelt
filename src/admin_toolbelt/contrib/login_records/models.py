import random

from django.db  import models


def generate_token():
    return ''.join([
        random.choice('abcdefghijfklmnopqrstuvwxyz0123456789') 
        for i in range(24)
    ])


class LoginRecordToken(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    last_used   = models.DateTimeField(null=True, blank=True)
    expires     = models.DateTimeField(null=True, blank=True)
    name        = models.CharField(max_length=32)
    token       = models.CharField(
        max_length=32, unique=True, default=generate_token
    )

    def __str__(self):
        return '{} - {}'.format(self.name, self.created)


class LoginRecord(models.Model):
    when        = models.DateTimeField()
    host        = models.CharField(max_length=64)
    service     = models.CharField(max_length=32)
    method      = models.CharField(max_length=32, blank=True, null=True)
    user        = models.CharField(max_length=32)
    fromhost    = models.CharField(max_length=256)

    def __str__(self):
        return '{} - {}'.format(self.user, self.when)
