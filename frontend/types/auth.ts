export type Role = "admin" | "recruiter" | "hiring_manager" | "interviewer" | "candidate";

export type ApprovalStatus = "pending" | "approved" | "rejected" | "suspended";
export type VerificationStatus = "pending" | "approved" | "rejected" | "suspended";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  website: string;
  approval_status: ApprovalStatus;
  is_active: boolean;
  created_at: string;
}

export interface RecruiterProfile {
  id: string;
  first_name: string;
  last_name: string;
  title: string;
  organization: Organization | null;
  verification_status: VerificationStatus;
  is_verified: boolean;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_email_verified: boolean;
  is_active: boolean;
  recruiter_profile: RecruiterProfile | null;
  date_joined: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface ApiError {
  detail?: string;
  code?: string;
  [key: string]: any;
}
