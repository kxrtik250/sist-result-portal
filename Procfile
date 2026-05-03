web: python manage.py migrate && python manage.py shell -c "from
django.contrib.auth.models import User;
User.objects.filter(username='admin').exists() or
User.objects.create_superuser('admin', 'admin@sist.ac.in', 'Admin@1234')" &&
gunicorn student_result_system.wsgi --log-file -