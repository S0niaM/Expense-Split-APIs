from rest_framework import serializers
from .models import User, Expense, ExpenseSplit
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Use the custom user model if specified in the Django settings
User = get_user_model()

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone']

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    # Validate the email format
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value

    # Validate the phone number length
    def validate_phone(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits")
        return value

    # Validate the password strength
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")
        return value

    # Create a new user with the provided validated data
    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            name=validated_data.get('name'),
            phone=validated_data.get('phone')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Serializer for user login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    # Validate the login credentials
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        else:
            raise serializers.ValidationError("Invalid credentials")


# Import serializers module
from rest_framework import serializers
from .models import Expense, ExpenseSplit

# Serializer for the User model (duplicated, make sure to use only one)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Serializer for the ExpenseSplit model
class ExpenseSplitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Read-only nested user serializer
    user_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source='user')

    class Meta:
        model = ExpenseSplit
        fields = ['id', 'user', 'user_id', 'amount', 'person', 'percentage']

# Serializer for the Expense model
class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True, read_only=True)  # Nested ExpenseSplit serializer
    created_by = UserSerializer(read_only=True)  # Read-only nested user serializer

    class Meta:
        model = Expense
        fields = ['id', 'description', 'amount', 'split_method', 'split_between', 'created_by', 'splits']

# Serializer for creating ExpenseSplit instances
class ExpenseSplitCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    person = serializers.CharField(max_length=255, required=False)

# Serializer for creating Expense instances
class ExpenseCreateSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'split_method', 'split_between', 'splits']

    # Validate the splits data based on the split method
    def validate(self, data):
        splits_data = data.get('splits', [])
        split_method = data['split_method']
        split_between = data['split_between']
        amount = data['amount']

        if len(splits_data) != split_between:
            raise serializers.ValidationError(f"Number of splits ({len(splits_data)}) must match split_between ({split_between}).")

        if split_method == 'PERCENTAGE':
            total_percentage = sum([split.get('percentage', 0) for split in splits_data])
            if total_percentage != 100:
                raise serializers.ValidationError("Total percentage must add up to 100%.")
            for split in splits_data:
                if 'percentage' not in split:
                    raise serializers.ValidationError("Percentage is required for each split in PERCENTAGE method.")
        elif split_method == 'EXACT':
            total_amount = sum([split.get('amount', 0) for split in splits_data])
            if total_amount != amount:
                raise serializers.ValidationError(f"Total split amount ({total_amount}) must equal expense amount ({amount}).")
            for split in splits_data:
                if 'amount' not in split:
                    raise serializers.ValidationError("Amount is required for each split in EXACT method.")
        elif split_method == 'EQUAL':
            for split in splits_data:
                if 'amount' in split or 'percentage' in split:
                    raise serializers.ValidationError("Amount and percentage should not be provided for EQUAL split method.")

        return data

    # Create the expense and related splits based on the split method
    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        expense = Expense.objects.create(**validated_data)

        if expense.split_method == 'EQUAL':
            split_amount = expense.amount / expense.split_between
            for split_data in splits_data:
                ExpenseSplit.objects.create(expense=expense, amount=split_amount, **split_data)
        elif expense.split_method == 'EXACT':
            for split_data in splits_data:
                ExpenseSplit.objects.create(expense=expense, **split_data)
        elif expense.split_method == 'PERCENTAGE':
            for split_data in splits_data:
                percentage = split_data['percentage']
                amount = (expense.amount * percentage) / 100
                ExpenseSplit.objects.create(expense=expense, amount=amount, **split_data)

        return expense
