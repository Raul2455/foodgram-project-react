from rest_framework import mixins, viewsets
from rest_framework.response import Response


class ReadOnlyViewSet(
    mixins.ListModelMixin,        # Миксин для получения списка объектов
    mixins.RetrieveModelMixin,    # Миксин для получения одного объекта
    viewsets.GenericViewSet       # Базовый класс для ViewSet
):
    """
    Кастомный ViewSet, предоставляющий только операции чтения:
    - `list` (получение списка объектов)
    - `retrieve` (получение одного объекта по ID)
    """

    def get_queryset(self):
        """
        Возвращает queryset, который будет использоваться
        для получения объектов.
        Этот метод можно переопределить в дочерних классах для фильтрации или
        изменения queryset.
        """
        return super().get_queryset()

    def get_serializer_context(self):
        """
        Возвращает контекст, который будет передан в сериализатор.
        Этот метод можно переопределить для добавления
        дополнительных данных в контекст.
        """
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'view': self,
        })
        return context

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения списка объектов.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения одного объекта по его ID.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
