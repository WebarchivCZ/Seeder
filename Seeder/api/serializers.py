from rest_framework.serializers import ModelSerializer

from source.models import Category, SubCategory


class SubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'subcategory_id')


class CategorySerializer(ModelSerializer):
    sub_categories = SubCategorySerializer(source='subcategory_set', many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'sub_categories')
