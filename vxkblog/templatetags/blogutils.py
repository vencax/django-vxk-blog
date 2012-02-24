import re

from django import template
from vxkblog.models import Entry
from django.utils.translation import ugettext as _

register = template.Library()

PULLQUOTE_RE = re.compile(r'<blockquote\sclass="pullquote">.+?</blockquote>',
    re.UNICODE)
    
def _get_nav_button_content(clsid, label, entry):
    """ Help method for blognavigation tag """
    return unicode(
        '<p class="%s">%s: <a href="%s">%s</a> <span>%s</span></p>' %\
            (clsid, label, entry.get_absolute_url(), entry.title, 
             entry.published_at)
        )
        
@register.simple_tag
def blognavigation(blog):
    return nextblog(blog) + prevblog(blog)

@register.simple_tag
def nextblog(blog):
    nextbl = blog.get_next_published_entry()
    if nextbl:
        return _get_nav_button_content('nextentry', _('Next'), nextbl)
    return ''

@register.simple_tag
def bloginfo(blog, length_standfirst=None):
    blogtitle = blog.title
    if length_standfirst:
        standfirst = blog.standfirst[:length_standfirst] + '...'
    else:
        standfirst = blog.standfirst
    return """
        <div>
            <a href="%s">%s</a>
            %s
        </div>
        <p class="standfirst">%s</p>
    """ % (blog.get_absolute_url(), blogtitle, 
           blogmeta(blog), standfirst)

@register.simple_tag    
def blogmeta(blog):
    return """
    <span class="author">%s</span>,
    <span class="publishdate">%s</span>
    """ % (unicode(blog.author), blog.created_at)

@register.inclusion_tag('blog/tag_newestblogs.html')
def newestblogs(count=5):
    return {'blogs': Entry.objects.all()[:count]}

@register.inclusion_tag('blog/tag_yearswithblogs.html')
def yearswithblogs():
    return {'years': Entry.objects.published().dates('published_at', 'year')}
        
@register.simple_tag
def prevblog(blog):
    prev = blog.get_previous_published_entry()
    if prev:
        return _get_nav_button_content('previousentry', _('Previous'), prev)
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
