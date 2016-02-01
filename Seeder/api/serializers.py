import source
import publishers

from rest_framework.serializers import ModelSerializer


class SubCategorySerializer(ModelSerializer):
    class Meta:
        model = source.models.SubCategory
        fields = ['id', 'name', 'subcategory_id']


class CategorySerializer(ModelSerializer):
    sub_categories = SubCategorySerializer(source='subcategory_set', many=True)

    class Meta:
        model = source.models.Category
        fields = ['id', 'name', 'sub_categories']


class ContactPersonSerializer(ModelSerializer):
    class Meta:
        model = publishers.models.ContactPerson


class PublisherSerializer(ModelSerializer):
    contacts = ContactPersonSerializer(
        source='contactperson_set',
        many=True
    )

    class Meta:
        model = publishers.models.Publisher


class SourceSerializer(ModelSerializer):
    publisher = PublisherSerializer()

    class Meta:
        model = source.models.Source
        exclude = ['created_by', 'owner']
