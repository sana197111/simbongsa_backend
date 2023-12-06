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
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, VolunteerEvent, Participation, Organization
from django.contrib.auth import get_user_model

def display_csrf_token(request):
    return render(request, 'csrf_token_display.html')

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 사용자 정의 클레임 추가
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         username = data.get('username')
#         password = data.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)

#             # JWT 토큰 생성
#             refresh = RefreshToken.for_user(user)
#             return JsonResponse({
#                 'message': '로그인 성공',
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=200)
#         else:
#             return JsonResponse({'error': 'Invalid credentials'}, status=400)

#     return JsonResponse({'error': 'Invalid request'}, status=400)
    
@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'message': '로그아웃 성공'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')
        contact = data.get('contact')

        # 중복된 사용자 이름이 있는지 확인
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '이미 존재하는 사용자 이름입니다.'}, status=400)

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = name  # 'first_name' 필드에 이름을 저장
            user.contact = contact  # 추가된 'contact' 필드에 전화번호 저장
            user.save()

            return JsonResponse({'message': '회원가입 성공'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer, VolunteerEventSerializer, ParticipationSerializer
from datetime import datetime

@api_view(['GET'])
def current_user(request):
    """
    현재 로그인한 사용자의 정보를 반환합니다.
    """
    if request.method == 'GET':
        # 로그인한 사용자인지 확인
        if not request.user.is_authenticated:
            return Response({'error': '로그인 필요'}, status=status.HTTP_401_UNAUTHORIZED)

        User = get_user_model()
        # request.user가 실제 User 모델의 인스턴스인지 확인
        if isinstance(request.user, User):
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response({'error': '유효하지 않은 사용자'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_business_number(request):
    business_number = request.data.get('businessNumber')
    user = request.user

    if not request.user.is_authenticated:
        return Response({'error': '로그인 필요'}, status=status.HTTP_401_UNAUTHORIZED)

    # 사용자가 속한 조직(회사)을 가져옵니다.
    organization = user.company

    if organization:
        # 조직의 사업자 등록번호가 일치하는지 확인
        if organization.company_number == business_number:
            return Response({'message': '인증 성공'})
        else:
            return Response({'error': '인증 실패'}, status=400)
    else:
        # 조직이 없는 경우, 새로운 조직을 생성하고 사용자에게 할당
        new_organization = Organization.objects.create(name="New Company", company_number=business_number)
        user.company = new_organization
        user.save()
        return Response({'message': '새로운 조직 생성 및 인증 성공'}, status=201)

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

# @api_view(['POST'])
# def become_superuser(request):
#     if request.method == 'POST':
#         data = request.data
#         user = request.user
#         name = data.get('company_name')
#         company_id = data.get('company_number')

#         # 사업자 등록증 겹치는지 확인하기
#         try:
#             company = Organization.objects.get(company_id=company_id)
#             return Response({'error': '이미 존재하는 회사 번호입니다.'}, status=status.HTTP_400_BAD_REQUEST)
#         except Organization.DoesNotExist:
#             company = Organization.objects.create(company_id=company_id, name=name)
#             user.company = company
#             user.is_superuser = True            
#             user.save()

#         return Response({'message': 'Superuser로 업그레이드 및 회사 정보 업데이트 성공'}, status=status.HTTP_200_OK)

#     return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_event(request):
    if request.method == 'POST':
        data = request.data.copy()

        # Serializer를 사용하여 데이터 유효성 검사
        serializer = VolunteerEventSerializer(data=data)
        if serializer.is_valid():
            # 유효성 검사가 통과하면 모델 인스턴스 생성
            event = VolunteerEvent.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                location=data.get('location'),
                mbti_type=data.get('mbti_type'),
                vol_start=data.get('vol_start'),
                vol_end=data.get('vol_end'),
                apply_start=data.get('apply_start'),
                apply_end=data.get('apply_end'),
                user_id =request.user  # 현재 로그인한 사용자 객체를 할당
            )

            # 성공 응답 반환
            return Response({'message': '이벤트 업로드 성공'}, status=status.HTTP_201_CREATED)
        else:
            # 오류 응답 반환
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def volunteer_list_mbti(request,mbti_type):
        if request.method == 'GET':
            events = VolunteerEvent.objects.filter(mbti_type=mbti_type)
            serializer = VolunteerEventSerializer(events, many=True)
            return Response(serializer.data)
        return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def volunteer_list(request):
    if request.method == 'GET':
        events = VolunteerEvent.objects.all()
        print(events)
        serializer = VolunteerEventSerializer(events, many=True)
        return Response(serializer.data)
    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def my_page(request):
    if request.method == 'GET':
        # user_id가 주어진 사용자의 참가신청 목록을 가져옵니다.
        user_id = request.user.user_id
        participations = Participation.objects.filter(user_id=user_id)

        # 오늘 날짜를 기준으로 vol_end가 지난 것과 아닌 것을 나눕니다. volunteerserializer을 불러옴
        today = datetime.today()
        # Fetching event IDs for past and upcoming events
        past_events_ids = participations.filter(event_id__vol_end__lt=today).values_list('event_id', flat=True)
        upcoming_events_ids = participations.filter(event_id__vol_end__gte=today).values_list('event_id', flat=True)

        # Fetching events based on IDs
        past_events = VolunteerEvent.objects.filter(event_id__in=past_events_ids)
        upcoming_events = VolunteerEvent.objects.filter(event_id__in=upcoming_events_ids)

        # Serialize the data
        past_events_serializer = VolunteerEventSerializer(past_events, many=True)
        upcoming_events_serializer = VolunteerEventSerializer(upcoming_events, many=True)

        # serialize된 데이터를 반환합니다.
        return Response({
            'past_events': past_events_serializer.data,
            'upcoming_events': upcoming_events_serializer.data,
        })

    # GET 요청이 아닌 경우의 처리
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


@api_view(['POST'])
def apply_for_event(request, event_id):
    if request.method == 'POST':
        print(request.user)
        if not request.user.is_authenticated:
            return Response({'error': '로그인 필요'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.user.user_id

        # 이미 신청한 이벤트인지 확인
        existing_participation = Participation.objects.filter(user_id=user_id, event_id=event_id)
        if existing_participation.exists():
            return Response({'message': '이미 신청됨'}, status=status.HTTP_208_ALREADY_REPORTED)

        # 이미 신청하지 않은 경우, 새로운 레코드 생성
        serializer = ParticipationSerializer(data={'user_id': user_id, 'event_id': event_id, 'apply_date': datetime.now()})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '신청 완료'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def my_page_org(request):
    if request.method == 'GET':
        user_id = request.user.user_id
        user = User.objects.get(user_id=user_id)
        company_number = user.company.company_number
        print(user_id, user, company_number)
        if company_number is not None:
            events = VolunteerEvent.objects.filter(user_id__company__company_number=company_number)
            # print(VolunteerEvent.objects.filter())
            serializer = VolunteerEventSerializer(events, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    # GET 요청이 아닌 경우의 처리
    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def accept_or_reject_application(request, participation_id):
    if request.method == 'PUT':
        participation = Participation.objects.get(pk=participation_id)
        decision = request.data.get('decision')

        if decision == 'accept':
            serializer = ParticipationSerializer(participation, data={'status': "Accepted"}, partial=True)
        elif decision == 'reject':
            serializer = ParticipationSerializer(participation, data={'status': "Rejected"}, partial=True)
        else:
            return Response({'error': 'Decision must be either "accept" or "reject"'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': '잘못된 요청'}, status=status.HTTP_400_BAD_REQUEST)


def leave_feedback(request):
    pass