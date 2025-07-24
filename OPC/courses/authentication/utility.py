from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def get_jwt_tokens(username, password):
    """
    Authenticate user locally instead of making external API call
    """
    try:
        # Use Django's built-in authentication
        user = authenticate(username=username, password=password)
        if user is not None:
            # Return a simple token structure for compatibility
            return {
                'access': 'django_auth_success',
                'refresh': 'django_auth_success',
                'user_id': user.id,
                'username': user.username
            }
    except Exception as e:
        print(f"Authentication error: {e}")
    return None



