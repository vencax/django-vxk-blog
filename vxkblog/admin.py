from django.contrib import admin
from django.db.models import Q

from models import Entry

class EntryAdmin(admin.ModelAdmin):

    """
    Class for specifiying the options for administering the
    vxk-blog.models.Entry model via the Django admin.
    """

    date_hierarchy = 'published_at'
    list_display = ('title', 'author', 'published_at', 'status', 'allow_new_comment')
    list_filter = ('published_at', 'author', 'status')
    prepopulated_fields = {'slug': ('title',)}
    radio_fields = {'status': admin.HORIZONTAL}
    search_fields = ('title', 'standfirst', 'content')

#    class Media:
#        css = {
#            'all': ('apps/files/css/files.css',),
#        }

    def queryset(self, request):
        """
        Return the queryset to use in the admin list view.  Superusers
        can see all entries, other users can see all their own entries
        and all entries by other authors with a status other than
        private.
        """
        if request.user.is_superuser:
            return Entry.objects.all()
        return Entry.objects.filter(
            Q(author=request.user) | Q(status=Entry.DRAFT_STATUS))

admin.site.register(Entry, EntryAdmin)
