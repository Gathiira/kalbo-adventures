import logging

from rest_framework import serializers

from adventure import models as adv_models
from authentication import models as auth_models
from filemanager import models as file_models
from filemanager.serializers import CATEGORIES

log = logging.getLogger(__name__)


def get_user_details(user, request):
    user_details = {
        "userid": user.id,
        "names": user.full_name,
        "phone_number": user.phone_number,
        "email": user.email,
        "profile_photo": None,
    }
    profile = file_models.Poster.objects.filter(id=user.profile_photo)
    if profile:
        profile_inst = profile.first()
        url = request.build_absolute_uri(profile_inst.poster.url)
        user_details.update({
            "profile_photo": url
        })
    return user_details


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)


#
class CreatePaymentChannelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    account = serializers.CharField(required=True)
    is_bank = serializers.BooleanField(required=True)
    description = serializers.CharField(required=True)


class ListPaymentChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = adv_models.PaymentChannel
        fields = ['id', 'name', 'account', 'description', 'is_bank']


class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = adv_models.Category
        fields = ['name']


class ListCategorySerializer(CreateCategorySerializer):
    class Meta:
        model = adv_models.Category
        fields = CreateCategorySerializer.Meta.fields + ['id', 'date_created', ]


class CreateImageSerializer(serializers.Serializer):
    image_id = serializers.UUIDField(required=True)
    category = serializers.ChoiceField(required=True, choices=CATEGORIES)


class CreateAdventureSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    payment_channel = serializers.ListField(required=True)
    organizers = serializers.ListField(required=True)
    category = serializers.ListField(required=True)
    slots = serializers.IntegerField(required=True)
    inclusives = serializers.ListField(required=True)
    adult = serializers.IntegerField(required=True)
    child = serializers.IntegerField(required=True)
    images = serializers.ListField(
        required=True,
        child=CreateImageSerializer()
    )

    def validate(self, obj):
        payment_channels = set(obj['payment_channel'])
        payment_instances = adv_models.PaymentChannel.objects.filter(id__in=payment_channels)
        if len(payment_channels) != payment_instances.count():
            raise serializers.ValidationError('Invalid payment channel')
        obj.update({
            "payment_instances": payment_instances
        })
        images = [image['image_id'] for image in obj['images']]
        images_instances = file_models.Poster.objects.filter(id__in=images)
        if len(images) != images_instances.count():
            raise serializers.ValidationError('Invalid images provided')

        # validate organizers
        organizers = set(obj['organizers'])
        organizer_instances = auth_models.User.objects.filter(id__in=organizers)
        if len(organizers) != organizer_instances.count():
            raise serializers.ValidationError('Invalid organizers')

        obj.update({
            "organizers_instances": organizer_instances
        })

        # validate categories
        categories = set(obj['category'])
        category_instances = adv_models.Category.objects.filter(id__in=categories)
        if len(categories) != category_instances.count():
            raise serializers.ValidationError('Invalid Category(s)')

        obj.update({
            "category_instances": category_instances
        })

        return obj


class UpdateAdventureSerializer(CreateAdventureSerializer):
    request = serializers.CharField(required=True)


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')

    class Meta:
        model = adv_models.Image
        fields = ['image_id', 'image', 'category']

    def get_image(self, obj):
        try:
            request = self.context.get('request')
            image_id = obj.image_id
            image = file_models.Poster.objects.get(id=image_id)
            url = request.build_absolute_uri(image.poster.url)
            return url
        except Exception as e:
            log.error(e)
            return []


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = adv_models.Price
        fields = ['adult', 'child']


class ListAdventureSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField('get_categories')
    main_image = serializers.SerializerMethodField('get_main_image')

    class Meta:
        model = adv_models.Adventure
        fields = [
            'id', 'title',
            'description',
            'reference_number',
            'adventure_status',
            'categories',
            'start_date',
            'end_date',
            'main_image',
            'date_created']

    def get_categories(self, obj):
        try:
            categories = obj.category.all()
            all_categories = []
            for category in categories:
                all_categories.append({
                    "id": category.id,
                    "name": category.name
                })
            return all_categories
        except Exception as e:
            log.error(e)
            return []

    def get_main_image(self, obj):
        images = obj.images.filter(category='MAIN')
        images_details = ImageSerializer(
            images, many=True, context=self.context).data
        return images_details


class AdventureDetailSerializer(ListAdventureSerializer):
    created_by = serializers.SerializerMethodField('get_created_by')
    organizers = serializers.SerializerMethodField('get_organizers')
    payment_channel = serializers.SerializerMethodField('get_payment_channel')

    class Meta:
        model = adv_models.Adventure
        fields = ListAdventureSerializer.Meta.fields + [
            'created_by',
            'organizers',
            'slots',
            'payment_channel',
        ]

    def get_created_by(self, obj):
        created_by = obj.created_by
        try:
            request = self.context.get('request')
            author = auth_models.User.objects.get(id=created_by)
            author_details = get_user_details(author, request)
            return author_details
        except Exception as e:
            log.error(e)
            return None

    def get_organizers(self, obj):
        try:
            organizers = obj.organizer.all()
            request = self.context.get('request')
            organizer_details = []
            for organizer in organizers:
                user_details = get_user_details(organizer, request)
                organizer_details.append(user_details)
            return organizer_details
        except Exception as e:
            log.error(e)
            return None

    def get_payment_channel(self, obj):
        try:
            payment_channels = obj.payment_channel.all()
            channels = ListPaymentChannelSerializer(payment_channels, many=True)
            return channels.data
        except Exception as e:
            log.error(e)
            return []