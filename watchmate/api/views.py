from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status, generics, viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
# from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.throttling import (UserRateThrottle, 
                                       AnonRateThrottle, ScopedRateThrottle)

from django.shortcuts import get_object_or_404

from watchlist import models
from api import serializers, permissions, throttling, pagination

# Create your views here.

class UserReview(generics.ListAPIView):
    # queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [throttling.ReviewListThrottle, 
    #                     AnonRateThrottle]
    
    # Filtering against the URL
    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return models.Review.objects.filter(review_user__username=username)
    
    # Filtering against query parameters
    def get_queryset(self):
        username = self.request.query_params.get('username')
        return models.Review.objects.filter(review_user__username=username)

class StreamPlatformVS(viewsets.ModelViewSet):
    queryset = models.StreamPlatform.objects.all()
    serializer_class = serializers.StreamPlatformSerializer
    permission_classes = [permissions.IsAdminOrReadOnly]

# class StreamPlatformVS(viewsets.ViewSet):
    
#     def list(self, request):
#         queryset = models.StreamPlatform.objects.all()
        # serializer = serializers.StreamPlatformSerializer(queryset, 
        #                                                  many=True, context={'request': request})
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = models.StreamPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = serializers.StreamPlatformSerializer(watchlist, context={'request': request})
#         return Response(serializer.data)
    
#     def create(self, request):
#         serializer = serializers.StreamPlatformSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)



class ReviewCreate(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.ReviewCreateThrottle]
    
    
    def get_queryset(self):
        return models.Review.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = models.WatchList.objects.get(pk=pk)
        
        current_user = self.request.user
        review_queryset = models.Review.objects.filter(watchlist=watchlist, review_user=current_user)
        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie!")
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating']) / 2
            
        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()
        
        serializer.save(watchlist=watchlist, review_user=current_user)
    
    
class ReviewList(generics.ListAPIView):
    # queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    # permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']
    
    # get queryset for (watchlist field only)
    def get_queryset(self):
        pk = self.kwargs['pk']
        return models.Review.objects.filter(watchlist=pk)
    
    
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'
    


# class ReviewDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
#                    mixins.DestroyModelMixin, generics.GenericAPIView):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
    
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
    
    
# class ReviewList(mixins.ListModelMixin, mixins.CreateModelMixin,
#                  generics.GenericAPIView):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
    

class StreamPlatformAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    
    def get(self, request):
        platform = models.StreamPlatform.objects.all()
        serializer = serializers.StreamPlatformSerializer(platform, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.StreamPlatformSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    

class StreamPlatformDetailAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    
    def get(self,request, pk):
        try:
            platform = models.StreamPlatform.objects.get(pk=pk)
        except models.StreamPlatform.DoesNotExist:
            return Response({'msg': "Stream details are not available"}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.StreamPlatformSerializer(platform, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        platform = models.StreamPlatform.objects.get(pk=pk)
        serializer = serializers.StreamPlatformSerializer(platform, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        platform = models.StreamPlatform.objects.get(pk=pk)
        platform.delete()
        return Response({"msg": "Stream platform deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
           
           
class WatchListGV(generics.ListAPIView):
    queryset = models.WatchList.objects.all()
    serializer_class = serializers.WatchListSerializer
    # pagination_class = pagination.WatchListPagination
    # pagination_class = pagination.WatchListLOPagination
    pagination_class = pagination.WatchListCPagination
    
    # for Filter
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['title', 'platform__name']
    
    # For Search
    # filter_backends = [filters.SearchFilter]
    # # search_fields = ['title', 'platform__name']
    # search_fields = ['^title', '=platform__name']
    
    # For Ordering
    # filter_backends = [filters.OrderingFilter]
    # ordering_fields  = ['avg_rating']
    
    # get queryset for (watchlist field only)
    # def get_queryset(self):
    #     pk = self.kwargs['pk']
    #     return models.Review.objects.filter(watchlist=pk)
    
    
class WatchListAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    
    def get(self, request):
        movies = models.WatchList.objects.all()
        serializer = serializers.WatchListSerializer(movies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class WatchDetailAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    
    def get(self, request, pk):
        try:
            movie = models.WatchList.objects.get(pk=pk)
        except models.WatchList.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.WatchListSerializer(movie)
        return Response(serializer.data)
    
    def put(self, request, pk):
        movie = models.WatchList.objects.get(pk=pk)
        serializer = serializers.WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        movie = models.WatchList.objects.get(pk=pk)
        movie.delete()
        return Response({"msg": "Movie deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        


#################     Function Based Views     ########################

# @api_view(['GET', 'POST'])
# def movie_list(request):
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)
#     if request.method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors)

# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_details(request, pk):
#     try:
#         movie = Movie.objects.get(pk=pk)
#     except Movie.DoesNotExist:
#         return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
#     if request.method == 'GET':
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)
#     if request.method == 'PUT':
#         serializer = MovieSerializer(movie, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     if request.method == 'DELETE':
#         movie.delete()
#         return Response({"msg": "Movie deleted successfully"}, status=status.HTTP_204_NO_CONTENT)