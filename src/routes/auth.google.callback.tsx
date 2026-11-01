import { useEffect, useState } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/auth/google/callback")({
  component: GoogleCallbackPage,
  validateSearch: (search: Record<string, unknown>) => ({
    code: (search.code as string) || "",
    state: (search.state as string) || "",
    error: (search.error as string) || "",
  }),
});

function GoogleCallbackPage() {
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const search = Route.useSearch();

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (search.error) {
      setIsLoading(false);
      setErrorMessage(`Google authentication error: ${search.error}`);
      return;
    }

    if (!search.code) {
      setIsLoading(false);
      setErrorMessage("No authorization code was received from Google.");
      return;
    }

    handleCodeExchange(search.code);
  }, [search.code, search.error]);

  const handleCodeExchange = async (code: string) => {
    try {
      setIsLoading(true);
      const redirectUri = `${window.location.origin}/auth/google/callback`;
      const user = await loginWithGoogle({ code, redirect_uri: redirectUri });
      toast.success("Google Authentication Successful", {
        description: `Welcome to SentinelAI, ${user.displayName || user.username}.`,
      });
      navigate({ to: "/" });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Failed to complete Google authentication.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <AuthLayout
        title="Authenticating with Google"
        subtitle="Verifying OpenID Connect identity with SentinelAI backend"
      >
        <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
          <Loader2 className="size-10 animate-spin text-primary" />
          <p className="text-xs text-muted-foreground font-mono">
            Exchanging cryptographic tokens and restoring session...
          </p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Google Sign-In Status"
      subtitle="Google OAuth authorization callback"
    >
      <div className="space-y-5 text-center">
        {errorMessage ? (
          <>
            <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-destructive/15 text-destructive">
              <AlertCircle className="size-8" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-semibold text-foreground">
                Authentication Could Not Be Completed
              </h3>
              <p className="text-xs text-destructive leading-relaxed">
                {errorMessage}
              </p>
            </div>
          </>
        ) : (
          <>
            <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success">
              <CheckCircle2 className="size-8" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-semibold text-foreground">
                Authentication Verified
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Redirecting to SentinelAI dashboard...
              </p>
            </div>
          </>
        )}

        <Button
          type="button"
          onClick={() => navigate({ to: "/login" })}
          className="w-full font-semibold"
        >
          Return to Login
        </Button>
      </div>
    </AuthLayout>
  );
}
