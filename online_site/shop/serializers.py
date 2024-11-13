from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'age',
                  'phone_number', 'status')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user
    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверные учетные данные')

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'



class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =['first_name','last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
        fields = ['category_name']



class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class ReviewSerializers(serializers.ModelSerializer):
    created_date = serializers.DateField(format='%d-%m-%Y-%H-%M')

    class Meta:
        model = Review
        fields = '__all__'

        def get_average_rating(self, obj):
            return obj.get_average_rating()

class ProductListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    date = serializers.DateField(format='%d-%m-%Y')
    class Meta:
            model = Product
            fields = ['id','product_name', 'average_rating', 'price','owner',
                    'description','date']


    def get_average_rating(self, obj):
            return obj.get_average_rating()


class ProductDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    product_photo = ProductPhotosSerializer(many=True,read_only=True )
    category = CategorySerializer()
    ratings =RatingSerializer(many=True,read_only=True )
    reviews =RatingSerializer(many=True,read_only=True )
    date =serializers.DateField(format='%d-%m-%Y')
    owner =UserProfileSimpleSerializer()




    class Meta:
        model = Product
        fields = ['product_name','category',' description','price','product_video',
                  'product_photo', 'active', 'average_rating','ratings','reviews', 'owner','date']

        def get_average_rating(self, obj):
            return obj.get_average_rating()




class CartItemSerialazer(serializers.ModelSerializer):
        product = ProductListSerializer()
        product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),write_only=True,source='product')

        class Meta:
            model = CarItem
            fields = ['id','product','product_id','quantity','get_total_price']

class CartSerialazer(serializers.ModelSerializer):
    items = CartItemSerialazer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()



