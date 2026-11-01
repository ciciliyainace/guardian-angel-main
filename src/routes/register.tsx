import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { PasswordStrengthMeter, analyzePassword } from "@/components/auth/password-strength";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  UserCheck,
  AlertCircle,
  CheckCircle2,
  Send,
} from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/register")({
  component: RegisterPage,
});

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [registeredUser, setRegisteredUser] = useState<{
    username: string;
    email: string;
  } | null>(null);

  const passwordAnalysis = analyzePassword(password);
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Frontend validations
    if (!username.trim() || !email.trim() || !password || !confirmPassword) {
      setErrorMessage("Please fill in all required registration fields.");
      return;
    }

    if (username.trim().length < 3) {
      setErrorMessage("Username must be at least 3 characters in length.");
      return;
    }

    if (!/^[a-zA-Z0-9_\-\.]+$/.test(username.trim())) {
      setErrorMessage("Username may only contain letters, numbers, hyphens, and underscores.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage("Password and confirmation password do not match.");
      return;
    }

    if (passwordAnalysis.score < 2) {
      setErrorMessage("Please choose a stronger password meeting security requirements.");
      return;
    }

    if (!termsAccepted) {
      setErrorMessage("You must acknowledge the Security Operations & Terms policy to proceed.");
      return;
    }

    try {
      setIsLoading(true);
      const user = await register({
        username: username.trim(),
        email: email.trim().toLowerCase(),
        password,
        confirm_password: confirmPassword,
        terms_accepted: termsAccepted,
      });

      setRegisteredUser({
        username: user.username,
        email: user.email,
      });

      toast.success("Account Created", {
        description: `Account for ${user.username} successfully registered. Welcome email sent.`,
      });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Failed to create account. Please verify your details.");
      toast.error("Registration Error", {
        description: e.message || "Failed to create account.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // If successfully registered, show clear confirmation view
  if (registeredUser) {
    return (
      <AuthLayout
        title="Account Provisioned"
        subtitle="Your SentinelAI SOC analyst credentials have been created"
      >
        <div className="space-y-5 text-center">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success">
            <CheckCircle2 className="size-8" />
          </div>

          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-foreground">
              Welcome to the Defense Team, {registeredUser.username}!
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Your account has been saved in MongoDB Atlas. We have dispatched a confirmation email with account details to:
            </p>
            <div className="rounded-md border border-primary/30 bg-primary/10 py-2 px-3 font-mono text-xs font-semibold text-primary">
              {registeredUser.email}
            </div>
          </div>

          <div className="rounded-lg border border-border/70 bg-muted/30 p-3.5 text-left text-xs text-muted-foreground space-y-1.5">
            <div className="flex items-center gap-2 font-medium text-foreground">
              <Send className="size-3.5 text-primary" />
              <span>Next Steps:</span>
            </div>
            <p>1. Check your inbox for the SentinelAI welcome notification.</p>
            <p>2. If verification is enabled, click the verification link in the email.</p>
            <p>3. Sign in to your dashboard to monitor live firewall and ML events.</p>
          </div>

          <Button
            type="button"
            onClick={() => navigate({ to: "/login" })}
            className="w-full font-semibold"
          >
            Proceed to Login
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Create SOC Account"
      subtitle="Register an analyst account on SentinelAI Defense System"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="mt-0.5 size-4 shrink-0" />
            <span className="leading-relaxed">{errorMessage}</span>
          </div>
        )}

        {/* Username */}
        <div className="space-y-1.5">
          <Label htmlFor="username" className="text-xs font-medium">
            Username
          </Label>
          <div className="relative">
            <User className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="username"
              type="text"
              autoComplete="username"
              placeholder="e.g. analyst_john"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="pl-9 text-sm"
              disabled={isLoading}
              required
            />
          </div>
        </div>

        {/* Email Address */}
        <div className="space-y-1.5">
          <Label htmlFor="email" className="text-xs font-medium">
            Email Address
          </Label>
          <div className="relative">
            <Mail className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="e.g. analyst@sentinelai.local"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-9 text-sm"
              disabled={isLoading}
              required
            />
          </div>
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-password" className="text-xs font-medium">
            Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="reg-password"
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
          {/* Real-time Password Strength Meter */}
          <PasswordStrengthMeter password={password} />
        </div>

        {/* Confirm Password */}
        <div className="space-y-1.5">
          <Label htmlFor="confirm-password" className="text-xs font-medium">
            Confirm Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="confirm-password"
              type={showConfirmPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Re-enter your password"
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
                <span className="text-success flex items-center gap-1">
                  ✓ Passwords match
                </span>
              ) : (
                <span className="text-destructive flex items-center gap-1">
                  ✕ Passwords do not match
                </span>
              )}
            </div>
          )}
        </div>

        {/* Terms Acknowledgment */}
        <div className="flex items-start gap-2.5 pt-1">
          <Checkbox
            id="terms"
            checked={termsAccepted}
            onCheckedChange={(checked) => setTermsAccepted(checked === true)}
            className="mt-0.5"
          />
          <Label htmlFor="terms" className="text-xs text-muted-foreground leading-snug cursor-pointer">
            I acknowledge SentinelAI's Security & Compliance Policies, and agree to keep authentication credentials confidential.
          </Label>
        </div>

        {/* Submit Register Button */}
        <Button
          type="submit"
          disabled={isLoading || !termsAccepted}
          className="w-full gap-2 font-semibold shadow-sm transition-all"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Provisioning Account...
            </span>
          ) : (
            <>
              <UserCheck className="size-4" /> Create Account
            </>
          )}
        </Button>

        {/* Separator */}
        <div className="relative my-4 flex items-center justify-center">
          <div className="w-full border-t border-border/80" />
          <span className="absolute bg-card px-3 font-mono text-[11px] text-muted-foreground uppercase">
            Or
          </span>
        </div>

        {/* Continue with Google */}
        <GoogleSignInButton label="Register with Google" disabled={isLoading} />

        {/* Login link */}
        <div className="pt-2 text-center text-xs text-muted-foreground">
          Already registered?{" "}
          <Link
            to="/login"
            className="font-semibold text-primary transition-colors hover:text-primary/80 hover:underline"
          >
            Sign in to existing account
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
