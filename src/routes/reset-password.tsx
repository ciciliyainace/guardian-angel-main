import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { PasswordStrengthMeter, analyzePassword } from "@/components/auth/password-strength";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Lock, CheckCircle2, AlertCircle, KeySquare } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/reset-password")({
  component: ResetPasswordPage,
  validateSearch: (search: Record<string, unknown>) => ({
    token: (search.token as string) || "",
  }),
});

function ResetPasswordPage() {
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const search = Route.useSearch();

  const [token, setToken] = useState(search.token || "");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const passwordAnalysis = analyzePassword(password);
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!token.trim()) {
      setErrorMessage("Password reset token is missing. Please use the link provided in your email.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    if (passwordAnalysis.score < 2) {
      setErrorMessage("Please choose a stronger password meeting security requirements.");
      return;
    }

    try {
      setIsLoading(true);
      await resetPassword(token.trim(), password, confirmPassword);
      setIsSuccess(true);
      toast.success("Password Updated", {
        description: "Your password has been changed. You may now log in with your new credentials.",
      });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Failed to reset password. Link may be invalid or expired.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <AuthLayout
        title="Password Successfully Updated"
        subtitle="Your SentinelAI account credentials have been secured"
      >
        <div className="space-y-5 text-center">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success">
            <CheckCircle2 className="size-8" />
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold text-foreground">
              New Password Active
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Your password has been updated in MongoDB Atlas. Previous authentication sessions have been invalidated for security.
            </p>
          </div>

          <Button
            type="button"
            onClick={() => navigate({ to: "/login" })}
            className="w-full font-semibold"
          >
            Sign In with New Password
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Create New Password"
      subtitle="Establish a new secure password for your SentinelAI account"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="mt-0.5 size-4 shrink-0" />
            <span className="leading-relaxed">{errorMessage}</span>
          </div>
        )}

        {/* If token was not present in URL, let user paste it */}
        {!search.token && (
          <div className="space-y-1.5">
            <Label htmlFor="token" className="text-xs font-medium">
              Reset Token
            </Label>
            <div className="relative">
              <KeySquare className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
              <Input
                id="token"
                type="text"
                placeholder="Paste reset token from email"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="pl-9 text-xs font-mono"
                required
              />
            </div>
          </div>
        )}

        {/* New Password */}
        <div className="space-y-1.5">
          <Label htmlFor="new-password" className="text-xs font-medium">
            New Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="new-password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Min. 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="pl-9 pr-10 text-sm"
              disabled={isLoading}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-2.5 text-muted-foreground transition-colors hover:text-foreground"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>
          <PasswordStrengthMeter password={password} />
        </div>

        {/* Confirm Password */}
        <div className="space-y-1.5">
          <Label htmlFor="confirm-reset-password" className="text-xs font-medium">
            Confirm New Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="confirm-reset-password"
              type={showConfirmPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Re-enter new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="pl-9 pr-10 text-sm"
              disabled={isLoading}
              required
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-2.5 text-muted-foreground transition-colors hover:text-foreground"
              aria-label={showConfirmPassword ? "Hide password" : "Show password"}
            >
              {showConfirmPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>
          {confirmPassword.length > 0 && (
            <div className="text-[11px] font-mono">
              {passwordsMatch ? (
                <span className="text-success flex items-center gap-1">✓ Passwords match</span>
              ) : (
                <span className="text-destructive flex items-center gap-1">✕ Passwords do not match</span>
              )}
            </div>
          )}
        </div>

        <Button
          type="submit"
          disabled={isLoading}
          className="w-full gap-2 font-semibold shadow-sm transition-all"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Securing Account...
            </span>
          ) : (
            "Update Password"
          )}
        </Button>

        <div className="pt-2 text-center text-xs">
          <Link
            to="/login"
            className="text-muted-foreground transition-colors hover:text-foreground hover:underline"
          >
            Cancel and Return to Login
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
