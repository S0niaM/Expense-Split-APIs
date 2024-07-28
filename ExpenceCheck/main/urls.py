from django.urls import path
from .views import SignUpView, LoginView, ExpenseListCreateView, UserExpenseDetailView,  UserOverallExpensesView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:expense_id>/', UserExpenseDetailView.as_view(), name='user-expense-detail'),
    path('user-overall-expenses/<int:user_id>/', UserOverallExpensesView.as_view(), name='user-overall-expenses'),
]
