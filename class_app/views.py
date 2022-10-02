from os import path
from django.urls import include, re_path
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication as authentication_simplejwt
from rest_framework_swagger.views import get_swagger_view

from authentication.models import CustomUser
from .models import Classroom, File
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class ClassView(APIView):
    authentication_classes = [authentication_simplejwt.JWTAuthentication]

    def get(self, request):
        user = get_object_or_404(CustomUser, user=request.user)
        print(user)
        role = user.role

        if role == "student":
            classes = user.classrooms.all()
            response = [
                {
                    "id": classroom.id,
                    "name": classroom.name,
                    "created_by": classroom.created_by.user.username,
                    "created_at": classroom.created_at,
                    "files": [file.file.name for file in classroom.files.all()],
                    "students": [
                        student.user.username for student in classroom.students.all()
                    ],
                }
                for classroom in classes
            ]
            return JsonResponse(
                {"classes": response},
            )
        elif role == "teacher":
            classes = user.owner.all()
            response = [
                {
                    "id": classroom.id,
                    "name": classroom.name,
                    "created_by": classroom.created_by.user.username,
                    "created_at": classroom.created_at,
                    "files": [file.file.name for file in classroom.files.all()],
                    "students": [
                        student.user.username for student in classroom.students.all()
                    ],
                }
                for classroom in classes
            ]
            return JsonResponse(
                {"classes": response},
            )

    @swagger_auto_schema(operation_description="POST API for ClassView")
    def post(self, request):
        role = request.user.custom_user.role
        if role == "student":
            return JsonResponse({"message": "You are not allowed to create a class"})

        name = request.POST.get("name") if request.POST.get("name") else None
        students = (
            request.POST.get("students") if request.POST.get("students") else None
        )
        file = request.FILES.get("file") if request.FILES.get("file") else None
        user = get_object_or_404(CustomUser, user=request.user)

        if name and file:
            if Classroom.objects.filter(name=name).exists():
                return JsonResponse({"message": "Class already exists"})

            classroom = Classroom.objects.create(
                name=name,
                created_by=user,
            )

            for student in students.split(" "):
                student_obj = (
                    CustomUser.objects.get(user__username=student)
                    if CustomUser.objects.filter(user__username=student).exists()
                    else None
                )
                if not student_obj:
                    return JsonResponse(
                        {"message": f"Student {student} does not exist"}
                    )
                classroom.students.add(student_obj)

            if file:

                file = File.objects.create(
                    name=file.name, type=file.content_type, file=file
                )
                file.save()
                classroom.files.add(file)
            classroom.save()

            response = {
                "id": classroom.id,
                "name": classroom.name,
                "created_by": classroom.created_by.user.username,
                "created_at": classroom.created_at,
                "files": [file.file.name for file in classroom.files.all()],
                "students": [
                    student.user.username for student in classroom.students.all()
                ],
            }
            return JsonResponse(
                {"class": response},
            )
        else:
            return JsonResponse(
                {
                    "message": "Classroom not created. Details not sufficient! Need name and file."
                }
            )

    def patch(self, request):
        class_id = request.POST.get("class_id")
        role = request.user.custom_user.role
        if role == "student":
            return JsonResponse({"message": "You are not allowed to create a class"})

        classroom = get_object_or_404(Classroom, id=class_id)

        file = request.FILES.get("file") if request.FILES.get("file") else None

        if file:
            file = File.objects.create(
                name=file.name, type=file.content_type, file=file
            )
            file.save()
            classroom.files.add(file)
            classroom.save()

        students_add = (
            request.POST.get("students_add")
            if request.POST.get("students_add")
            else None
        )

        if students_add:
            for student in students_add.split(" "):
                student_obj = (
                    CustomUser.objects.get(user__username=student)
                    if CustomUser.objects.filter(user__username=student).exists()
                    else None
                )
                if not student_obj:
                    return JsonResponse(
                        {"message": f"Student {student} does not exist"}
                    )
                classroom.students.add(student_obj)
            classroom.save()

        students_remove = (
            request.POST.get("students_remove")
            if request.POST.get("students_remove")
            else None
        )

        if students_remove:
            for student in students_remove.split(" "):
                student_obj = (
                    CustomUser.objects.get(user__username=student)
                    if CustomUser.objects.filter(user__username=student).exists()
                    else None
                )
                # if not student_obj:
                #     return JsonResponse({'message': f'Student {student} does not exist'})
                classroom.students.remove(student_obj)
            classroom.save()

        response = {
            "id": classroom.id,
            "name": classroom.name,
            "created_by": classroom.created_by.user.username,
            "created_at": classroom.created_at,
            "files": [file.file.name for file in classroom.files.all()],
            "students": [student.user.username for student in classroom.students.all()],
        }
        return JsonResponse(
            {"class": response},
        )
        return JsonResponse({"message": "Classroom updated successfully"})

    def delete(self, request):
        class_id = request.POST.get("class_id")
        role = request.user.custom_user.role
        if role == "student":
            return JsonResponse({"message": "You are not allowed to create a class"})

        classroom = get_object_or_404(Classroom, id=class_id)
        classroom.delete()
        return JsonResponse({"message": "Classroom deleted successfully"})


class FeedView(APIView):
    def get(self, request):
        query = request.GET.get("query") if request.GET.get("query") else None
        if not query:
            return JsonResponse({"message": "Query not provided"})
        user = request.user.custom_user
        role = user.role

        user_classes = user.owner.all() if role == "teacher" else user.student.all()

        response = []
        for classroom in user_classes:
            if (
                query in classroom.name
                or query in classroom.created_by.user.username
                or classroom.files.filter(name__icontains=query).exists()
            ):
                response.append(
                    {
                        "id": classroom.id,
                        "name": classroom.name,
                        "created_by": classroom.created_by.user.username,
                        "created_at": classroom.created_at,
                        "files": [file.file.name for file in classroom.files.all()],
                        "students": [
                            student.user.username
                            for student in classroom.students.all()
                        ],
                    }
                )

        return JsonResponse(
            {"classes": response},
        )
