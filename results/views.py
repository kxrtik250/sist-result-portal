import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Student, Result, AIAnalysis
from .ai_helper import generate_ai_analysis, get_grade_point, calculate_gpa


# ── Auth ───────────────────────────────────────────────────────

def student_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        reg_no   = request.POST.get('register_number', '').strip()
        name     = request.POST.get('name', '').strip()
        dept     = request.POST.get('department', '').strip()

        if not all([username, password, reg_no, name, dept]):
            return render(request, 'register.html', {'error': 'All fields are required.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken.'})
        if Student.objects.filter(register_number=reg_no).exists():
            return render(request, 'register.html', {'error': 'Register number already exists.'})
        if len(password) < 6:
            return render(request, 'register.html', {'error': 'Password must be at least 6 characters.'})

        user = User.objects.create_user(username=username, password=password)
        Student.objects.create(user=user, register_number=reg_no, name=name, department=dept)
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not password:
            return render(request, 'login.html', {'error': 'Both fields are required.'})
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('staff_dashboard' if user.is_staff else 'student_dashboard')
        return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


# ── Student ────────────────────────────────────────────────────

@login_required
def student_dashboard(request):
    student     = get_object_or_404(Student, user=request.user)
    semester    = request.GET.get('semester', '')
    all_results = Result.objects.filter(student=student)
    results     = all_results.filter(semester=semester) if semester else all_results
    analysis    = AIAnalysis.objects.filter(student=student).first()
    semesters   = all_results.values_list('semester', flat=True).distinct().order_by('semester')

    cgpa        = calculate_gpa(list(all_results))
    sem_list    = list(results)
    sem_gpa     = calculate_gpa(sem_list)
    sem_total   = sum(r.marks for r in sem_list)
    sem_count   = len(sem_list)
    sem_avg     = round(sem_total / sem_count, 1) if sem_count else 0
    sem_weak    = min(sem_list, key=lambda r: r.marks) if sem_list else None
    sem_best    = max(sem_list, key=lambda r: r.marks) if sem_list else None

    if sem_avg >= 90:
        sem_performance = "Excellent"
    elif sem_avg >= 75:
        sem_performance = "Good"
    elif sem_avg >= 50:
        sem_performance = "Average"
    else:
        sem_performance = "Needs Improvement"

    subject_analysis = {}
    if analysis and analysis.subject_analysis:
        try:
            subject_analysis = json.loads(analysis.subject_analysis)
        except Exception:
            pass

    results_with_gp = [{
        'result'      : r,
        'grade_point' : get_grade_point(r.marks),
        'suggestion'  : subject_analysis.get(r.subject, {}).get('suggestion', ''),
        'status'      : subject_analysis.get(r.subject, {}).get('status', ''),
    } for r in results]

    return render(request, 'student_dashboard.html', {
        'student'           : student,
        'results'           : results,
        'results_with_gp'   : results_with_gp,
        'analysis'          : analysis,
        'semesters'         : semesters,
        'selected_semester' : semester,
        'cgpa'              : cgpa,
        'sem_gpa'           : sem_gpa,
        'sem_total'         : sem_total,
        'sem_avg'           : sem_avg,
        'sem_weak'          : sem_weak,
        'sem_best'          : sem_best,
        'sem_performance'   : sem_performance,
    })


