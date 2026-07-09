---
type: architecture
title: "Frontend Architecture"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, frontend/nextjs, frontend/react]
---

# Frontend Architecture

## Overview

The frontend is a **Next.js 14+** application using the **App Router**, **TypeScript**, and **TailwindCSS**. It follows a server-first rendering strategy with selective client-side interactivity for dynamic components like the pipeline board and analytics dashboard. The app communicates with the Django backend via a typed API client layer with automatic token refresh.

---

## Next.js App Router Structure

```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout (providers, global styles)
│   ├── page.tsx                      # Landing / marketing page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── forgot-password/page.tsx
│   │   └── reset-password/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx                # Dashboard shell (sidebar, topbar)
│   │   ├── page.tsx                  # Dashboard overview
│   │   ├── jobs/
│   │   │   ├── page.tsx              # Jobs list
│   │   │   ├── [id]/page.tsx         # Job detail
│   │   │   └── new/page.tsx          # Create job
│   │   ├── candidates/
│   │   │   ├── page.tsx              # Candidates list
│   │   │   └── [id]/page.tsx         # Candidate detail + AI insights
│   │   ├── pipeline/
│   │   │   └── page.tsx              # Kanban board
│   │   ├── analytics/
│   │   │   └── page.tsx              # Analytics dashboard
│   │   └── settings/
│   │       ├── page.tsx              # Organization settings
│   │       ├── team/page.tsx         # Team management
│   │       └── billing/page.tsx      # Billing management
│   └── api/                          # Next.js API routes (BFF pattern, optional)
│
├── components/
│   ├── ui/                           # Design system primitives
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Table.tsx
│   │   ├── Dropdown.tsx
│   │   └── Skeleton.tsx
│   ├── layout/                       # Structural components
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   └── PageHeader.tsx
│   ├── jobs/                         # Job-specific components
│   │   ├── JobCard.tsx
│   │   ├── JobForm.tsx
│   │   └── JobFilters.tsx
│   ├── candidates/                   # Candidate-specific components
│   │   ├── CandidateCard.tsx
│   │   ├── CandidateScoreCard.tsx
│   │   ├── ResumeUploader.tsx
│   │   └── AIInsightsPanel.tsx
│   ├── pipeline/                     # Pipeline components
│   │   ├── KanbanBoard.tsx
│   │   ├── KanbanColumn.tsx
│   │   └── KanbanCard.tsx
│   └── analytics/                    # Analytics components
│       ├── MetricCard.tsx
│       ├── HiringFunnel.tsx
│       └── TimeToHireChart.tsx
│
├── lib/
│   ├── api/                          # API client layer
│   │   ├── client.ts                 # Axios instance with interceptors
│   │   ├── auth.ts                   # Auth API functions
│   │   ├── jobs.ts                   # Jobs API functions
│   │   ├── candidates.ts             # Candidates API functions
│   │   └── pipeline.ts              # Pipeline API functions
│   ├── hooks/                        # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useJobs.ts
│   │   ├── useCandidates.ts
│   │   └── usePipeline.ts
│   ├── types/                        # TypeScript type definitions
│   │   ├── auth.ts
│   │   ├── job.ts
│   │   ├── candidate.ts
│   │   └── pipeline.ts
│   └── utils/                        # Utility functions
│       ├── formatters.ts
│       ├── validators.ts
│       └── constants.ts
│
├── styles/
│   └── globals.css                   # TailwindCSS imports + custom styles
├── public/                           # Static assets
├── middleware.ts                      # Auth middleware (route protection)
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Component Hierarchy

```
RootLayout
├── AuthProvider (context)
├── ThemeProvider
└── QueryClientProvider (React Query)
    ├── (auth)
    │   ├── LoginPage
    │   └── RegisterPage
    └── (dashboard)
        └── DashboardLayout
            ├── Sidebar
            ├── Topbar (user menu, notifications)
            └── PageContent
                ├── JobsPage → JobCard[]
                ├── CandidatesPage → CandidateCard[] + AIInsightsPanel
                ├── PipelinePage → KanbanBoard → KanbanColumn[] → KanbanCard[]
                └── AnalyticsPage → MetricCard[] + Charts
