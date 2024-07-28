from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ExpenseSerializer, ExpenseCreateSerializer
from .models import User, Expense, ExpenseSplit
from django.db.models import Sum

# View for user registration
class SignUpView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')

        # Validate email format
        if email:
            try:
                validate_email(email)
            except ValidationError:
                return Response({'error': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email__iexact=email).exists():
                return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number length
        if phone:
            if len(phone) != 10:
                return Response({'error': 'Phone number must be 10 digits.'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(phone__iexact=phone).exists():
                return Response({'error': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = User.objects.create_user(name=name, email=email, phone=phone, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

# View for user login
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

# View to list and create expenses
class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]

    # Determine serializer class based on request method
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCreateSerializer
        return ExpenseSerializer

    # Save the created expense with the current user as creator
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# View to get details of a specific user's expense
class UserExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, created_by=user)
        except Expense.DoesNotExist:
            return Response({"detail": "Expense not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

# View to get the total expenses of a user
class UserOverallExpensesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        total_expenses = ExpenseSplit.objects.filter(user_id=user_id).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return Response({"user_id": user_id, "total_expenses": total_expenses}, status=status.HTTP_200_OK)
