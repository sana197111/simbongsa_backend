# urls.py
"""
URL configuration for simvolunteer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Volunteer import views

urlpatterns = [
    path('admin', admin.site.urls),
    # path('login', views.login_view, name='login'),  # 로그인 뷰 함수 지정
    path('login', views.MyTokenObtainPairView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),  # 로그아웃 뷰 함수 지정
    path('signup', views.signup, name='signup'),  # 회원가입 뷰 함수 지정
    path('volunteerlist', views.volunteer_list, name='volunteerlist'),  # 봉사 목록 뷰 함수 지정 
    path('volunteerlist/<str:mbti_type>', views.volunteer_list_mbti, name='volunteerlist_mbti'),  # 봉사 목록 뷰 함수 지정 
    path('volunteer/<int:event_id>', views.event_detail, name='event_detail'),  # 이벤트 상세 뷰 함수 지정
    path('api/users', views.user_list, name='user_list'),  # 사용자 목록 API
    path('api/current-user', views.current_user, name='current_user'), # 현재 사용자 정보 API
    path('api/mypage/', views.my_page, name='mypage'),  # 마이 페이지 뷰 함수 지정
    path('api/verify-business-number', views.verify_business_number, name='verify_business_number'),
    path('mypage/org/', views.my_page_org, name='mypage_org'),  # 마이 페이지_기업 뷰 함수 지정
    path('event/<int:event_id>/apply', views.apply_for_event, name='apply_for_event'),  # 이벤트 신청 뷰
    path('application/<int:participation_id>', views.accept_or_reject_application, name='accept_or_reject_application'),  # 신청 수락/거절 뷰
    path('api/upload_event', views.upload_event , name='upload_event'),
    path('display-csrf-token', views.display_csrf_token, name='display_csrf_token'),
]