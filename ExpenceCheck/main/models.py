from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom manager for the User model
class UserManager(BaseUserManager):
    # Method to create a regular user
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        # Ensure that at least an email or phone number is provided
        if not email and not phone:
            raise ValueError('Either Email or Phone number is required')
        
        if email:
            email = self.normalize_email(email)
        
        # Create and save the user
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Method to create a superuser
    def create_superuser(self, email=None, phone=None, password=None, **extra_fields):
        # Set superuser-specific fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email=email, phone=phone, password=password, **extra_fields)

# Custom User model
class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    
    # Use the custom user manager
    objects = UserManager()

    # Specify the username field and required fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email if self.email else self.phone

    @property
    def username(self):
        return self.email if self.email else self.phone

# Model to represent an expense
class Expense(models.Model):
    SPLIT_CHOICES = [
        ('EQUAL', 'Equal'),
        ('EXACT', 'Exact'),
        ('PERCENTAGE', 'Percentage'),
    ]

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_method = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    split_between = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_created')

    def __str__(self):
        return self.description

# Model to represent an expense split among users
class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    person = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.person}"
