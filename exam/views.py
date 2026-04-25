from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
import random
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from .models import Question, ExamSession, Answer, DEPARTMENT_CHOICES
from .forms import RegistrationForm

@ensure_csrf_cookie
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            session = form.save()
            return redirect('exam_start', session_id=session.id)
    else:
        form = RegistrationForm()
    return render(request, 'exam/register.html', {'form': form})

def exam_view(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, is_complete=False)

    if request.method == 'POST':
        question_ids = request.POST.getlist('question_ids')
        questions = Question.objects.filter(id__in=question_ids)

        for question in questions:
            field_key = f"q_{question.id}"
            value = request.POST.get(field_key, "").strip()
            if not value:
                continue

            answer, _ = Answer.objects.get_or_create(session=session, question=question)
            if question.question_type == 'mcq':
                answer.selected_option = value
                answer.answer_text = ""
            else:
                answer.answer_text = value
                answer.selected_option = ""
            answer.save()

        session.submitted_at = timezone.now()
        session.is_complete = True
        session.save()
        return redirect('exam_done')

    # --- SAVOLLARNI TAQSIMLASH LOGIKASI (6 MCQ + 4 OPEN + 2 CAREER = 12) ---
    selected_depts = session.get_departments_list()
    num_depts = len(selected_depts)
    
    # 1. MCQ Savollar (Jami 6 ta)
    mcq_questions = []
    if num_depts > 0:
        per_dept_limit = 6 // num_depts
        for dept in selected_depts:
            qs = list(Question.objects.filter(department=dept, question_type='mcq', is_active=True))
            if qs:
                mcq_questions.extend(random.sample(qs, min(per_dept_limit, len(qs))))
        
        if len(mcq_questions) < 6:
            remaining = 6 - len(mcq_questions)
            exclude_ids = [q.id for q in mcq_questions]
            extra_mcq = list(Question.objects.filter(
                department__in=selected_depts, question_type='mcq', is_active=True
            ).exclude(id__in=exclude_ids))
            if extra_mcq:
                mcq_questions.extend(random.sample(extra_mcq, min(remaining, len(extra_mcq))))

    # 2. Open Questions (Jami 4 ta)
    open_qs_pool = list(Question.objects.filter(
        department__in=selected_depts, question_type='open', is_active=True
    ))
    open_questions = random.sample(open_qs_pool, min(4, len(open_qs_pool)))

    # 3. Career Center (Jami 2 ta)
    career_qs = list(Question.objects.filter(department='career', is_active=True))
    career_questions = random.sample(career_qs, min(2, len(career_qs)))

    all_questions = mcq_questions + open_questions + career_questions
    all_questions.sort(key=lambda q: q.order)

    return render(request, 'exam/exam.html', {
        'session': session,
        'questions': all_questions,
        'exam_duration': 20 * 60,
        'warning_time': 5 * 60,
    })

def done_view(request):
    return render(request, 'exam/done.html')

@staff_member_required
def admin_results_view(request):
    # Natijalarni savollari bilan birga bazadan tortish
    sessions = ExamSession.objects.prefetch_related('answers__question').all().order_by('-submitted_at')
    dept_map = dict(DEPARTMENT_CHOICES)
    
    rows = []
    for session in sessions:
        dept_display = ', '.join([dept_map.get(d, d) for d in session.get_departments_list()])
        
        answered_data = []
        # Har bir talabaning individual javoblarini savol matni bilan birga yig'amiz
        for ans in session.answers.select_related('question').all().order_by('question__order'):
            val = ans.selected_option.upper() if ans.selected_option else ans.answer_text
            answered_data.append({
                'dept': ans.question.get_department_display(),
                'question_text': ans.question.text, # Savolning to'liq matni
                'title': ans.question.title,
                'value': val,
            })
            
        rows.append({
            'session': session,
            'dept_display': dept_display,
            'answered': answered_data,
        })
        
    return render(request, 'exam/admin_results.html', {'rows': rows})

@staff_member_required
def export_excel_view(request):
    # Bazadan barcha sessiyalarni javoblari bilan tortib olish
    sessions = ExamSession.objects.prefetch_related('answers__question').all()
    dept_map = dict(DEPARTMENT_CHOICES)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Detailed MBA Results"

    # Dizayn uchun uslublar
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a3c5e")
    top_align = Alignment(vertical="top", wrap_text=True)

    # 1. Excel Header (Sarlavha) qismini shakllantirish
    headers = ["Full Name", "Phone", "Date", "Group", "Teacher", "Departments"]
    for i in range(1, 13): # 12 ta savol uchun joy
        headers.append(f"Q&A {i}")

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        # Ustun kengligini sozlash
        column_letter = ws.cell(row=1, column=col).column_letter
        ws.column_dimensions[column_letter].width = 20 if col <= 6 else 60

    # 2. Ma'lumotlarni qatorma-qator to'ldirish
    for row_num, session in enumerate(sessions, 2):
        dept_display = ', '.join([dept_map.get(d, d) for d in session.get_departments_list()])
        
        # Asosiy talaba ma'lumotlari
        ws.cell(row=row_num, column=1, value=session.full_name).alignment = top_align
        ws.cell(row=row_num, column=2, value=session.phone).alignment = top_align
        ws.cell(row=row_num, column=3, value=str(session.exam_date)).alignment = top_align
        ws.cell(row=row_num, column=4, value=session.group).alignment = top_align
        ws.cell(row=row_num, column=5, value=session.teacher).alignment = top_align
        ws.cell(row=row_num, column=6, value=dept_display).alignment = top_align

        # Talabaga tushgan individual savollar va uning javoblari
        ans_col = 7
        # Har bir talaba uchun o'ziga tushgan savollarni tartibi bilan chiqaramiz
        user_answers = session.answers.select_related('question').all().order_by('question__order')
        
        for ans in user_answers:
            if ans_col > 18: break # Jami 12 ta ustundan chiqib ketmaslik uchun
            
            question_text = ans.question.text
            student_answer = ans.selected_option.upper() if ans.selected_option else ans.answer_text
            
            # Katak ichida savol va javobni birlashtiramiz
            combined_data = f"SAVOL: {question_text}\n\nJAVOB: {student_answer}"
            
            cell = ws.cell(row=row_num, column=ans_col, value=combined_data)
            cell.alignment = top_align
            ans_col += 1

    # 3. Faylni yuklash uchun tayyorlash
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = f"MBA_Results_{timezone.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    
    return response