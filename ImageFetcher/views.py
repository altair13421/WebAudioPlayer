from django.shortcuts import render

# Create your views here.
# Now For the views.py file, we will create a view to handle the API requests.
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from .models import LastFMArtist
from .serializers import LastFMArtistSerializer


class LastFMArtistModelViewSet(ReadOnlyModelViewSet):
    """
    A viewset that provides default `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """
    queryset = LastFMArtist.objects.all()
    serializer_class = LastFMArtistSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['name', 'artist']