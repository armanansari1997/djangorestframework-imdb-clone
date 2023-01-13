from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from user_app.api.serializers import RegistrationSerializer
from user_app import models


@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        curent_user_token = request.user.auth_token
        curent_user_token.delete()
        return Response(status=status.HTTP_200_OK)



@api_view(['POST',])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        
        data = {}
        
        if serializer.is_valid():
            account = serializer.save()
            
            data['response'] = "Registration Successfull"
            data['username'] = account.username
            data['email'] = account.email
            token = Token.objects.get(user=account).key
            data['token'] = token
            
            '''
                For JWT Authentication(Creating Tokens Manually)
            '''
            # refresh = RefreshToken.for_user(account)
            # data['token'] = {
            #                 'refresh': str(refresh),
            #                 'access': str(refresh.access_token),
            # }
            
            # Till upper part
            
        else:
            data = serializer.errors
            
        return Response(data, status=status.HTTP_201_CREATED)
        