# views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, VolunteerEvent, Participation

def display_csrf_token(request):
    return render(request, 'csrf_token_display.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({'message': '로그인 성공'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'message': '로그아웃 성공'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
def signup(request):
    if request.method == 'POST':
        # JSON 데이터로 요청된 경우 처리
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        # 전화번호 입력란 추가
        contact = data.get('contact')

        # 사용자 생성
        try:
            user = User.objects.create_user(username, email, password, contact)
            # 추가적인 사용자 데이터 설정 (예: 프로필 정보 등)
            user.save()

            # 성공 응답 반환
            return JsonResponse({'message': '회원가입 성공'}, status=201)
        except Exception as e:
            # 오류 응답 반환
            return JsonResponse({'error': str(e)}, status=400)

    # POST 요청이 아닌 경우의 처리
    return JsonResponse({'error': 'Invalid request'}, status=400)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer, VolunteerEventSerializer

@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def become_superuser(request):
    if request.method == 'POST':
        organization_id = request.POST.get('organization_id')
        user = request.user

        # Check if the organization_id is correct (you might want to implement additional validation)
        if organization_id == user.organization_id:
            # Set the user as superuser
            user.is_superuser = True
            user.save()

            # Redirect to a success page or any other page you desire
            messages.success(request, 'You are now a superuser!')
            return redirect('mypage')  

    return render(request, 'become_superuser.html')  

@api_view(['POST'])
def upload_event(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['user_id'] = request.user.id

        serializer = VolunteerEventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # 성공 응답 반환
            return Response({'message': '이벤트 업로드 성공'}, status=status.HTTP_201_CREATED)
        else:
            # 오류 응답 반환
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # POST 요청이 아닌 경우의 처리
    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get', 'PUT', 'DELETE'])
def event_detail(request, event_id):
    try:
        event = VolunteerEvent.objects.get(pk=event_id)
    except VolunteerEvent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Read 불러오기
    if request.method == 'GET':
        serializer = VolunteerEventSerializer(event)
        return Response(serializer.data)
    
    # Update 수정하기
    elif request.method == 'PUT':
        serializer = VolunteerEventSerializer(event, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete 삭제하기
    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




def apply_for_event(request, event_id):
    if request.method == 'POST':
        user_id = request.user.id
        event = get_object_or_404(VolunteerEvent, pk=event_id)

        # 이미 신청한 이벤트인지 확인
        existing_participation = Participation.objects.filter(user_id=user_id, event_id=event)
        if existing_participation.exists():
            return HttpResponse("You have already applied for this event.")

        # 새로운 참여 레코드 생성 (기본적으로 'Pending' 상태)
        participation = Participation(user_id=request.user, event_id=event, attendance=False)
        participation.save()

        return redirect('event_detail', event_id=event_id)

    return HttpResponse("Invalid request method.")

def accept_or_reject_application(request, participation_id, decision):
    if request.method == 'POST' and request.user.is_superuser:
        participation = get_object_or_404(Participation, pk=participation_id)
        event_id = participation.event_id.id

        if decision == 'accept':
            participation.status = 'Accepted'
            participation.save()
        elif decision == 'reject':
            participation.status = 'Rejected'
            participation.save()

        return redirect('event_detail', event_id=event_id)

    return HttpResponse("Invalid request or permission denied.")

def leave_feedback(request):
    pass