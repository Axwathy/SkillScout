from django.db.models import Q
from rest_framework import generics, status, views
from rest_framework.response import Response

from apps.accounts.permissions import IsVerifiedRecruiter
from apps.candidates.models import Application
from apps.candidates.views import get_recruiter_organization

from .models import InterviewQuestion, InterviewQuestionNote, QuestionBankItem
from .serializers import (
    InterviewQuestionNoteCreateSerializer,
    InterviewQuestionNoteSerializer,
    InterviewQuestionSerializer,
    InterviewQuestionSetSerializer,
    InterviewQuestionUpdateSerializer,
    QuestionBankItemSerializer,
)
from .services import generate_interview_question_set, latest_interview_question_set


def _get_application_or_404(request, application_id):
    organization = get_recruiter_organization(request)
    return generics.get_object_or_404(
        Application.objects.select_related("candidate", "job", "organization").filter(
            organization=organization,
        ),
        pk=application_id,
    )


class ApplicationInterviewQuestionSetView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, application_id, *args, **kwargs):
        application = _get_application_or_404(request, application_id)
        question_set = latest_interview_question_set(application)
        if question_set is None:
            return Response({"question_set": None})
        return Response({"question_set": InterviewQuestionSetSerializer(question_set).data})


class GenerateInterviewQuestionSetView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def post(self, request, application_id, *args, **kwargs):
        application = _get_application_or_404(request, application_id)
        force = str(request.query_params.get("force", "")).lower() in {"1", "true", "yes"}
        question_set = generate_interview_question_set(
            application,
            user=request.user,
            force=force,
        )
        question_set = latest_interview_question_set(application) or question_set
        return Response(
            {"question_set": InterviewQuestionSetSerializer(question_set).data},
            status=status.HTTP_201_CREATED,
        )


class InterviewQuestionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsVerifiedRecruiter]

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return InterviewQuestionUpdateSerializer
        return InterviewQuestionSerializer

    def get_queryset(self):
        organization = get_recruiter_organization(self.request)
        return InterviewQuestion.objects.filter(
            question_set__organization=organization,
        ).prefetch_related("notes")


class InterviewQuestionNoteCreateView(generics.CreateAPIView):
    serializer_class = InterviewQuestionNoteCreateSerializer
    permission_classes = [IsVerifiedRecruiter]

    def get_question(self):
        organization = get_recruiter_organization(self.request)
        return generics.get_object_or_404(
            InterviewQuestion.objects.filter(question_set__organization=organization),
            pk=self.kwargs["question_id"],
        )

    def create(self, request, *args, **kwargs):
        question = self.get_question()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = InterviewQuestionNote.objects.create(
            question=question,
            author=request.user,
            body=serializer.validated_data["body"],
        )
        return Response(
            InterviewQuestionNoteSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )


class QuestionBankListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionBankItemSerializer
    permission_classes = [IsVerifiedRecruiter]

    def get_queryset(self):
        organization = get_recruiter_organization(self.request)
        queryset = QuestionBankItem.objects.filter(
            Q(organization=organization) | Q(organization__isnull=True),
            is_active=True,
        )
        category = self.request.query_params.get("category", "").strip()
        role_family = self.request.query_params.get("role_family", "").strip()
        search = self.request.query_params.get("search", "").strip()
        if category:
            queryset = queryset.filter(category=category)
        if role_family:
            queryset = queryset.filter(role_family=role_family)
        if search:
            queryset = queryset.filter(
                Q(question_text__icontains=search)
                | Q(evaluation_criteria__icontains=search)
            )
        return queryset.order_by("role_family", "category", "created_at")

    def perform_create(self, serializer):
        organization = get_recruiter_organization(self.request)
        serializer.save(organization=organization)
