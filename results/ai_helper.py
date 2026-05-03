import json
import google.generativeai as genai
from django.conf import settings
from .models import Result, AIAnalysis


def get_grade_point(marks):
    if marks >= 91:   return 10
    elif marks >= 81: return 9
    elif marks >= 71: return 8
    elif marks >= 61: return 7
    elif marks >= 51: return 6
    elif marks >= 41: return 5
    else:             return 0


def calculate_gpa(results):
    if not results:
        return 0.0
    total = sum(get_grade_point(r.marks) for r in results)
    return round(total / len(results), 2)


# Sathyabama CSE R2023 — subject-wise study tips
SUBJECT_TIPS = {
    # Semester 1
    "technical english": (
        "Practice reading comprehension and essay writing daily. "
        "Focus on grammar rules, letter writing, and report formats."
    ),
    "matrices and calculus": (
        "Revise matrix operations, eigenvalues, and calculus theorems. "
        "Solve 10 problems daily from Kreyszig or previous papers."
    ),
    "chemistry": (
        "Make reaction-wise short notes. Practice balancing equations "
        "and electrochemistry numericals daily."
    ),
    "electrical and electronics engineering": (
        "Revise Kirchhoff's laws, op-amp circuits, and network theorems. "
        "Practice circuit problems from previous question papers."
    ),
    "programming in c": (
        "Practice pointer problems, arrays, and file handling daily. "
        "Write at least one C program every day to build logic."
    ),
    "chemistry lab": (
        "Revise experiment procedures and viva questions. "
        "Practice calculations for titration and estimation experiments."
    ),
    # Semester 2
    "advanced calculus and statistics": (
        "Focus on Fourier series, Laplace transforms, and probability. "
        "Solve 10 statistics problems daily from textbook exercises."
    ),
    "physics": (
        "Revise optics, quantum mechanics, and semiconductor formulas. "
        "Practice numerical problems chapter by chapter."
    ),
    "data structures": (
        "Practice linked lists, stacks, queues, trees, and graphs daily. "
        "Implement each data structure in C from scratch."
    ),
    "programming in python": (
        "Practice list comprehensions, file handling, and OOP in Python. "
        "Build one small Python script daily to strengthen concepts."
    ),
    "engineering drawing and design": (
        "Practice orthographic projections and isometric views daily. "
        "Revise AutoCAD commands and geometric construction methods."
    ),
    "data structures lab": (
        "Implement sorting algorithms and tree traversals from scratch. "
        "Focus on time complexity analysis of each program."
    ),
    # Semester 3
    "discrete mathematics and numerical methods": (
        "Focus on graph theory, set theory, and numerical integration. "
        "Practice proofs and numerical method problems from previous papers."
    ),
    "computer architecture and organization": (
        "Revise ALU design, memory hierarchy, pipelining, and cache. "
        "Draw diagrams of CPU components and practice instruction formats."
    ),
    "theory of computation": (
        "Practice DFA, NFA, PDA construction and conversion problems. "
        "Focus on pumping lemma proofs and Turing machine design."
    ),
    "digital logic circuits": (
        "Revise Boolean algebra, K-maps, and flip-flop circuits. "
        "Practice combinational and sequential circuit design problems."
    ),
    "microprocessor and microcontroller": (
        "Practice 8085 and 8051 assembly language programs daily. "
        "Revise interrupt handling and memory interfacing concepts."
    ),
    "programming in java": (
        "Practice OOP concepts: inheritance, polymorphism, and interfaces. "
        "Build small Java projects using collections and exception handling."
    ),
    "universal human values": (
        "Revise modules on harmony in family and society. "
        "Write reflective notes on value-based living for exams."
    ),
    # Semester 4
    "probability and statistics": (
        "Focus on probability distributions, hypothesis testing, and regression. "
        "Solve statistical inference problems from previous year papers."
    ),
    "operating systems and unix": (
        "Revise CPU scheduling, deadlock prevention, and memory management. "
        "Practice UNIX shell commands and system call programs."
    ),
    "database management systems": (
        "Practice SQL queries, normalization, and ER diagram design daily. "
        "Focus on transaction management and relational algebra."
    ),
    "design thinking and innovations": (
        "Work on empathy mapping and prototype-building exercises. "
        "Revise design thinking stages and innovation frameworks."
    ),
    # Semester 5
    "data communication and computer networks": (
        "Revise OSI and TCP/IP layers thoroughly. "
        "Practice subnetting problems and protocol comparison questions."
    ),
    "design and analysis of algorithms": (
        "Practice greedy, dynamic programming, and divide-and-conquer problems. "
        "Analyze time and space complexity of each algorithm."
    ),
    "software engineering design and development": (
        "Revise SDLC models, UML diagrams, and software testing techniques. "
        "Practice drawing class, sequence, and use case diagrams."
    ),
    "augmented and virtual reality": (
        "Focus on AR/VR frameworks, display technologies, and interaction design. "
        "Revise Unity basics and 3D coordinate transformations."
    ),
    # Semester 6
    "compiler design": (
        "Practice lexical analysis, parsing techniques, and code generation. "
        "Focus on LL(1) and LR parsing table construction."
    ),
    "network security": (
        "Revise cryptographic algorithms, PKI, and firewall concepts. "
        "Practice encryption and decryption problems from previous papers."
    ),
    "parallel and distributed computing": (
        "Focus on parallel algorithms, MPI programming, and distributed systems. "
        "Revise consistency models and distributed transaction concepts."
    ),
    "machine learning": (
        "Implement supervised and unsupervised learning algorithms from scratch. "
        "Practice on real datasets using scikit-learn and analyze results."
    ),
    "compiler design lab": (
        "Implement lexical analyzer and parser using LEX and YACC. "
        "Focus on building a mini compiler step by step."
    ),
    # Semester 7
    "artificial intelligence": (
        "Practice search algorithms: BFS, DFS, A*, and heuristic methods. "
        "Revise knowledge representation, logic, and planning problems."
    ),
    "big data analytics": (
        "Practice Hadoop MapReduce and Spark programs on sample datasets. "
        "Focus on Hive queries and data pipeline design."
    ),
    "project phase 1": (
        "Define clear project objectives and complete literature survey. "
        "Prepare a detailed project proposal with timeline and methodology."
    ),
    # Semester 8
    "project phase 2": (
        "Focus on implementation, testing, and documentation of your project. "
        "Prepare a clear presentation with results, graphs, and future scope."
    ),
}


