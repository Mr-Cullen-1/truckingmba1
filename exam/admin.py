from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from .models import Question, ExamSession, Answer, DEPARTMENT_CHOICES


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['order', 'department', 'question_type', 'title', 'is_active']
    list_display_links = ['title']
    list_editable = ['order', 'is_active']
    list_filter = ['department', 'question_type', 'is_active']
    search_fields = ['title', 'text']
    fieldsets = (
        ('Question Info', {
            'fields': ('department', 'question_type', 'title', 'text', 'order', 'is_active')
        }),
        ('MCQ Options (leave blank for open questions)', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'classes': ('collapse',),
        }),
    )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'answer_text']
    can_delete = False


def export_sessions_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Exam Results"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a3c5e")
    center = Alignment(horizontal="center", vertical="center")

    base_headers = ["ID", "Full Name", "Phone", "Date", "Group", "Teacher",
                    "Departments", "Started At", "Submitted At", "Complete"]

    for col, header in enumerate(base_headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 22

    for row_num, session in enumerate(queryset, 2):
        dept_map = dict(DEPARTMENT_CHOICES)
        dept_display = ', '.join([dept_map.get(d, d) for d in session.get_departments_list()])

        row_data = [
            session.id,
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

        for col, val in enumerate(row_data, 1):
            ws.cell(row=row_num, column=col, value=val)

        # Write answers after base columns
        ans_col = len(base_headers) + 1
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

export_sessions_excel.short_description = "📥 Export selected to Excel"


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'group', 'teacher', 'exam_date',
                    'departments', 'started_at', 'submitted_at', 'is_complete']
    list_filter = ['is_complete', 'exam_date', 'group', 'teacher']
    search_fields = ['full_name', 'phone', 'group', 'teacher']
    readonly_fields = ['started_at', 'submitted_at']
    inlines = [AnswerInline]
    actions = [export_sessions_excel]