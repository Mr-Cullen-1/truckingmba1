from django import forms
from .models import ExamSession, DEPARTMENT_CHOICES

# Logistika uchun career bo'lmagan tanlovlar
STUDENT_DEPT_CHOICES = [c for c in DEPARTMENT_CHOICES if c[0] != 'career' and not c[0].startswith('eng_')]

# Faqat ingliz tili modullarini ajratib olish
ENGLISH_MODULES = [c for c in DEPARTMENT_CHOICES if c[0].startswith('eng_')]

class FinalRegistrationForm(forms.ModelForm):
    """Final imtihon uchun barcha maydonlar majburiy[cite: 5]"""
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
    """Mock uchun faqat ism, guruh va yo'nalishlar kifoya[cite: 5]"""
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

class EnglishRegistrationForm(forms.ModelForm):
    """Ingliz tili sessiyasi uchun maxsus forma"""
    teacher = forms.CharField(
        max_length=200, 
        label="Teacher's name (English)",
        widget=forms.TextInput(attrs={'placeholder': 'Enter teacher name'})
    )
    
    # Faqat bitta modul tanlash uchun ChoiceField (RadioSelect bilan)[cite: 1]
    departments = forms.ChoiceField(
        choices=ENGLISH_MODULES,
        widget=forms.RadioSelect,
        label="Choose Module"
    )

    class Meta:
        model = ExamSession
        fields = ['full_name', 'group', 'teacher', 'departments']
        labels = {
            'full_name': "Student's Full Name",
            'group': 'Group',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Student\'s full name'}),
            'group': forms.TextInput(attrs={'placeholder': 'Your group'}),
        }

    def clean_departments(self):
        # ChoiceField bitta string qaytaradi, uni bazaga moslash uchun qaytaramiz[cite: 1]
        return self.cleaned_data.get('departments', '')