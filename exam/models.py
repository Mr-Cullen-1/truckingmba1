from django.db import models

# Department tanlovlari: ham logistika, ham yangi ingliz tili modullari kiritilgan
DEPARTMENT_CHOICES = [
    ('dispatch', 'Dispatch'),
    ('update', 'Update'),
    ('safety', 'Safety'),
    ('fleet', 'Fleet'),
    ('accounting', 'Accounting'),
    ('recruiting', 'Recruiting'),
    ('career', 'Career Center'),
    # Yangi Ingliz tili modullari
    ('eng_mod1', 'Module 1: English Foundations'),
    ('eng_mod2', 'Module 2: Tenses & Timeline'),
    ('eng_mod3', 'Module 3: Advanced Communication'),
]

class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('open', 'Open / Written'),
        ('scramble', 'Sentence Building'), # Yangi scramble turi qo'shildi
    ]
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    title = models.CharField(max_length=200, help_text="Question label shown to student")
    text = models.TextField(help_text="The full question text or scrambled words (separated by /)")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    @property
    def options_list(self):
        """Template (HTML) ichida variantlarni loop qilish uchun qulay property"""
        options = []
        if self.option_a: options.append(('a', self.option_a))
        if self.option_b: options.append(('b', self.option_b))
        if self.option_c: options.append(('c', self.option_c))
        if self.option_d: options.append(('d', self.option_d))
        return options

    def __str__(self):
        return f"[{self.get_department_display()}] {self.text[:60]}"

class ExamSession(models.Model):
    EXAM_TYPES = [
        ('mock', 'Mock Exam'),
        ('final', 'Final Exam'),
    ]
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES, default='mock')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True, null=True)
    exam_date = models.DateField()
    group = models.CharField(max_length=100)
    teacher = models.CharField(max_length=200, blank=True, null=True)
    departments = models.CharField(max_length=300, default='') # Tanlangan modullar vergul bilan saqlanadi
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    
    # --- CHEATING GA QARSHI YANGI USTUNLAR ---
    is_blocked = models.BooleanField(default=False, help_text="Talaba qoidani buzsa True bo'ladi")
    block_reason = models.CharField(max_length=100, blank=True, null=True, help_text="Refresh yoki Tab o'zgarishi")

    def get_departments_list(self):
        """Vergul bilan ajratilgan departamentlarni list ko'rinishida qaytaradi"""
        return [d.strip() for d in self.departments.split(',') if d.strip()]

    def __str__(self):
        return f"{self.full_name} — {self.get_exam_type_display()} ({self.group})"

class Answer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    selected_option = models.CharField(max_length=1, blank=True) # Faqat MCQ uchun ishlatiladi