import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { AuthLayout } from "@/components/auth/auth-layout";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Lock, LogIn, Mail, User, AlertCircle } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/login")({
  component: LoginPage,
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: (search.redirect as string) || "/",
  }),
});

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const search = Route.useSearch();
  const redirectTarget = search.redirect || "/";

  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!usernameOrEmail.trim() || !password) {
      setErrorMessage("Please enter both username/email and password.");
      return;
    }

    try {
      setIsLoading(true);
      const user = await login(usernameOrEmail.trim(), password);
      toast.success("Authentication Successful", {
        description: `Welcome back, ${user.displayName || user.username}.`,
      });
      navigate({ to: redirectTarget });
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMessage(e.message || "Invalid username/email or password.");
      toast.error("Login Failed", {
        description: e.message || "Invalid username/email or password.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title="SOC Access Portal"
      subtitle="Enter your verified credentials to access SentinelAI Defense System"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
            <AlertCircle className="mt-0.5 size-4 shrink-0" />
            <span className="leading-relaxed">{errorMessage}</span>
          </div>
        )}

        {/* Username or Email */}
        <div className="space-y-1.5">
          <Label htmlFor="identifier" className="text-xs font-medium">
            Username or Email Address
          </Label>
          <div className="relative">
            <User className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="identifier"
              type="text"
              autoComplete="username"
              placeholder="e.g. analyst or user@corp.net"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              className="pl-9 text-sm"
              disabled={isLoading}
              required
            />
          </div>
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-xs font-medium">
              Password
            </Label>
            <Link
              to="/forgot-password"
              className="text-xs text-primary transition-colors hover:text-primary/80 hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••••••"
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
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full gap-2 font-semibold shadow-sm transition-all"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Verifying Credentials...
            </span>
          ) : (
            <>
              <LogIn className="size-4" /> Sign In
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
        <GoogleSignInButton label="Continue with Google" disabled={isLoading} />

        {/* Register link */}
        <div className="pt-2 text-center text-xs text-muted-foreground">
          Don't have an account yet?{" "}
          <Link
            to="/register"
            className="font-semibold text-primary transition-colors hover:text-primary/80 hover:underline"
          >
            Create an account
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
