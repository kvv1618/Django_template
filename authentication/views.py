from django.urls import include, re_path
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from authentication.models import CustomUser
from django.contrib.auth.models import User



class CustomUserCreateView(APIView):
    def post(self, request):
        name = request.POST.get('name') if request.POST.get('name') else None
        password = request.POST.get('password') if request.POST.get('password') else None
        email = request.POST.get('email') if request.POST.get('email') else None
        role = request.POST.get('role') if request.POST.get('role') else None

        if name and password and email and role:

            if User.objects.filter(username=name).exists():
                return JsonResponse({'message': 'User already exists'}, status=400)

            user = User.objects.create_user(username=name, password=password, email=email)
        else:
            return JsonResponse({'message': 'User not created. Details not sufficient! Need name, password, email and role'})

        student = CustomUser.objects.create(
            user=user,
            role=role
        )
        user.save()
        student.save()
        return JsonResponse({'name': student.user.username, 'email': student.user.email, 'role': student.role})

