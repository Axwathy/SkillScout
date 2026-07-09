---
type: deployment
title: "Vercel Deployment"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, deployment]
---

# Vercel Deployment

This document covers the deployment of the **Next.js frontend** on Vercel, including configuration, environment management, preview deployments, and performance optimization.

See also: [[frontend-architecture|Frontend Architecture]], [[deployment-architecture|Deployment Architecture]]

---

## Why Vercel

| Factor             | Benefit                                              |
|--------------------|------------------------------------------------------|
| Next.js native     | Built by the Next.js team — optimal integration      |
| Edge Network       | Global CDN with edge functions for low latency       |
| Preview Deploys    | Automatic preview URL for every PR                   |
| Zero Config        | Detects Next.js automatically, no build config needed |
| Analytics          | Built-in Web Vitals and speed insights               |

---

## Project Configuration

### `vercel.json`

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm ci",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/api/v1/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, must-revalidate" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "https://api.example.com/api/v1/:path*"
    }
  ]
}
```

### Key Configuration Notes

- **`rewrites`**: Proxies API requests from the frontend domain to the Django backend, avoiding CORS issues in production.
- **`regions`**: Deploy to `iad1` (US East) for lowest latency to the Railway-hosted backend. Add additional regions as needed.
- **`headers`**: Security headers applied globally; API routes explicitly disable caching.

---

## Environment Variables

Environment variables are configured per-environment in the Vercel dashboard.

| Variable                        | Preview   | Staging   | Production |
|---------------------------------|-----------|-----------|------------|
| `NEXT_PUBLIC_API_URL`           | PR backend URL | `https://staging-api.example.com` | `https://api.example.com` |
| `NEXT_PUBLIC_APP_ENV`           | `preview` | `staging` | `production` |

> **Important:** Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Never put secrets in `NEXT_PUBLIC_` variables.

---

## Preview Deployments

Every pull request automatically receives a **unique preview deployment URL**:

- Format: `https://project-<hash>-team.vercel.app`
- The Vercel bot comments on the PR with the preview link
- Preview deployments use the **Preview** environment variables
- Useful for design review, QA testing, and stakeholder demos

### Preview Environment Behavior

- Connected to the **staging backend** by default
- Each preview has its own isolated build
- Automatically deleted when the PR is closed or merged
- Can be pinned for longer-lived testing if needed

---

## Custom Domain Setup

### Production Domain

1. Add `app.example.com` in Vercel dashboard → Domains
2. Configure DNS:
   - **CNAME**: `app.example.com` → `cname.vercel-dns.com`
   - Or **A record**: `76.76.21.21`
3. SSL certificate is automatically provisioned via Let's Encrypt
4. Enable "Redirect to Primary Domain" to canonicalize URLs

### Staging Domain

1. Add `staging.example.com` and assign to the `develop` branch
2. Same DNS setup as production

---

## ISR / SSG Configuration

### Static Generation (SSG)

Pages that can be fully pre-rendered at build time:

- `/` — Landing page
- `/pricing` — Pricing page
- `/docs/*` — Documentation pages

### Incremental Static Regeneration (ISR)

Pages that benefit from caching with periodic revalidation:

```typescript
// Example: Job listing page with 60-second revalidation
export async function generateStaticParams() {
  const jobs = await fetchPublicJobs();
  return jobs.map((job) => ({ slug: job.slug }));
}

export const revalidate = 60; // Revalidate every 60 seconds
```

| Page Type          | Strategy  | Revalidate | Notes                           |
|--------------------|-----------|------------|---------------------------------|
| Landing page       | SSG       | Build-time | Fully static                    |
| Job listing (public) | ISR     | 60s        | Near-real-time, cacheable       |
| Job detail (public)  | ISR     | 60s        | Per-job page, on-demand         |
| Dashboard pages    | CSR/SSR   | —          | Authenticated, real-time data   |
| Admin pages        | CSR       | —          | Fully client-side rendered      |

---

## Edge Functions

Edge functions are used sparingly for latency-sensitive middleware:

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Redirect unauthenticated users from dashboard routes
  const token = request.cookies.get("session_token");
  if (request.nextUrl.pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
```

---

## Build Optimization

| Optimization               | Implementation                          |
|-----------------------------|-----------------------------------------|
| Image optimization          | `next/image` with Vercel Image CDN     |
| Bundle analysis             | `@next/bundle-analyzer` in CI          |
| Tree shaking                | Ensure ESM imports for all libraries   |
| Font optimization           | `next/font` with `Inter` and `Outfit` |
| Dependency caching          | Vercel auto-caches `node_modules`      |

---

## Monitoring

- **Vercel Analytics**: Core Web Vitals (LCP, FID, CLS) tracked per deployment
- **Vercel Speed Insights**: Real user monitoring with percentile breakdowns
- **Build Logs**: Available in Vercel dashboard per deployment
- **Error Tracking**: Integrated with Sentry via `@sentry/nextjs`
