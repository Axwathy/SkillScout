import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const RECRUITER_PROTECTED = ["/dashboard"];
const CANDIDATE_PROTECTED = ["/candidate/dashboard", "/candidate/applications", "/candidate/profile"];
const RECRUITER_AUTH_ROUTES = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip Next.js internals and static assets
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/static") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  const hasAccessCookie = request.cookies.has("access");

  // ── Auth routes (login/register) ────────────────────────────────
  // If already authenticated, redirect users away from auth pages
  if (hasAccessCookie && RECRUITER_AUTH_ROUTES.some((r) => pathname.startsWith(r))) {
    // If the user tries to access /login, we should ideally know their role, but middleware doesn't know it.
    // Defaulting to /dashboard. If they are a candidate, the frontend will redirect them properly
    // or they'll get a 403 on dashboard and handle it. Alternatively, they'll land on /dashboard and NextJS will render it.
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Protect candidate portal routes
  if (!hasAccessCookie && CANDIDATE_PROTECTED.some((r) => pathname.startsWith(r))) {
    const url = new URL("/login", request.url);
    url.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(url);
  }

  // Protect recruiter dashboard routes
  if (!hasAccessCookie && RECRUITER_PROTECTED.some((r) => pathname.startsWith(r))) {
    const url = new URL("/login", request.url);
    url.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
