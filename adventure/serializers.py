import logging

from rest_framework import serializers

from adventure import models as adv_models
from authentication import models as auth_models
from filemanager import models as file_models
from filemanager.serializers import CATEGORIES

log = logging.getLogger(__name__)


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)


#
class CreatePaymentChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = adv_models.PaymentChannel
        fields = ['name', 'account', 'is_bank']


class ListPaymentChannelSerializer(CreatePaymentChannelSerializer):
    class Meta:
        model = adv_models.PaymentChannel
        fields = CreatePaymentChannelSerializer.Meta.fields + ['id', 'date_created', ]


class CreateImageSerializer(serializers.Serializer):
    image_id = serializers.UUIDField(required=True)
    category = serializers.ChoiceField(required=True, choices=CATEGORIES)


class CreateAdventureSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    payment_channel = serializers.ListField(required=True)
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
    class Meta:
        model = adv_models.Adventure
        fields = ['id', 'title', 'reference_number', 'adventure_status', 'date_created']


class AdventureDetailSerializer(ListAdventureSerializer):
    created_by = serializers.SerializerMethodField('get_created_by')
    payment_channel = serializers.SerializerMethodField('get_payment_channel')

    class Meta:
        model = adv_models.Adventure
        fields = ListAdventureSerializer.Meta.fields + [
            'created_by',
            'description',
            'start_date',
            'end_date',
            'slots',
            'payment_channel',
        ]

    def get_created_by(self, obj):
        created_by = obj.created_by
        try:
            request = self.context.get('request')
            author = auth_models.User.objects.get(id=created_by)
            author_details = {
                "names": author.full_name,
                "phone_number": author.phone_number,
                "email": author.email,
                "profile_photo": None,
            }
            profile = file_models.Poster.objects.filter(id=author.profile_photo)
            if profile:
                profile_inst = profile.first()
                url = request.build_absolute_uri(profile_inst.poster.url)
                author_details.update({
                    "profile_photo": url
                })

            return author_details
        except Exception as e:
            log.error(e)
            return None

    def get_payment_channel(self, obj):
        try:
            payment_channels = obj.payment_channel.all()
            channels = []
            for channel in payment_channels:
                channels.append({
                    "id": channel.id,
                    "name": channel.name,
                    "account": channel.account,
                    "is_bank": channel.is_bank
                })
            return channels
        except Exception as e:
            log.error(e)
            return []