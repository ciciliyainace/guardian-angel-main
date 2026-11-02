import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail, ArrowLeft, CheckCircle2, AlertCircle, KeyRound } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/forgot-password")({
  component: ForgotPasswordPage,
});

function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim()) {
      setErrorMessage("Please enter your registered email address.");
      return;
    }

    try {
      setIsLoading(true);
      await forgotPassword(email.trim().toLowerCase());
      setIsSubmitted(true);
      toast.success("Reset Request Dispatched", {
        description: "If an account with that email exists, reset instructions have been dispatched.",
      });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Failed to submit password reset request.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <AuthLayout
        title="Check Your Email"
        subtitle="Password reset instructions have been dispatched"
      >
        <div className="space-y-5 text-center">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-primary/15 text-primary">
            <CheckCircle2 className="size-8" />
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold text-foreground">
              Reset Instructions Dispatched
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              If an active account exists for <span className="font-mono font-semibold text-primary">{email}</span>, a secure single-use reset link has been dispatched.
            </p>
          </div>

          <div className="rounded-lg border border-border/70 bg-muted/30 p-3.5 text-left text-xs text-muted-foreground space-y-1.5">
            <p>• The reset link is single-use and will expire in 30 minutes.</p>
            <p>• If you don't receive an email within 5 minutes, verify your spam folder.</p>
            <p>• Never share password reset links with anyone.</p>
          </div>

          <div className="pt-2">
            <Link
              to="/login"
              className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-secondary py-2 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80"
            >
              <ArrowLeft className="size-3.5" /> Return to Login
            </Link>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Reset Account Password"
      subtitle="Enter your email to receive a secure password recovery link"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="mt-0.5 size-4 shrink-0" />
            <span className="leading-relaxed">{errorMessage}</span>
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="reset-email" className="text-xs font-medium">
            Account Email Address
          </Label>
          <div className="relative">
            <Mail className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="reset-email"
              type="email"
              autoComplete="email"
              placeholder="e.g. analyst@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-9 text-sm"
              disabled={isLoading}
              required
            />
          </div>
        </div>

        <Button
          type="submit"
          disabled={isLoading}
          className="w-full gap-2 font-semibold shadow-sm transition-all"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Dispatching Instructions...
            </span>
          ) : (
            <>
              <KeyRound className="size-4" /> Send Recovery Link
            </>
          )}
        </Button>

        <div className="pt-2 text-center text-xs">
          <Link
            to="/login"
            className="inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-3.5" /> Back to Login
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
