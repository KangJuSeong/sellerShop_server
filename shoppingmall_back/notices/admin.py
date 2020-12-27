from django.contrib import admin
from django import forms

from notices.models import Notice

class NoticeForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Notice
        fields = '__all__'

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'content']
    list_display_links = ['title']
    form = NoticeForm