from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.user_login,        name='login'),
    path('register/',                               views.student_register,  name='register'),
    path('logout/',                                 views.user_logout,       name='logout'),
    path('student/',                                views.student_dashboard, name='student_dashboard'),
    path('student/download-pdf/',                   views.download_pdf,      name='download_pdf'),
    path('staff/',                                  views.staff_dashboard,   name='staff_dashboard'),
    path('staff/add/',                              views.add_result,        name='add_result'),
    path('staff/edit/<int:result_id>/',             views.edit_result,       name='edit_result'),
    path('staff/delete/<int:result_id>/',           views.delete_result,     name='delete_result'),
    path('staff/delete-student/<int:student_id>/',  views.delete_student,    name='delete_student'),
    path('staff/delete-all/',                       views.delete_all_results,name='delete_all_results'),
    path('staff/view-student/<int:student_id>/',    views.view_student,      name='view_student'),
    path('staff/upload-excel/',                     views.upload_excel,      name='upload_excel'),
]