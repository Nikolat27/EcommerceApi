from rest_framework.permissions import BasePermission


def OnlyPostMethod(request):
    if request.method == "POST":
        return True
    else:
        return False
    