import logging

from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from booking import models as book_models, serializers as book_serializer
from sharedservice import service_responses, utility_functions, time_functions

utility_function = utility_functions
time_function = time_functions

log = logging.getLogger(__name__)


class BoookingViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['reference_number', ]

    def get_serializer_class(self):
        mapper = {
            'book_adventure': book_serializer.CreateBookingSerializer,
            'list': book_serializer.ListBookingsSerializer,
            'retrieve': book_serializer.BookingDetailSerializer,
        }
        return mapper.get(self.action, book_serializer.ListBookingsSerializer)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    def get_authenticated_user(self):
        return self.request.user

    def get_queryset(self):
        user = self.get_authenticated_user()
        try:
            user_group = user.groups.first()
            group = user_group.name
        except Exception as e:
            log.error(e)
            group = ''

        if group == 'STAFF':
            return book_models.Booking.objects.all().order_by('-date_created')
        else:
            return book_models.Booking.objects.filter(user=user).order_by('-date_created')

    @action(methods=['POST'],
            detail=False,
            url_path='book-adventure',
            url_name='book-adventure')
    def book_adventure(self, request, *args, **kwargs):
        payload = request.data
        serializer = self.get_serializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data

        # create user
        user_payload = {
            "email": payload['email'],
            "user_type": 'PUBLIC',
            "full_name": payload['name'],
            "phone_number": payload['phone_number']
        }
        registered_user, resp = service_responses.register_user(user_payload)
        if not registered_user:
            log.error(resp)
            return Response({"details": "Failed to process request. Try again later",
                             "errors": resp},
                            status=status.HTTP_400_BAD_REQUEST)

        current_time = time_function.get_current_datetime()
        book_instance = book_models.Booking.objects.filter(
            user=resp, book_status__in=['UNPAID', 'COMPLETE'], adventure__start_date__gte=current_time)
        if book_instance.exists():
            return Response({"details": "You have already booked", 'redirect': "DETAIL_PAGE"},
                            status=status.HTTP_400_BAD_REQUEST)

        # generated reference
        reference_number = utility_function.generate_unique_reference_per_model(
            book_models.Booking, size=10)
        validated_data = serializer.validated_data
        adventure = validated_data['adventure_instance']
        no_adults = payload['adult_participants']
        no_childs = payload['child_participants']
        # create booking
        booking_payload = {
            "user": resp,
            "adventure": adventure,
            "reference_number": reference_number,
            "book_status": 'UNPAID',
            "name": payload['name'],
            "phone_number": payload['phone_number'],
            "idnum": payload['idnum'],
            "adult_participants": no_adults,
            "child_participants": no_childs,
            "is_cleared": False,
        }

        booking_instance = book_models.Booking.objects.create(**booking_payload)

        # invoice payload
        try:
            invoice_reference_number = utility_function.generate_unique_reference_per_model(
                book_models.Invoice, size=10)
            prices = adventure.prices
            expiry_date = adventure.end_date
            date_due = adventure.start_date
            total = prices.adult * no_adults
            child = prices.child
            if child:
                total_child = child * no_childs
                total = total + total_child

            invoice_payload = {
                "booking": booking_instance,
                "reference_number": invoice_reference_number,
                "invoice_status": 'PENDING',
                "amount": total,
                "expiry_date": expiry_date,
                "date_due": date_due,
                "allow_partial_payment": False,
            }
            book_models.Invoice.objects.create(**invoice_payload)
        except Exception as e:
            log.error(e)
            pass

        return Response({"details": "Successfully booked"}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
