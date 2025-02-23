from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import Task


# Setups the initial users and tasks for testing purposes
def create_initial_users():
    users = [
        {"username": "alice", "password": "redqueen", "tasks": [
            {"title": "Alice's Task 1", "description": "Description for Alice's Task 1"},
            {"title": "Alice's Task 2", "description": "Description for Alice's Task 2"},
        ]},
        {"username": "bob", "password": "squarepants", "tasks": [
            {"title": "Bob's Task", "description": "Description for Bob's Task"},
        ]},
    ]

    for user_data in users:
        if not User.objects.filter(username=user_data["username"]).exists():
            # Create the user
            user = User.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],
            )

            # Create tasks for the user
            for task_data in user_data["tasks"]:
                Task.objects.create(
                    user=user,
                    title=task_data["title"],
                    description=task_data["description"]
                )

create_initial_users()


# Welcome page
def index(request):
    return render(request, 'index.html')


# Login to dashboard
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html')
    return render(request, 'login.html')


# Main dashboard to view tasks, add tasks, and delete tasks
@login_required
def dashboard(request):
    query = request.GET.get('query', '')

    # SQL INJECTION - VULNERABLE, this query "%' OR 1=1 --" allows an attacker to retrieve all tasks
    with connection.cursor() as cursor:
        if query:
            sql_query = f"SELECT * FROM tasks_task WHERE user_id = {request.user.id} AND title LIKE '%{query}%'"
        else:
            sql_query = f"SELECT * FROM tasks_task WHERE user_id = {request.user.id}"

        """
        # SQL INJECTION - FIXED, replace above code with the following code
        with connection.cursor() as cursor:
            if query:
                sql_query = "SELECT id, title, description FROM tasks_task WHERE user_id = %s AND title LIKE %s"
                cursor.execute(sql_query, [request.user.id, f"%{query}%"])
            else:
                sql_query = "SELECT id, title, description FROM tasks_task WHERE user_id = %s"
                cursor.execute(sql_query, [request.user.id])
        """

        # Executing the query, injection happens here
        cursor.execute(sql_query)

        # Changing to suitable format for rendering
        tasks = [{"id": row[0], "title": row[1], "description": row[2]} for row in cursor.fetchall()]

    return render(request, 'dashboard.html', {'tasks': tasks})


# View for the creation of tasks based on user submitted form's data
@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        Task.objects.create(title=title, description=description, user=request.user)
    return redirect('dashboard')


# View for the deletion of tasks through the button on the dashboard
@login_required
def delete_task(request, task_id):
    # BROKEN ACCESS CONTROL - VULNERABLE, users can delete tasks that do not belong to them
    task = Task.objects.get(id=task_id)
    
    """
    # BROKEN ACCESS CONTROL - FIXED, simply uncomment the following code
    if task.user != request.user:
        return redirect('dashboard')
    """
    
    task.delete()
    return redirect('dashboard')


# View for the logout button
def logout_view(request):
    logout(request)
    return redirect('login')


# View for the CSRF exploit page to test flaw 4
def csrf_exploit_view(request):
    return render(request, 'csrf_exploit.html')