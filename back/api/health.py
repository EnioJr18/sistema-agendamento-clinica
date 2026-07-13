from django.db import connection
from django.db.utils import OperationalError
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

HealthResponseSerializer = inline_serializer(
    name='HealthResponse',
    fields={
        'status': serializers.CharField(),
        'database': serializers.CharField(),
    },
)


@extend_schema(
    responses={
        200: OpenApiResponse(response=HealthResponseSerializer, description='Aplicacao saudavel.'),
        503: OpenApiResponse(response=HealthResponseSerializer, description='Aplicacao degradada.'),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    database_ok = True
    http_status = status.HTTP_200_OK

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except OperationalError:
        database_ok = False
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        {
            'status': 'ok' if database_ok else 'degraded',
            'database': 'ok' if database_ok else 'unavailable',
        },
        status=http_status,
    )
