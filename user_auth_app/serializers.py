from rest_framework import serializers

from user_auth_app.models import User


class UserModelSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"

    def get_is_admin(self, obj):
        return obj.is_staff()
