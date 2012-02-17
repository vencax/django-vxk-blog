from django.contrib.auth.decorators import permission_required

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext

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
