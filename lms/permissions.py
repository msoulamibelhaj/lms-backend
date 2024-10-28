from rest_framework.permissions import BasePermission

# Permission for users who are in the 'Teacher' group
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in the 'Teacher' group
        return request.user.groups.filter(name='Teacher').exists()

# Permission for users who are in the 'Admin' group
class IsSchoolAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in the 'Admin' group
        return request.user.groups.filter(name='Admin').exists()

# Permission for users who are in the 'Student' group
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in the 'Student' group
        return request.user.groups.filter(name='Student').exists()