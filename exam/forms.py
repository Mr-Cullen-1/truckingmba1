from django import forms
from .models import ExamSession, DEPARTMENT_CHOICES

STUDENT_DEPT_CHOICES = [c for c in DEPARTMENT_CHOICES if c[0] != 'career']

class FinalRegistrationForm(forms.ModelForm):
    """Final imtihon uchun barcha maydonlar majburiy"""
    exam_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    departments = forms.MultipleChoiceField(
        choices=STUDENT_DEPT_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ExamSession
        fields = ['exam_date', 'full_name', 'phone', 'group', 'teacher', 'departments']
        labels = {
            'full_name': 'Full Name',
            'phone': 'Phone Number',
            'group': 'Group',
            'teacher': 'Logistics Teacher',
        }

    def clean_departments(self):
        return ','.join(self.cleaned_data.get('departments', []))

class MockRegistrationForm(forms.ModelForm):
    """Mock uchun faqat ism, guruh va yo'nalishlar kifoya"""
    departments = forms.MultipleChoiceField(
        choices=STUDENT_DEPT_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ExamSession
        fields = ['full_name', 'group', 'departments']
        labels = {
            'full_name': 'Student Name',
            'group': 'Your Group',
        }

    def clean_departments(self):
        return ','.join(self.cleaned_data.get('departments', []))