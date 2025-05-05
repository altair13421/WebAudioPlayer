from django.shortcuts import render

from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import action  # type: ignore

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

    @action(detail=False, methods=["get"])
    def get_artist(self, request):
        """
        Get the artist from the request.
        """
        artist = request.query_params.get("artist")
        if not artist:
            return Response({"error": "Artist not found"}, status=404)
        try:
            artist_obj = LastFMArtist.objects.get(name=artist)
            serializer = self.get_serializer(artist_obj)
            return Response(serializer.data)
        except LastFMArtist.DoesNotExist:
            return Response({"error": "Artist not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)