```

### Component Guidelines

- **Server Components** (default) — Used for data fetching, layout, and static content. No `useState`, `useEffect`, or event handlers.
- **Client Components** (`"use client"`) — Used for interactive elements: forms, modals, drag-and-drop, real-time updates.
- **Composition** — Server components fetch data and pass it as props to client components for interactivity.

---

## State Management Approach

| Concern | Solution | Rationale |
|---------|----------|-----------|
| **Server State** | React Query (TanStack Query) | Caching, background refetching, optimistic updates |
| **Auth State** | React Context + cookies | Lightweight, synced with HttpOnly JWT cookies |
| **UI State** | Local `useState` / `useReducer` | Component-scoped, no global store needed |
| **Form State** | React Hook Form + Zod | Performant forms with schema validation |
| **Drag & Drop** | `@dnd-kit/core` | Pipeline board Kanban interactions |

### React Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      gcTime: 10 * 60 * 1000,         // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

---

## API Client Layer

The API client is a centralized Axios instance with automatic token refresh:

```typescript
// API client module
const apiBaseUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1`;

const apiClient = axios.create({
  baseURL: apiBaseUrl,
  withCredentials: true,   // Send cookies automatically
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      await apiClient.post('/auth/refresh/');
      return apiClient(error.config);
    }
    return Promise.reject(error);
  }
);
```

Each API module exports typed functions:

```typescript
// lib/api/v1/candidates.ts
export const candidatesApi = {
  list: (jobId: string, params?: ListParams) =>
    apiClient.get<PaginatedResponse<Candidate>>(`/candidates/`, { params: { job: jobId, ...params } }),
  get: (id: string) =>
    apiClient.get<Candidate>(`/candidates/${id}/`),
  create: (data: CreateCandidateInput) =>
    apiClient.post<Candidate>('/candidates/', data),
};
```

---

## Authentication Flow (Client-Side)

1. **Middleware** (`middleware.ts`) — Runs on every request. Checks for `access_token` cookie. Redirects unauthenticated users to `/login` for protected routes.
2. **AuthProvider** — React context that holds the current user profile. Fetches `/api/v1/auth/me/` on mount.
3. **Login** — Calls `/api/v1/auth/login/`, cookies are set by the server. AuthProvider re-fetches user profile.
4. **Logout** — Calls `/api/v1/auth/logout/`, cookies are cleared. User redirected to `/login`.

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const isAuthPage = request.nextUrl.pathname.startsWith('/login')
    || request.nextUrl.pathname.startsWith('/register');

  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
}
```

---

## Routing Strategy

| Route Pattern | Access | Rendering |
|---------------|--------|-----------|
| `/` | Public | SSG (static) |
| `/login`, `/register` | Public (redirect if auth'd) | Client |
| `/dashboard` | Protected | SSR + Client |
| `/jobs`, `/jobs/[id]` | Protected | SSR |
| `/candidates/[id]` | Protected | SSR + Client (AI panel) |
| `/pipeline` | Protected | Client (drag-and-drop) |
| `/analytics` | Protected | SSR + Client (charts) |
| `/settings/*` | Protected (Admin only) | SSR |

---

## Related Documents

- [[candidate-dashboard|Candidate Dashboard]] — Candidate detail page design and AI insights display.
- [[pipeline-board|Pipeline Board]] — Kanban board implementation with drag-and-drop.
- [[analytics-dashboard|Analytics Dashboard]] — Charts, metrics, and reporting components.
- [[system-overview|System Overview]] — High-level platform architecture.
- [[authentication-flow|Authentication Flow]] — Backend JWT strategy and cookie configuration.
