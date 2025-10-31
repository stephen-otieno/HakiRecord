from django.contrib import admin
from .models import *

class StatementAdmin(admin.ModelAdmin):
    list_display = ('ob_number','last_name', 'id_number', 'incident_type', 'incident_location', 'incident_date')
    search_fields = ('ob_number', 'id_number', 'last_name', 'incident_location')
    list_filter = ('recorded_at',)
    readonly_fields = [f.name for f in Statement._meta.fields]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'contact_email')
    search_fields = ('contact_name', 'contact_email')

admin.site.register(Statement,StatementAdmin)
admin.site.register(Contact, ContactAdmin)





