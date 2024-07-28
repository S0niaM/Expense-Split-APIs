
from django import forms
from .models import Expense, ExpenseSplit

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'split_method', 'split_between']

class ExpenseSplitForm(forms.ModelForm):
    class Meta:
        model = ExpenseSplit
        fields = ['person', 'amount', 'percentage']
