from django.db import models


DEPARTMENT_CHOICES = [
    ('dispatch', 'Dispatch'),
    ('update', 'Update'),
    ('safety', 'Safety'),
    ('fleet', 'Fleet'),
    ('accounting', 'Accounting'),
    ('recruiting', 'Recruiting'),
    ('career', 'Career Center'),
]


class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('open', 'Open / Written'),
    ]

    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    title = models.CharField(max_length=200, help_text="Question label shown to student")
    text = models.TextField(help_text="The full question text")
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.get_department_display()}] {self.text[:60]}"


class ExamSession(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    exam_date = models.DateField()
    group = models.CharField(max_length=100)
    teacher = models.CharField(max_length=200)
    departments = models.CharField(max_length=300, default='')

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)

    def get_departments_list(self):
        return [d.strip() for d in self.departments.split(',') if d.strip()]

    def get_departments_display(self):
        from exam.models import DEPARTMENT_CHOICES
        dept_map = dict(DEPARTMENT_CHOICES)
        return ', '.join([dept_map.get(d, d) for d in self.get_departments_list()])

    def __str__(self):
        return f"{self.full_name} — {self.exam_date} ({self.group})"

    class Meta:
        ordering = ['-started_at']


class Answer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    selected_option = models.CharField(max_length=1, blank=True)

    def __str__(self):
        return f"{self.session.full_name} → Q{self.question.id}"