def get_subject_suggestion(subject, marks):
    subject_lower = subject.lower().strip()
    for key, tip in SUBJECT_TIPS.items():
        if key in subject_lower or subject_lower in key:
            return tip
    return (
        f"Revise {subject} core concepts from the textbook thoroughly. "
        f"Solve previous year Sathyabama question papers regularly."
    )


def generate_ai_analysis(student):
    results = list(Result.objects.filter(student=student))
    if not results:
        return

    total_marks = sum(r.marks for r in results)
    max_marks   = len(results) * 100
    percentage  = (total_marks / max_marks) * 100
    cgpa        = calculate_gpa(results)

    if percentage >= 90:   grade = "O"
    elif percentage >= 75: grade = "A"
    elif percentage >= 60: grade = "B"
    elif percentage >= 50: grade = "C"
    else:                  grade = "F"

    if percentage >= 90:   performance = "Excellent"
    elif percentage >= 75: performance = "Good"
    elif percentage >= 50: performance = "Average"
    else:                  performance = "Poor"

    weak_result  = min(results, key=lambda r: r.marks)
    weak_subject = weak_result.subject
    suggestion   = get_subject_suggestion(weak_subject, weak_result.marks)

    strong_list = [r.subject for r in results if r.marks >= 75]
    strengths   = (
        ", ".join(strong_list)
        if strong_list
        else "Keep improving — aim for above 75 in all subjects"
    )

    cgpa_float = float(cgpa)
    if performance == "Excellent":
        predicted = round(min(10.0, cgpa_float + 0.3), 2)
    elif performance == "Good":
        predicted = round(min(10.0, cgpa_float + 0.2), 2)
    elif performance == "Average":
        predicted = round(max(0.0, cgpa_float + 0.1), 2)
    else:
        predicted = round(max(0.0, cgpa_float - 0.2), 2)

    subject_analysis = {}
    for r in results:
        subject_analysis[r.subject] = {
            'marks'      : r.marks,
            'grade_point': get_grade_point(r.marks),
            'suggestion' : get_subject_suggestion(r.subject, r.marks),
            'status'     : (
                "Excellent"         if r.marks >= 90 else
                "Good"              if r.marks >= 75 else
                "Average"           if r.marks >= 50 else
                "Needs Improvement"
            )
        }

    # Try Gemini for enhanced suggestion
    try:
        subjects_text = "\n".join(
            [f"- {r.subject}: {r.marks}/100" for r in results]
        )
        prompt = (
            "You are an academic counselor at Sathyabama Institute of Science "
            "and Technology analyzing a B.E. CSE student's performance.\n\n"
            f"Student: {student.name}\n"
            f"Department: Computer Science and Engineering\n"
            f"CGPA: {cgpa}/10\n"
            f"Percentage: {round(percentage, 1)}%\n\n"
            f"Subject-wise marks (Sathyabama R2023 curriculum):\n"
            f"{subjects_text}\n\n"
            "Respond in EXACTLY this format (one line each, no extra text):\n"
            "Performance: [Excellent/Good/Average/Poor]\n"
            "Weak Subject: [subject with lowest marks]\n"
            "Suggestion: [one specific actionable tip for that subject]\n"
        )
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model    = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        for line in response.text.strip().split('\n'):
            line = line.strip()
            if line.startswith("Performance:"):
                performance  = line.replace("Performance:", "").strip()
            elif line.startswith("Weak Subject:"):
                weak_subject = line.replace("Weak Subject:", "").strip()
            elif line.startswith("Suggestion:"):
                suggestion   = line.replace("Suggestion:", "").strip()
    except Exception:
        pass

    AIAnalysis.objects.update_or_create(
        student  = student,
        defaults = {
            'total_marks'     : total_marks,
            'overall_grade'   : grade,
            'performance'     : performance,
            'weak_subject'    : weak_subject,
            'suggestion'      : suggestion,
            'cgpa'            : str(cgpa),
            'subject_analysis': json.dumps(subject_analysis),
            'strengths'       : strengths,
            'predicted_cgpa'  : str(predicted),
        }
    )