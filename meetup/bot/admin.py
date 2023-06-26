from django.contrib import admin
from .models import Message, Speaker, User


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('guest', 'speaker', 'message')


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'subject', 'delay')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'name')
    fields = ('tg_id', 'name')  # Добавьте эту строку


