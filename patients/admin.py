from django.contrib import admin

from .models import PatientRecord


@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ("full_name", "date_of_birth", "email", "glucose", "haemoglobin", "cholesterol", "updated_at")
    search_fields = ("full_name", "email")
