from haystack import indexes

from . import models


class PublisherIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='search_blob')

    def get_model(self):
        return models.Publisher

class PublisherContactIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='search_blob')

    def get_model(self):
        return models.ContactPerson
