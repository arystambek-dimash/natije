from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        role = Role.objects.get(name='teacher')
        return self.create_user(email, password, role=role, **extra_fields)


class Role(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=100,
                              unique=True,
                              verbose_name='email address',
                              null=False,
                              error_messages={
                                  "unique": "A user with that email already exists.",
                              },
                              )
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, default=2)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Profile(models.Model):
    profile_picture = models.ImageField(upload_to='medias/profile_pictures', null=True)
    test_limit = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
