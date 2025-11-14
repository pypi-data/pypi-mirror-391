
from django.db.models import Manager
from rest_framework import generics

from .base import BaseAPIView


class TranslatedListView(generics.ListAPIView, BaseAPIView):
    manager: Manager

    def get_queryset(self):
        self.update_lang()
        return self.manager.all()
