from django.contrib import admin
from .models import Artifact, PaymentTransaction

admin.site.register(Artifact)
admin.site.register(PaymentTransaction)
