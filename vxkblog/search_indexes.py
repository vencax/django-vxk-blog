from haystack import indexes
from models import Entry

class EntryIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  author = indexes.CharField(model_attr='author')
  created = indexes.DateTimeField(model_attr='created_at')
  summary = indexes.CharField(model_attr='standfirst')

  def get_model(self):
    return Entry

  def index_queryset(self):
    """Used when the entire index for model is updated."""
    return self.get_model().objects.all()
