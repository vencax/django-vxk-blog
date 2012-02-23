from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from models import Entry


site = Site.objects.get_current()


class LatestEntries(Feed):
    """An Atom 1.0 feed of the latest ten public entries from the blog."""

    feed_type = Atom1Feed
    title = u'%s: %s' % (site.name, _('Latest blogs'))
    title_template = 'feeds/latest_title.html'
    description_template = 'feeds/latest_description.html'

    def link(self, item):
        return reverse('blog_entry_index')

    def items(self):
        return Entry.objects.published().select_related()[:10]

    def item_author_name(self, item):
        return item.author.first_name or item.author.username

    def item_pubdate(self, item):
        return item.published_at
