from rest_framework import mixins, viewsets


# Почему ViewSet в файле для mixin?
class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass
