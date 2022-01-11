from django.core.validators import RegexValidator
from rest_framework import serializers

from adventure import models as adv_models
from booking import models as book_models


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)


class CreateBookingSerializer(serializers.Serializer):
    adventure = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(
        required=True, max_length=10, min_length=10,
        validators=[RegexValidator(r'^\d{0,10}$', 'Kindly add valid phone number')],
        error_messages={
            "invalid": "Kindly add valid number",
            "min_length": "Should be at least 10 numbers",
            "max_length": "Should be at most 10 numbers",
        })
    idnum = serializers.CharField(allow_null=True)
    adult_participants = serializers.IntegerField(required=True, min_value=1)
    child_participants = serializers.IntegerField(required=True, allow_null=True, min_value=1)

    def validate(self, attrs):
        adventure_id = attrs.get('adventure')
        adventure = adv_models.Adventure.objects.filter(id=adventure_id)
        if not adventure.exists():
            raise serializers.ValidationError('Adventure does not exist')
        attrs['adventure_instance'] = adventure.first()
        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = book_models.Invoice
        fields = [
            'id', 'reference_number',
            'invoice_status',
            'amount', 'expiry_date',
            'date_due', 'allow_partial_payment',
            'date_created'
        ]


class ListBookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = book_models.Booking
        fields = [
            'id',
            'reference_number',
            'book_status',
            'is_cleared',
            'date_created'
        ]


class BookingDetailSerializer(ListBookingsSerializer):
    invoices = serializers.SerializerMethodField('get_invoices')

    class Meta:
        model = book_models.Booking
        fields = ListBookingsSerializer.Meta.fields + [
            'adventure',
            'name',
            'phone_number',
            'idnum',
            'adult_participants',
            'child_participants',
            'invoices',
        ]

    def get_invoices(self, obj):
        try:
            invoices = obj.invoice.all()
            invoice_details = InvoiceSerializer(invoices, many=True).data
            return invoice_details
        except Exception as e:
            print(e)
            return []
