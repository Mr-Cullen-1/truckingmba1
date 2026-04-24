from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
import random
import openpyxl
from openpyxl.styles import Font, PatternFill

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

    # Build personalized question set
    selected_depts = session.get_departments_list()

    # Always 2 from Career Center
    career_qs = list(Question.objects.filter(department='career', is_active=True))
    career_questions = random.sample(career_qs, min(2, len(career_qs)))

    # 10 from selected departments combined
    dept_qs = list(Question.objects.filter(
        department__in=selected_depts, is_active=True
    ))
    if len(dept_qs) <= 10:
        dept_questions = dept_qs
    else:
        dept_questions = random.sample(dept_qs, 10)

    dept_questions.sort(key=lambda q: q.order)
    career_questions.sort(key=lambda q: q.order)

    questions = dept_questions + career_questions

    return render(request, 'exam/exam.html', {
        'session': session,
        'questions': questions,
        'exam_duration': 20 * 60,
        'warning_time': 5 * 60,
    })


def done_view(request):
    return render(request, 'exam/done.html')


@staff_member_required
def admin_results_view(request):
    sessions = ExamSession.objects.prefetch_related('answers__question').all()
    dept_map = dict(DEPARTMENT_CHOICES)

    rows = []
    for session in sessions:
        dept_display = ', '.join([dept_map.get(d, d) for d in session.get_departments_list()])
        answered = []
        for ans in session.answers.select_related('question').all():
            val = ans.selected_option.upper() if ans.selected_option else ans.answer_text
            answered.append({
                'dept': ans.question.get_department_display(),
                'title': ans.question.title,
                'value': val,
            })
        rows.append({
            'session': session,
            'dept_display': dept_display,
            'answered': answered,
        })

    return render(request, 'exam/admin_results.html', {'rows': rows})


@staff_member_required
def export_excel_view(request):
    sessions = ExamSession.objects.prefetch_related('answers__question').all()
    dept_map = dict(DEPARTMENT_CHOICES)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Exam Results"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a3c5e")

    headers = ["Full Name", "Phone", "Date", "Group", "Teacher",
               "Departments", "Started", "Submitted", "Complete"]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 22

    for row_num, session in enumerate(sessions, 2):
        dept_display = ', '.join([dept_map.get(d, d) for d in session.get_departments_list()])
        row = [
            session.full_name,
            session.phone,
            str(session.exam_date),
            session.group,
            session.teacher,
            dept_display,
            session.started_at.strftime("%Y-%m-%d %H:%M") if session.started_at else "",
            session.submitted_at.strftime("%Y-%m-%d %H:%M") if session.submitted_at else "",
            "Yes" if session.is_complete else "No",
        ]
        for col, val in enumerate(row, 1):
            ws.cell(row=row_num, column=col, value=val)

        ans_col = len(headers) + 1
        for ans in session.answers.select_related('question').all():
            val = ans.selected_option.upper() if ans.selected_option else ans.answer_text
            label = f"[{ans.question.get_department_display()}] {ans.question.title}"
            ws.cell(row=1, column=ans_col, value=label).font = header_font
            ws.cell(row=1, column=ans_col).fill = header_fill
            ws.column_dimensions[ws.cell(row=1, column=ans_col).column_letter].width = 30
            ws.cell(row=row_num, column=ans_col, value=val)
            ans_col += 1

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="exam_results.xlsx"'
    wb.save(response)
    return response