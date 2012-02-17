import re

from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.hashcompat import md5_constructor
from vxkblog.models import Entry
from django.utils.translation import ugettext as _

register = template.Library()


DEFAULT_GRAVATAR_IMAGE = '%score/img/avatar.png' % settings.MEDIA_URL
GRAVATAR_RATING = 'r'
PULLQUOTE_RE = re.compile(r'<blockquote\sclass="pullquote">.+?</blockquote>',
    re.UNICODE)


@register.simple_tag
def gravatarimg(email, size=32):
    email_hash = md5_constructor(email).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s?s=%d&r=%s&d=%s' % (email_hash,
        size, GRAVATAR_RATING, DEFAULT_GRAVATAR_IMAGE)
    return '<img alt="Gravatar" height="%s" src="%s" width="%s" />' % (size,
        escape(url), size)
    
def _get_nav_button_content(id, label, entry):
    """ Help method for blognavigation tag """
    return unicode(
        '<p class="%s">%s: <a href="%s">%s</a> <span>%s</span></p>' %\
            (id, label, entry.get_absolute_url(), entry.title, 
             entry.published_at)
        )
        
@register.simple_tag
def blognavigation(blog):
    return nextblog(blog) + prevblog(blog)

@register.simple_tag
def nextblog(blog):
    next = blog.get_next_published_entry()
    if next:
        return _get_nav_button_content('nextentry', _('Next'), next)
    return ''

@register.inclusion_tag('blog/newestblogs.html')
def newestblogs(count=5):
    return {'blogs': Entry.objects.all()[:count]}

@register.inclusion_tag('blog/yearswithblogs.html')
def yearswithblogs():
    return {'years': Entry.objects.published().dates('published_at', 'year')}
        
@register.simple_tag
def prevblog(blog):
    prev = blog.get_previous_published_entry()
    if prev:
        retval += _get_nav_button_content('previousentry', _('Previous'), prev)
    return ''

@register.filter
def strip_pullquotes(copy):
    """
    Strip pullquotes from the given blog entry copy.  This is used
    in the Atom feed template, as the pullquotes are confusing and out
    of place without CSS applied.

    As an example, given the string::

    >>> s = '<p>Lorem <a href="#">ipsum</a>.</p><blockquote class="pullquote"><p>Dolor sit amet</p></blockquote><p>consectetur adipisicing elit</p>'
    >>> strip_pullquotes(s)
    '<p>Lorem <a href="#">ipsum</a>.</p><p>consectetur adipisicing elit</p>'
    >>> s = '<blockquote><p>Lorem ipsum</p></blockquote><blockquote class="pullquote"><p>Dolor sit amet</p></blockquote><blockquote><p>consectetur adipisicing elit</p></blockquote>'
    >>> strip_pullquotes(s)
    '<blockquote><p>Lorem ipsum</p></blockquote><blockquote><p>consectetur adipisicing elit</p></blockquote>'
    """
    return PULLQUOTE_RE.sub('', copy)
