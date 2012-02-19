from django.contrib.auth.decorators import permission_required

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentTypeManager, ContentType
from django.conf import settings
if 'tagging' in settings.INSTALLED_APPS:
    from tagging.models import TaggedItem, Tag

from models import Entry

def entry_archive_year(request, year):
    """Output the published blog entries for a given year."""
    entries = get_list_or_404(Entry.objects.published(), published_at__year=year)
    years_with_entries = Entry.objects.published().dates('published_at', 'year')
    entries_by_month = dict.fromkeys(range(1, 13), 0)
    for entry in entries:
        entries_by_month[entry.published_at.month] += 1
    context = {
        'year': year,
        'entries': entries,
        'entries_by_month': entries_by_month,
        'max_entries_per_month': max(entries_by_month.values()),
        'years_with_entries': years_with_entries,
    }
    return render_to_response('blog/entry_archive_year.html', context,
        RequestContext(request))

def entry_tag_list(request, tagid):
    """Output the published blog entries for a given tag."""
    tag = get_object_or_404(Tag, id=int(tagid))
    entry_c_type = ContentType.objects.get_for_model(Entry)
    taggedObjs = TaggedItem.objects.filter(tag=tag, content_type=entry_c_type)
    blogz = Entry.objects.filter(
        id__in=taggedObjs.values_list('object_id', flat=True))
    context = {
        'blogs' : blogz,
        'tag' : tag
    }
    return render_to_response('blog/entry_by_tag.html', context,
        RequestContext(request))

def entry_detail(request, year, slug):
    """
    Output a full individual entry; this is the view for an entry's
    permalink.
    """
    entry = get_object_or_404(Entry.objects.published(), published_at__year=year,
        slug=slug)
    context = {'entry': entry}
    return render_to_response('blog/entry_detail.html', context,
        RequestContext(request))


@permission_required('blog.change_entry', '/admin/')
def entry_preview(request, year, slug):
    """
    Allows draft entries to be viewed as if they were publicly available
    on the site.  Draft entries with a ``published_at`` date in the
    future are visible too.  The same template as the ``entry_detail``
    view is used.
    """
    entry = get_object_or_404(Entry.objects.filter(status=Entry.DRAFT_STATUS),
        published_at__year=year, slug=slug)
    context = {'entry': entry}
    return render_to_response('blog/entry_detail.html', context,
        RequestContext(request))
