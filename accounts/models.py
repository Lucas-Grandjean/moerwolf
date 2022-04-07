from django.db import models
from django.contrib.auth.models import (
    UserManager, AbstractUser
)
from login.models import Card

class UserManager(UserManager):
    def create_user(self, username, password=None, email=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError('Users must have an username address')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, username, password):
        """
        Creates and saves a staff user with the given username and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password,  email=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser

    player_card = models.ForeignKey(
        Card,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    ongoing_game = models.ForeignKey(
        "moerwolfgame.Game",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    # GAME : Check s'il a déjà voté ou pas et son nombre de votes sur lui
    votes = models.IntegerField(default=0)
    wolf_votes = models.IntegerField(default=0)
    power_usage = models.IntegerField(default=0) # 0 : Pas de pouvoirs // 1 : Utilisable // 2 : Non utilisable // 3 (WITCH) : Heal // 4 (WITCH) : Death
    has_voted = models.BooleanField(default=False)
    alive = models.BooleanField(default=False)
    guarded = models.BooleanField(default=False) #Gardé pendant la nuit
    healed = models.BooleanField(default=False) #Soigné pendant la nuit
    death_potion = models.BooleanField(default=False) #Potion de mort pendant la nuit


    def get_full_name(self):
        # The user is identified by their username address
        return self.username

    def get_short_name(self):
        # The user is identified by their username address
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    objects = UserManager()