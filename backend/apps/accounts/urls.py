from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.CsrfTokenView.as_view(), name="auth-csrf"),
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("refresh/", views.RefreshView.as_view(), name="auth-refresh"),
    path("me/", views.MeView.as_view(), name="auth-me"),
    path("admin/recruiters/", views.AdminRecruiterListView.as_view(), name="admin-recruiters-list"),
    path(
        "admin/recruiters/<uuid:pk>/approve/",
        views.AdminRecruiterApproveView.as_view(),
        name="admin-recruiter-approve",
    ),
    path(
        "admin/recruiters/<uuid:pk>/reject/",
        views.AdminRecruiterRejectView.as_view(),
        name="admin-recruiter-reject",
    ),
    path(
        "admin/organizations/",
        views.AdminOrganizationListView.as_view(),
        name="admin-organizations-list",
    ),
    path(
        "admin/organizations/<uuid:pk>/approve/",
        views.AdminOrganizationApproveView.as_view(),
        name="admin-organization-approve",
    ),
    path(
        "admin/organizations/<uuid:pk>/reject/",
        views.AdminOrganizationRejectView.as_view(),
        name="admin-organization-reject",
    ),
]
