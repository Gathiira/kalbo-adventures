import logging

from django.db import transaction
from rest_framework import filters
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from adventure import models as adv_models
from adventure import serializers as adv_serializers
from sharedservice import utility_functions, time_functions

utility_function = utility_functions
time_function = time_functions

log = logging.getLogger(__name__)


class AdventureViewset(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['reference_number', 'title', 'description', 'organizer__full_name']
    serializer_class = adv_serializers.ListAdventureSerializer

    def get_authenticated_user_id(self):
        user = self.request.user
        return user.id

    def get_permissions(self):
        permission_classes = []
        if self.action == 'list':
            permission_classes = [permissions.AllowAny, ]
        if self.action == 'detail_view':
            permission_classes = [permissions.AllowAny, ]
        if self.action in ['create_adventure',
                           'delete_adventure',
                           'update_adventure',
                           'close_adventure',
                           'cancel_adventure']:
            permission_classes = [permissions.IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        _adventure = self.request.query_params.get('filter')
        if not bool(_adventure):
            _adventure = 'ALL'

        adventure = _adventure.upper()
        if adventure not in ['ALL', 'ONGOING', 'COMPLETE', 'CANCELLED']:
            return []

        if adventure != "ALL":
            queryset = adv_models.Adventure.objects.filter(
                adventure_status__iexact=adventure).order_by('-date_created')
        else:
            queryset = adv_models.Adventure.objects.all().order_by('-date_created')

        return queryset

    def create(self, request, *args, **kwargs):
        return Response()

    def destroy(self, request, *args, **kwargs):
        return Response()

    def retrieve(self, request, *args, **kwargs):
        return Response()

    @action(
        methods=['POST'],
        detail=False,
        url_path='create',
        url_name='create')
    def create_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.CreateAdventureSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            reference_number = utility_function.generate_unique_reference_per_model(
                adv_models.Adventure, size=10
            )
            adv_payload = {
                "reference_number": reference_number,
                "title": payload['title'],
                "adventure_status": 'ONGOING',
                "created_by": self.get_authenticated_user_id(),
                "description": payload['description'],
                "start_date": payload['start_date'],
                "end_date": payload['end_date'],
                "slots": payload['slots'],
            }
            adv_record = adv_models.Adventure.objects.create(**adv_payload)
            #  set payment methods
            validated_data = serializer.validated_data
            payment_instances = validated_data['payment_instances']
            organizers = validated_data['organizers_instances']
            categories = validated_data['category_instances']
            adv_record.payment_channel.set(payment_instances)
            adv_record.organizer.set(organizers)
            adv_record.category.set(categories)
            adv_record.save()

            # create inclusives
            for inclusive in set(payload['inclusives']):
                inc_payload = {
                    "adventure": adv_record,
                    "name": inclusive,
                }
                adv_models.Inclusives.objects.create(**inc_payload)

            # add price
            price_payload = {
                "adventure": adv_record,
                "adult": payload['adult'],
                "child": payload['child'],
            }
            adv_models.Price.objects.create(**price_payload)
            duplicate_images, resp = utility_function.find_duplicates_in_dict(payload['images'], 'image_id')
            if duplicate_images:
                transaction.set_rollback(True)
                return Response(
                    {"details": "Please add unique images"}, status=status.HTTP_400_BAD_REQUEST)

            for image in payload['images']:
                image_payload = {
                    "adventure": adv_record,
                    "image_id": image['image_id'],
                    "category": image['category']
                }
                adv_models.Image.objects.create(**image_payload)

        return Response(
            {"details": "Successfully created an adventure",
             "id": str(adv_record.id)})

    @action(methods=['GET'], detail=False, url_path='detail-view', url_name='detail-view')
    def detail_view(self, request, *args, **kwargs):
        payload = request.query_params.dict()
        serializer = adv_serializers.GenericRequestSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)

        try:
            record = adv_models.Adventure.objects.get(id=payload['request'])
        except Exception as e:
            log.error(e)
            return Response({"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        record_details = adv_serializers.AdventureDetailSerializer(
            record, many=False, context=self.get_serializer_context()).data
        prices = record.prices
        price_details = adv_serializers.PriceSerializer(prices, many=False).data
        record_details.update(price_details)
        inclusives = record.inclusives.all()
        all_inclusives = []
        for inclusive in inclusives:
            all_inclusives.append(inclusive.name)
        record_details.update({"inclusives": all_inclusives})

        images = record.images.all().order_by('category')
        images_details = adv_serializers.ImageSerializer(
            images, many=True,
            context=self.get_serializer_context()).data
        record_details.update({"images": images_details})
        return Response(record_details)

    @action(
        methods=['POST'],
        detail=False,
        url_path='delete',
        url_name='delete')
    def delete_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.GenericRequestSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        obj = adv_models.Adventure.objects.filter(id=payload['request'])
        if obj:
            obj.delete()
            return Response({"details": "Successfully Deleted"})
        else:
            return Response({"details": "Adventure does not exist"})

    @action(
        methods=['POST'],
        detail=False,
        url_path='update',
        url_name='update')
    def update_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.UpdateAdventureSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        try:
            record = adv_models.Adventure.objects.get(id=payload['request'])
        except Exception as e:
            log.error(e)
            return Response({"details": "Adventure does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        for field_name, field_value in payload.items():
            if field_name in ["payment_channel", "inclusives", "images", 'organizers', 'category']:
                continue
            else:
                if hasattr(record, field_name):
                    setattr(record, field_name, field_value)

        validated_data = serializer.validated_data

        record.created_by = self.get_authenticated_user_id()
        record.payment_channel.set(validated_data['payment_instances'])
        record.payment_channel.set(validated_data['organizers_instances'])
        record.category.set(validated_data['category_instances'])
        record.save()

        price = record.prices
        for field_name, field_value in payload.items():
            if hasattr(price, field_name):
                setattr(price, field_name, field_value)
        price.save()
        try:
            images = payload['images']
            if images:
                record.images.all().delete()
                for image in images:
                    image_payload = {
                        "adventure": record,
                        "image_id": image['image_id'],
                        "category": image['category'],
                    }
                    adv_models.Image.objects.create(**image_payload)
        except Exception as e:
            log.error(e)
            pass
        try:
            inclusives = payload['inclusives']
            if inclusives:
                record.inclusives.all().delete()
                for inclusive in inclusives:
                    inclusive_payload = {
                        "adventure": record,
                        "name": inclusive
                    }
                    adv_models.Inclusives.objects.create(**inclusive_payload)
        except Exception as e:
            log.error(e)
            pass

        return Response({"details": "Successfully updated"})

    @action(
        methods=['POST'],
        detail=False,
        url_path='close',
        url_name='close')
    def closeclose_adventure_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.GenericRequestSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        try:
            record = adv_models.Adventure.objects.get(id=payload['request'])
        except Exception as e:
            log.error(e)
            return Response({"details": "Adventure does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if record.adventure_status in ['COMPLETE', 'CANCELLED']:
            return Response({"details": "Adventure already closed or cancelled"},
                            status=status.HTTP_400_BAD_REQUEST)

        record.adventure_status = 'COMPLETE'
        record.save()

        return Response({"details": "Adventure Closed successfully"})

    @action(
        methods=['POST'],
        detail=False,
        url_path='cancel',
        url_name='cancel')
    def cancel_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.GenericRequestSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        try:
            record = adv_models.Adventure.objects.get(id=payload['request'])
        except Exception as e:
            log.error(e)
            return Response({"details": "Adventure does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if record.adventure_status in ['COMPLETE', 'CANCELLED']:
            return Response({"details": "Adventure already closed or cancelled"},
                            status=status.HTTP_400_BAD_REQUEST)

        record.adventure_status = 'CANCELLED'
        record.save()

        return Response({"details": "Adventure Cancelled successfully"})