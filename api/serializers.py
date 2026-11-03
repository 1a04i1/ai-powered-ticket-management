from rest_framework import serializers


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        required=True,
        trim_whitespace=True
    )