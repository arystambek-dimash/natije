import asyncio
from asgiref.sync import sync_to_async

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, ProfileUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        data = {
            'refresh': str(refresh),
            'access': str(access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        refresh_token = self.request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "Сау болыңыз!!"}, status=status.HTTP_200_OK)


class GetUpdateDeleteProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class_map = {"GET": ProfileSerializer, "PATCH": ProfileUpdateSerializer, "DELETE": UserSerializer}
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        return self.serializer_class_map.get(self.request.method.upper())

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        profile.delete()
        user.delete()

        return self.destroy(request, *args, **kwargs)
