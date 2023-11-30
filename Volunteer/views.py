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
from .models import User, VolunteerEvent, Participation, Feedback\

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
        # 추가적인 데이터 처리 (예: 전화번호 등)

        # 사용자 생성
        try:
            user = User.objects.create_user(username, email, password)
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
from .serializers import UserSerializer

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
            # (여기 수정해야함) Change 'home' to your desired URL

    return render(request, 'become_superuser.html')  
    # (템플릿 만들어야 함!) Create a template for this view


def upload_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        vol_start = request.POST.get('vol_start')
        vol_end = request.POST.get('vol_end')
        user_id = request.user.id # 이 부분은 로그인한 사용자의 organization_id로 수정해야 할 수도 있습니다.
        location = request.POST.get('location')
        apply_start = request.POST.get('apply_start')
        apply_end = request.POST.get('apply_end')
        event = VolunteerEvent(title=title, description=description, vol_start=vol_start, vol_end=vol_end, location=location, apply_start=apply_start, apply_end=apply_end, user_id=user_id)
        event.save()

        # 업로드 후 리다이렉트할 페이지 설정
        return redirect('event_list')  # event_list는 예시

    return render(request, 'upload_event.html')


def event_detail(request, event_id):
    # 해당 이벤트의 상세 정보, 참여자, 피드백을 가져옴
    event = get_object_or_404(VolunteerEvent, pk=event_id)
    participations = Participation.objects.filter(event_id=event)
    feedbacks = Feedback.objects.filter(event_id=event)

    # event_detail.html 템플릿에 전달할 데이터를 정리
    context = {'event': event, 'participations': participations, 'feedbacks': feedbacks}
    
    # 이벤트 상세 페이지 렌더링
    return render(request, 'event_detail.html', context)

    # 신청하기 눌렀을 때 (apply)



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

def leave_feedback(request, event_id, participation_id):
    if request.method == 'POST':
        user_id = request.user.id
        event = get_object_or_404(VolunteerEvent, pk=event_id)

        # 참여한 이벤트인지 확인
        participation = get_object_or_404(Participation, pk=participation_id, user_id=user_id, event_id=event)

        comment = request.POST.get('comment')
        rating = request.POST.get('rating')

        feedback = Feedback(comment=comment, rating=rating, participation_id=participation, event_id=event)
        feedback.save()

        return redirect('event_detail', event_id=event_id)

    return HttpResponse("Invalid request method.")