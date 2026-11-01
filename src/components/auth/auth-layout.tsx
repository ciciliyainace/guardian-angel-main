import React from "react";
import { ShieldAlert, ShieldCheck } from "lucide-react";

export function AuthLayout({
  children,
  title,
  subtitle,
}: {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-x-hidden bg-background p-4 sm:p-6 lg:p-8">
      {/* High-tech cybersecurity backdrop elements */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 size-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 size-96 rounded-full bg-info/10 blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
          style={{
            backgroundImage: `radial-gradient(var(--foreground) 1px, transparent 1px)`,
            backgroundSize: "24px 24px",
          }}
        />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Brand Header */}
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex items-center gap-2.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 shadow-sm backdrop-blur">
            <ShieldCheck className="size-4 text-primary animate-pulse" />
            <span className="font-mono text-xs font-semibold tracking-wider text-primary uppercase">
              SentinelAI Defense System
            </span>
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            {title}
          </h1>
          <p className="mt-1.5 text-xs text-muted-foreground sm:text-sm">
            {subtitle}
          </p>
        </div>

        {/* Auth Content Card */}
        <div className="rounded-xl border border-border/70 bg-card/75 p-6 shadow-2xl backdrop-blur-xl sm:p-8">
          {children}
        </div>

        {/* Footer Guidance */}
        <div className="mt-6 flex items-center justify-center gap-4 text-center font-mono text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="pulse-dot size-2 rounded-full bg-success" />
            TLS 1.3 / AES-256
          </span>
          <span>•</span>
          <span>Role-Based SOC Access</span>
          <span>•</span>
          <span>MongoDB Atlas</span>
        </div>
      </div>
    </div>
  );
}
