import { describe, expect, it } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "@/routeTree.gen";
import { analyzePassword } from "@/components/auth/password-strength";

describe("Password Strength Analyzer", () => {
  it("evaluates short and weak passwords correctly", () => {
    const weak = analyzePassword("abc");
    expect(weak.score).toBe(1);
    expect(weak.hasMinLength).toBe(false);
    expect(weak.hasUpper).toBe(false);
    expect(weak.hasLower).toBe(true);
    expect(weak.hasNumberOrSymbol).toBe(false);
  });

  it("evaluates passwords with length and upper/lowercase", () => {
    const fair = analyzePassword("Abcdefgh");
    expect(fair.hasMinLength).toBe(true);
    expect(fair.hasUpper).toBe(true);
    expect(fair.hasLower).toBe(true);
    expect(fair.hasNumberOrSymbol).toBe(false);
    expect(fair.score).toBe(3);
  });

  it("identifies formidable passwords with symbols and digits", () => {
    const strong = analyzePassword("CyberDefense#2026!");
    expect(strong.score).toBe(4);
    expect(strong.hasMinLength).toBe(true);
    expect(strong.hasUpper).toBe(true);
    expect(strong.hasLower).toBe(true);
    expect(strong.hasNumberOrSymbol).toBe(true);
    expect(strong.label).toBe("Strong");
  });
});

describe("Authentication Routes Tree", () => {
  const router = createRouter({
    routeTree,
    context: { queryClient: new QueryClient() },
  });

  it("matches /login route successfully", () => {
    const matches = router.matchRoutes("/login");
    expect(matches.at(-1)?.routeId).toBe("/login");
  });

  it("matches /register route successfully", () => {
    const matches = router.matchRoutes("/register");
    expect(matches.at(-1)?.routeId).toBe("/register");
  });

  it("matches /forgot-password route successfully", () => {
    const matches = router.matchRoutes("/forgot-password");
    expect(matches.at(-1)?.routeId).toBe("/forgot-password");
  });

  it("matches /reset-password route successfully", () => {
    const matches = router.matchRoutes("/reset-password");
    expect(matches.at(-1)?.routeId).toBe("/reset-password");
  });

  it("matches /verify-email route successfully", () => {
    const matches = router.matchRoutes("/verify-email");
    expect(matches.at(-1)?.routeId).toBe("/verify-email");
  });

  it("matches /auth/google/callback route successfully", () => {
    const matches = router.matchRoutes("/auth/google/callback");
    expect(matches.at(-1)?.routeId).toBe("/auth/google/callback");
  });
});
