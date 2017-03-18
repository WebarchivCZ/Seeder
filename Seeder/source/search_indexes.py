from haystack import indexes
from elasticstack.fields import CharField

from . import models


class SourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = CharField(document=True, model_attr='search_blob', analyzer='czech_hunspell')

    def get_model(self):
        return models.Source
