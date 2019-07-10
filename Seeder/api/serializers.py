import source
import publishers
import blacklists

from rest_framework.serializers import ModelSerializer
from rest_framework.fields import CharField


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
        fields = '__all__'


class SeedSerializer(ModelSerializer):
    class Meta:
        model = source.models.Seed
        exclude = ['source']


class SourceSerializer(ModelSerializer):
    publisher = PublisherSerializer(read_only=True)
    seed = SeedSerializer(source='main_seed')

    mdt = CharField(read_only=True, source='sub_category.subcategory_id')

    class Meta:
        model = source.models.Source
        exclude = ['created_by', 'owner']


class BlacklistSerializer(ModelSerializer):
    class Meta:
        model = blacklists.models.Blacklist
        fields = '__all__'
