import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.db import models
from django.db.models import permalink
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from ckeditor import fields as ckedit_fields
from managers import EntryManager
from django.core.validators import MaxLengthValidator

try:
    DAYS_COMMENTS_ENABLED = settings.DAYS_COMMENTS_ENABLED
except AttributeError:
    DAYS_COMMENTS_ENABLED = 30
    
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^ckeditor\.fields\.RichTextField'])

class Entry(models.Model):

    """An individual entry in the blog."""

    DRAFT_STATUS = 1
    PUBLISHED_STATUS = 2
    PRIVATE_STATUS = 3
    STATUS_CHOICES = (
        (DRAFT_STATUS, _('Draft')),
        (PUBLISHED_STATUS, _('Published')),
        (PRIVATE_STATUS, _('Private'))
    )

    title = models.CharField(verbose_name=_('title'), max_length=64)
    slug = models.SlugField(verbose_name=_('slug'), 
        unique_for_year='published_at')
    standfirst = models.TextField(verbose_name=_('standfirst'), 
        max_length=256, validators=[MaxLengthValidator(256)])
    content = ckedit_fields.RichTextField(verbose_name=_('content'), 
        blank=True)
    author = models.ForeignKey(User)
    created_at = models.DateTimeField(verbose_name=_('created_at'), 
        auto_now_add=True)
    published_at = models.DateTimeField(default=datetime.datetime.now,
        verbose_name=_('date published'))
    updated_at = models.DateTimeField(auto_now=True,
        verbose_name=_('date updated'))
    status = models.SmallIntegerField(verbose_name=_('status'),
        choices=STATUS_CHOICES,
        default=DRAFT_STATUS)
    enable_comments = models.BooleanField(verbose_name=_('enable_comments'),
        default=False)

    objects = EntryManager()

    class Meta:
        get_latest_by = 'published_at'
        ordering = ('-published_at',)
        verbose_name = _('entry')
        verbose_name_plural = _('entries')

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        """Return the canonical URL for a blog entry."""
        from views import entry_detail
        return (entry_detail, (self.published_at.year, self.slug))

    def is_published(self):
        """
        Return true if this entry is published on the site, -- that is,
        the status is "published" and the publishing date is today or
        earlier.
        """
        return (self.status == self.PUBLISHED_STATUS and
            self.published_at <= datetime.datetime.now())

    def allow_new_comment(self):
        """
        Return True if a new comment can be posted for this entry, False
        otherwise.  Comments can be posted if the entry is published
        (i.e. ``status`` isn't draft or private), the
        ``enable_comments`` field is True, the final date for for
        comments has not yet been reached, and the post's published date
        has passed.
        """
        date_for_comments = self.published_at + datetime.timedelta(
            days=DAYS_COMMENTS_ENABLED)
        return (self.is_published() and self.enable_comments and
            datetime.datetime.now() <= date_for_comments)
    allow_new_comment.short_description = _('Comments allowed')
    allow_new_comment.boolean = True

    def get_previous_published_entry(self):
        """
        Return the previous public entry published before the current
        time and date.
        """
        try:
            return self.get_previous_by_published_at(status=self.PUBLISHED_STATUS,
                published_at__lte=datetime.datetime.now)
        except Entry.DoesNotExist:
            return None

    def get_next_published_entry(self):
        """
        Return the next public entry published before the current time
        and date.
        """
        try:
            return self.get_next_by_published_at(status=self.PUBLISHED_STATUS,
                published_at__lte=datetime.datetime.now)
        except Entry.DoesNotExist:
            return None

static_gen_cls_name = 'staticgenerator.middleware.StaticGeneratorMiddleware'

if static_gen_cls_name in settings.MIDDLEWARE_CLASSES:
    from signals import delete_blog_index,\
      clear_stagnant_cache_on_comment_change
    
    signals.post_delete.connect(delete_blog_index, sender=Entry)
    signals.post_save.connect(delete_blog_index, sender=Entry)
    signals.post_delete.connect(clear_stagnant_cache_on_comment_change,
        sender=Comment)
    signals.post_save.connect(clear_stagnant_cache_on_comment_change,
        sender=Comment)
