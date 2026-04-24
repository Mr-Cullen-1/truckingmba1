from django import forms
from .models import ExamSession, DEPARTMENT_CHOICES

STUDENT_DEPT_CHOICES = [c for c in DEPARTMENT_CHOICES if c[0] != 'career']


class RegistrationForm(forms.ModelForm):
    exam_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Exam Date"
    )

    departments = forms.MultipleChoiceField(
        choices=STUDENT_DEPT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Choose your departments",
        help_text="Select all departments you studied."
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
        return ','.join(self.cleaned_data['departments'])