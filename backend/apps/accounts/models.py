import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RECRUITER = "recruiter", "Recruiter"
        HIRING_MANAGER = "hiring_manager", "Hiring Manager"
        INTERVIEWER = "interviewer", "Interviewer"
        CANDIDATE = "candidate", "Candidate"  # Reserved for Sprint 3+

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.RECRUITER)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_recruiter(self) -> bool:
        return self.role == self.Role.RECRUITER


class Recruiter(models.Model):
    """
    Recruiter profile — extends User for users with the recruiter role.
    Sprint 2: real Organization FK, verification workflow, full profile fields.
    See: raw/architecture/recruiter-verification-workflow.md
    """

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="recruiter_profile",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="recruiters",
        null=True,  # null during atomic creation; set immediately after org is created
        blank=True,
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Job title, e.g. 'Senior Recruiter'",
    )
    linkedin_profile = models.URLField(
        max_length=255,
        blank=True,
        help_text="LinkedIn profile URL. Required if company website is missing.",
    )
    verification_status = models.CharField(
        max_length=16,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Denormalized flag — True when verification_status == approved.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__email"]

    def __str__(self) -> str:
        return f"Recruiter({self.user.email})"

    @property
    def full_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.user.full_name

    @property
    def is_approved(self) -> bool:
        return self.verification_status == self.VerificationStatus.APPROVED

    def approve(self) -> None:
        """Approve this recruiter profile. Also syncs is_verified."""
        self.verification_status = self.VerificationStatus.APPROVED
        self.is_verified = True
        self.save(update_fields=["verification_status", "is_verified", "updated_at"])

    def reject(self) -> None:
        self.verification_status = self.VerificationStatus.REJECTED
        self.is_verified = False
        self.save(update_fields=["verification_status", "is_verified", "updated_at"])

    def suspend(self) -> None:
        self.verification_status = self.VerificationStatus.SUSPENDED
        self.is_verified = False
        self.save(update_fields=["verification_status", "is_verified", "updated_at"])
