from rest_framework import serializers
from watchlist.models import Movie



class MovieSerializer(serializers.ModelSerializer):
    # step -1 to adding custom serializer field
    len_name = serializers.SerializerMethodField()
    class Meta:
        model = Movie
        fields = '__all__'
        # fields = ['id', 'name', 'description', 'active']
        # exclude = ['description']
    
    # step - 2 to adding custom serializer field ('get_'<field name>)
    def get_len_name(self, obj):
        return len(obj.name)
    
     ### Object level validation ###
    def validate(self, data):
        if data['name'] == data['description']:
            raise serializers.ValidationError("Name and Description must be different")
        return data
        
        
     ### Field level validation ###
    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Name is too short")
        return value
    








### Validators level validation ###
# def name_length(value):
#     if len(value) < 2:
#         raise serializers.ValidationError("Name length should be more than 2 characters")
    
# class MovieSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(validators=[name_length])
#     description = serializers.CharField()
#     active = serializers.BooleanField()
    
#     def create(self, validated_data):
#         return Movie.objects.create(**validated_data)
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.description = validated_data.get('description', instance.description)
#         instance.active = validated_data.get('active', instance.active)
        
#         instance.save()
#         return instance
    
#     ### Object level Validation ###
#     def validate(self, data):
#         if data['name'] == data['description']:
#             raise serializers.ValidationError("Name and Description must be different")
#         return data
    
#     ### Field level validation ###
#     # def validate_name(self, value):
#     #     if len(value) < 2:
#     #         raise serializers.ValidationError("Name is too short")
#     #     return value