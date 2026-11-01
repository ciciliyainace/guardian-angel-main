import { useEffect, useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CheckCircle2, AlertCircle, MailCheck, Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/verify-email")({
  component: VerifyEmailPage,
  validateSearch: (search: Record<string, unknown>) => ({
    token: (search.token as string) || "",
  }),
});

function VerifyEmailPage() {
  const { verifyEmail, resendVerification } = useAuth();
  const search = Route.useSearch();
  const navigate = useNavigate();

  const [token, setToken] = useState(search.token || "");
  const [resendEmail, setResendEmail] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [resendStatus, setResendStatus] = useState<string | null>(null);

  useEffect(() => {
    if (search.token && !isSuccess && !isVerifying && !errorMessage) {
      handleAutoVerify(search.token);
    }
  }, [search.token]);

  const handleAutoVerify = async (tok: string) => {
    try {
      setIsVerifying(true);
      setErrorMessage(null);
      await verifyEmail(tok);
      setIsSuccess(true);
      toast.success("Email Verified", {
        description: "Your email address has been verified successfully.",
      });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Invalid or expired verification token.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;
    handleAutoVerify(token.trim());
  };

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resendEmail.trim()) return;

    try {
      setResendStatus("sending");
      const res = await resendVerification(resendEmail.trim());
      setResendStatus("sent");
      toast.info("Verification Dispatched", {
        description: res.message || "Verification email has been sent.",
      });
    } catch (err: unknown) {
      const e = err as Error;
      setResendStatus(null);
      toast.error("Resend Failed", {
        description: e.message || "Could not resend verification email.",
      });
    }
  };

  if (isVerifying) {
    return (
      <AuthLayout
        title="Verifying Email"
        subtitle="Cryptographically validating your verification token with SentinelAI"
      >
        <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
          <Loader2 className="size-10 animate-spin text-primary" />
          <p className="text-xs text-muted-foreground font-mono">
            Validating single-use token in MongoDB Atlas...
          </p>
        </div>
      </AuthLayout>
    );
  }

  if (isSuccess) {
    return (
      <AuthLayout
        title="Email Verified Successfully"
        subtitle="Your SentinelAI account identity has been confirmed"
      >
        <div className="space-y-5 text-center">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success">
            <CheckCircle2 className="size-8" />
          </div>

          <div className="space-y-1.5">
            <h3 className="text-base font-semibold text-foreground">
              Identity Confirmed
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Your email address is now verified. You have full access to network defense analytics, alert reviews, and firewall management.
            </p>
          </div>

          <Button
            type="button"
            onClick={() => navigate({ to: "/" })}
            className="w-full gap-2 font-semibold"
          >
            Enter Security Operations Center <ArrowRight className="size-4" />
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Verify Email Address"
      subtitle="Complete your SentinelAI account verification"
    >
      <div className="space-y-5">
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="mt-0.5 size-4 shrink-0" />
            <span className="leading-relaxed">{errorMessage}</span>
          </div>
        )}

        {/* Manual Token Verification Form */}
        <form onSubmit={handleManualSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <Label htmlFor="token" className="text-xs font-medium">
              Verification Token
            </Label>
            <Input
              id="token"
              type="text"
              placeholder="Paste verification token here"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="font-mono text-xs"
              required
            />
          </div>

          <Button type="submit" disabled={!token.trim()} className="w-full gap-2 font-semibold">
            <MailCheck className="size-4" /> Verify Account
          </Button>
        </form>

        {/* Resend Verification Section */}
        <div className="rounded-lg border border-border/70 bg-muted/20 p-4 space-y-3">
          <div className="text-xs font-medium text-foreground">
            Need a new verification link?
          </div>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            If your token expired or you didn't receive the original email, enter your email below to request a new link.
          </p>

          <form onSubmit={handleResend} className="flex gap-2">
            <Input
              type="email"
              placeholder="user@sentinelai.local"
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              className="text-xs flex-1"
              required
            />
            <Button
              type="submit"
              variant="secondary"
              size="sm"
              disabled={resendStatus === "sending" || !resendEmail.trim()}
              className="text-xs"
            >
              {resendStatus === "sending" ? "Sending..." : resendStatus === "sent" ? "Sent ✓" : "Resend"}
            </Button>
          </form>
        </div>

        <div className="text-center text-xs">
          <Link
            to="/login"
            className="text-muted-foreground transition-colors hover:text-foreground hover:underline"
          >
            Return to Login
          </Link>
        </div>
      </div>
    </AuthLayout>
  );
}
