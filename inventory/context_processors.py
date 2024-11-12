def user_role(request):
    role = None

    if request.user.is_authenticated:
        if request.user.groups.filter(name='manager').exists():
            role = 'Manager'
        elif request.user.groups.filter(name='employee').exists():
            role = 'Employee'

    return {
        'username': request.user.username if request.user.is_authenticated else None,
        'role': role
    }
