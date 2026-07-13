from rest_framework_simplejwt.tokens import RefreshToken


def generate_jwt_response(user, serializer_class):
    refresh = RefreshToken.for_user(user)
    return {
        "has_password": user.has_usable_password(),
        'access': str(refresh.access_token),
        'refresh': str(refresh)  # manage in cookie
    }
