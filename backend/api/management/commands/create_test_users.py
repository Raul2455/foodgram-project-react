from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone


class Command(BaseCommand):
    help = 'Создает тестовых пользователей'

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {'username': 'testuser1', 'email': 'test1@example.com',
                'password': 'testpassword1', 'first_name': 'Test',
                'last_name': 'User1'},
            {'username': 'testuser2', 'email': 'test2@example.com',
                'password': 'testpassword2', 'first_name': 'Test',
                'last_name': 'User2'},
            {'username': 'testuser3', 'email': 'test3@example.com',
                'password': 'testpassword3', 'first_name': 'Test',
                'last_name': 'User3'},
            # Добавляйте больше пользователей по мере необходимости
        ]

        for user_data in users:
            if not User.objects.filter(
                username=user_data['username']
            ).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    last_login=timezone.now(),
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Создан пользователь: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Пользователь {user_data["username"]} уже существует.'))