@login_required
def download_pdf(request):
    # Imports inside function so missing package won't crash the app
    try:
        import io
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
    except ImportError:
        return HttpResponse(
            "PDF library not installed. Run: pip install reportlab",
            status=500
        )

    student     = get_object_or_404(Student, user=request.user)
    all_results = Result.objects.filter(student=student)
    analysis    = AIAnalysis.objects.filter(student=student).first()
    cgpa        = calculate_gpa(list(all_results))

    buffer   = io.BytesIO()
    doc      = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=60, bottomMargin=40
    )
    elements = []

    title_style = ParagraphStyle(
        'title', fontSize=20, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=6
    )
    sub_style = ParagraphStyle(
        'sub', fontSize=11,
        textColor=colors.grey, spaceAfter=20
    )

    elements.append(Paragraph("Student Result Marksheet", title_style))
    elements.append(Paragraph("Official Academic Record", sub_style))

    info_data = [
        ['Student Name', student.name, 'Register No', student.register_number],
        ['Department', student.department, 'CGPA', f"{cgpa} / 10"],
    ]
    info_table = Table(info_data, colWidths=[110, 150, 110, 130])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4f8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4f8')),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME',   (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',   (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 10),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING',    (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    semesters = all_results.values_list('semester', flat=True).distinct().order_by('semester')
    for sem in semesters:
        sem_results = all_results.filter(semester=sem)
        sem_gpa     = calculate_gpa(list(sem_results))

        sem_heading = ParagraphStyle(
            'semh', fontSize=12, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#667eea'),
            spaceAfter=8, spaceBefore=14
        )
        elements.append(Paragraph(f"{sem}  |  GPA: {sem_gpa}/10", sem_heading))

        data = [['Subject', 'Marks', 'Grade', 'Grade Point']]
        for r in sem_results:
            data.append([r.subject, f"{r.marks}/100", r.grade,
                          f"{get_grade_point(r.marks)}/10"])

        t = Table(data, colWidths=[200, 100, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
            ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID',           (0, 0), (-1, -1), 0.5,
             colors.HexColor('#dee2e6')),
            ('ALIGN',          (1, 0), (-1, -1), 'CENTER'),
            ('PADDING',        (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)

    if analysis:
        elements.append(Spacer(1, 20))
        ai_heading = ParagraphStyle(
            'aih', fontSize=13, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2e7d32'),
            spaceAfter=8, spaceBefore=10
        )
        elements.append(Paragraph("AI Performance Analysis", ai_heading))
        ai_data = [
            ['Overall CGPA',   f"{cgpa}/10"],
            ['Performance',    analysis.performance],
            ['Overall Grade',  analysis.overall_grade],
            ['Weak Subject',   analysis.weak_subject],
            ['Strengths',      analysis.strengths or 'N/A'],
            ['Suggestion',     analysis.suggestion],
            ['Predicted CGPA', analysis.predicted_cgpa or 'N/A'],
        ]
        ai_table = Table(ai_data, colWidths=[150, 350])
        ai_table.setStyle(TableStyle([
            ('FONTNAME',       (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE',       (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1),
             [colors.HexColor('#e8f5e9'), colors.white]),
            ('GRID',           (0, 0), (-1, -1), 0.5,
             colors.HexColor('#dee2e6')),
            ('PADDING',        (0, 0), (-1, -1), 8),
            ('VALIGN',         (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(ai_table)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{student.register_number}_marksheet.pdf"'
    )
    return response


# ── Staff ──────────────────────────────────────────────────────

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('student_dashboard')

    query    = request.GET.get('search', '').strip()
    semester = request.GET.get('semester', '')

    results = Result.objects.select_related('student').all()
    if query:
        from django.db.models import Q
        results = results.filter(
            Q(student__register_number__icontains=query) |
            Q(student__name__icontains=query)
        )
    if semester:
        results = results.filter(semester=semester)

    paginator    = Paginator(results.order_by('-id'), 15)
    page_number  = request.GET.get('page')
    page_obj     = paginator.get_page(page_number)

    students      = Student.objects.select_related('user').all()
    all_semesters = Result.objects.values_list(
        'semester', flat=True
    ).distinct().order_by('semester')

    return render(request, 'staff_dashboard.html', {
        'page_obj'      : page_obj,
        'students'      : students,
        'total_students': students.count(),
        'total_results' : Result.objects.count(),
        'all_semesters' : all_semesters,
        'selected_sem'  : semester,
        'search_query'  : query,
    })


@login_required
def add_result(request):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    error = None
    if request.method == 'POST':
        reg_no = request.POST.get('register_number', '').strip()
        marks  = request.POST.get('marks', '0')
        try:
            marks_int = int(marks)
            if not (0 <= marks_int <= 100):
                raise ValueError
        except ValueError:
            return render(request, 'add_result.html',
                          {'error': 'Marks must be between 0 and 100.'})
        try:
            student = Student.objects.get(register_number=reg_no)
            Result.objects.create(
                student  = student,
                subject  = request.POST.get('subject', '').strip(),
                marks    = marks_int,
                grade    = request.POST.get('grade', ''),
                semester = request.POST.get('semester', ''),
            )
            generate_ai_analysis(student)
            messages.success(request, 'Result added successfully!')
            return redirect('staff_dashboard')
        except Student.DoesNotExist:
            error = f"No student found with register number '{reg_no}'."
    return render(request, 'add_result.html', {'error': error})


@login_required
def edit_result(request, result_id):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    result = get_object_or_404(Result, id=result_id)
    if request.method == 'POST':
        try:
            marks = int(request.POST.get('marks', 0))
            if not (0 <= marks <= 100):
                raise ValueError
        except ValueError:
            return render(request, 'edit_result.html',
                          {'result': result,
                           'error': 'Marks must be between 0 and 100.'})
        result.subject  = request.POST.get('subject', '').strip()
        result.marks    = marks
        result.grade    = request.POST.get('grade', '')
        result.semester = request.POST.get('semester', '')
        result.save()
        generate_ai_analysis(result.student)
        messages.success(request, 'Result updated successfully!')
        return redirect('staff_dashboard')
    return render(request, 'edit_result.html', {'result': result})


@login_required
def delete_result(request, result_id):
    if request.user.is_staff and request.method == 'POST':
        Result.objects.filter(id=result_id).delete()
        messages.success(request, 'Result deleted.')
    return redirect('staff_dashboard')


@login_required
def delete_student(request, student_id):
    if request.user.is_staff and request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        student.user.delete()
        messages.success(request, 'Student deleted.')
    return redirect('staff_dashboard')


@login_required
def delete_all_results(request):
    if request.user.is_staff and request.method == 'POST':
        Result.objects.all().delete()
        AIAnalysis.objects.all().delete()
        messages.success(request, 'All results deleted.')
    return redirect('staff_dashboard')


@login_required
def view_student(request, student_id):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    student   = get_object_or_404(Student, id=student_id)
    results   = Result.objects.filter(student=student).order_by('semester')
    analysis  = AIAnalysis.objects.filter(student=student).first()
    semesters = results.values_list('semester', flat=True).distinct()
    cgpa      = calculate_gpa(list(results))

    subject_analysis = {}
    if analysis and analysis.subject_analysis:
        try:
            subject_analysis = json.loads(analysis.subject_analysis)
        except Exception:
            pass

    results_with_gp = [{
        'result'      : r,
        'grade_point' : get_grade_point(r.marks),
        'suggestion'  : subject_analysis.get(r.subject, {}).get('suggestion', ''),
        'status'      : subject_analysis.get(r.subject, {}).get('status', ''),
    } for r in results]

    return render(request, 'view_student.html', {
        'student'         : student,
        'results'         : results,
        'results_with_gp' : results_with_gp,
        'analysis'        : analysis,
        'semesters'       : semesters,
        'cgpa'            : cgpa,
    })


@login_required
def upload_excel(request):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            import openpyxl
        except ImportError:
            messages.error(request, 'Excel library not installed. Run: pip install openpyxl')
            return redirect('staff_dashboard')

        excel_file = request.FILES['excel_file']
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload a valid .xlsx file.')
            return redirect('staff_dashboard')
        try:
            wb            = openpyxl.load_workbook(excel_file)
            ws            = wb.active
            success_count = 0
            error_list    = []
            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):
                    continue
                try:
                    reg_no, subject, marks, grade, semester = row[:5]
                    marks   = int(marks)
                    if not (0 <= marks <= 100):
                        raise ValueError("Marks out of range")
                    student = Student.objects.get(
                        register_number=str(reg_no).strip()
                    )
                    Result.objects.create(
                        student  = student,
                        subject  = str(subject).strip(),
                        marks    = marks,
                        grade    = str(grade).strip(),
                        semester = str(semester).strip(),
                    )
                    generate_ai_analysis(student)
                    success_count += 1
                except Student.DoesNotExist:
                    error_list.append(
                        f"Row {i}: Register number '{reg_no}' not found."
                    )
                except Exception as e:
                    error_list.append(f"Row {i}: {str(e)}")

            if success_count:
                messages.success(
                    request, f'{success_count} results uploaded successfully!'
                )
            for err in error_list[:5]:
                messages.error(request, err)
        except Exception as e:
            messages.error(request, f'Failed to read file: {str(e)}')
    return redirect('staff_dashboard')