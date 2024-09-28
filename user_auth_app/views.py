from django.contrib.auth import logout
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsNotAuthenticated

from user_auth_app.models import User


# Create your views here.


class UserRegisterView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        data = request.POST
        username = data.get("username")
        email = data.get("email")
        pass1 = data.get("pass1")
        pass2 = data.get("pass2")

        errors = {}
        if not username and not email and not pass1 and not pass2:
            errors['credentials'] = "Pls enter all the credentials!"

        if pass1 != pass2:
            errors['password'] = "Passwords aren`t matched!"

        if User.objects.filter(username=username).exists():
            errors['username'] = "This username exists!"

        if User.objects.filter(email=email).exists():
            errors['email'] = "This email exists!"

        if errors:
            return JsonResponse({"data": errors}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, email=email, password=pass1)
        return JsonResponse({"data": "User created successfully!"}, status=status.HTTP_201_CREATED)

    def handle_exception(self, exc):
        # Handle permission denied exceptions.
        if isinstance(exc, PermissionDenied):
            return JsonResponse(
                {"data": {"permission": "You must be unauthenticated to access this resource."},
                 "status": status.HTTP_403_FORBIDDEN},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Call the base class method for any other exceptions.
        return super().handle_exception(exc)


class UserLoginView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse(status=status.HTTP_200_OK)
        except:
            return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
