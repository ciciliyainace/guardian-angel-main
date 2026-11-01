import { Check, X } from "lucide-react";

export interface PasswordAnalysis {
  score: number; // 0 to 4
  label: string;
  colorClass: string;
  hasMinLength: boolean;
  hasUpper: boolean;
  hasLower: boolean;
  hasNumberOrSymbol: boolean;
}

export function analyzePassword(password: string): PasswordAnalysis {
  const hasMinLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumberOrSymbol = /[0-9!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password);

  let score = 0;
  if (hasMinLength) score += 1;
  if (hasUpper) score += 1;
  if (hasLower) score += 1;
  if (hasNumberOrSymbol) score += 1;

  let label = "Very Weak";
  let colorClass = "bg-destructive text-destructive";

  if (score === 1) {
    label = "Weak";
    colorClass = "bg-destructive text-destructive";
  } else if (score === 2) {
    label = "Fair";
    colorClass = "bg-warning text-warning";
  } else if (score === 3) {
    label = "Good";
    colorClass = "bg-info text-info";
  } else if (score === 4) {
    label = "Strong";
    colorClass = "bg-success text-success";
  }

  return {
    score,
    label,
    colorClass,
    hasMinLength,
    hasUpper,
    hasLower,
    hasNumberOrSymbol,
  };
}

export function PasswordStrengthMeter({ password }: { password: string }) {
  if (!password) return null;

  const analysis = analyzePassword(password);
  const percent = (analysis.score / 4) * 100;

  return (
    <div className="space-y-2.5 pt-1 text-xs">
      <div className="flex items-center justify-between font-mono text-[11px]">
        <span className="text-muted-foreground">Password Strength</span>
        <span className={`font-semibold ${analysis.colorClass.split(" ")[1]}`}>
          {analysis.label}
        </span>
      </div>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full transition-all duration-300 ${analysis.colorClass.split(" ")[0]}`}
          style={{ width: `${percent}%` }}
        />
      </div>

      <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-1.5">
          {analysis.hasMinLength ? (
            <Check className="size-3.5 text-success" />
          ) : (
            <X className="size-3.5 text-muted-foreground/60" />
          )}
          <span>8+ characters</span>
        </div>
        <div className="flex items-center gap-1.5">
          {analysis.hasUpper ? (
            <Check className="size-3.5 text-success" />
          ) : (
            <X className="size-3.5 text-muted-foreground/60" />
          )}
          <span>Uppercase letter</span>
        </div>
        <div className="flex items-center gap-1.5">
          {analysis.hasLower ? (
            <Check className="size-3.5 text-success" />
          ) : (
            <X className="size-3.5 text-muted-foreground/60" />
          )}
          <span>Lowercase letter</span>
        </div>
        <div className="flex items-center gap-1.5">
          {analysis.hasNumberOrSymbol ? (
            <Check className="size-3.5 text-success" />
          ) : (
            <X className="size-3.5 text-muted-foreground/60" />
          )}
          <span>Number or symbol</span>
        </div>
      </div>
    </div>
  );
}
