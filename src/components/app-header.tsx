import { useEffect, useState } from "react";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Bell, FlaskConical, LogOut, Moon, Search, Sun, Monitor, User, Settings, Palette, HelpCircle, Info, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { NAV } from "@/components/app-sidebar";
import { useTheme } from "@/lib/theme";
import { blockRequests, events, fmtTime, notificationsSeed } from "@/lib/mock-data";
import { SeverityBadge } from "@/components/soc";

import { useAuth } from "@/lib/auth-context";
import { api, type DetailedMonitoringHealth } from "@/lib/api";

export function AppHeader() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const current = NAV.flatMap((g) => g.items).find((i) => i.url === path);
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState(notificationsSeed);
  const [health, setHealth] = useState<DetailedMonitoringHealth | null>(null);
  const unread = notes.filter((n) => !n.read).length;

  useEffect(() => {
    let mounted = true;
    const fetchHealth = () => {
      api.detailedHealth()
        .then((h) => {
          if (mounted) setHealth(h);
        })
        .catch(() => {
          if (mounted) setHealth(null);
        });
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const displayName = user?.display_name || user?.username || "Analyst";
  const initials = displayName
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "SA";
  const roleTitle = user?.role?.toLowerCase() === "administrator" ? "Administrator" : "SOC Analyst";

  const handleSignOut = async () => {
    await logout();
    toast.success("Signed Out", {
      description: "Your SentinelAI session has ended.",
    });
    navigate({ to: "/login" });
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); setOpen((o) => !o); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const go = (to: string) => { setOpen(false); navigate({ to }); };
  const cycle = () => setTheme(theme === "dark" ? "light" : theme === "light" ? "system" : "dark");
  const ThemeIcon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-2 border-b bg-background/90 px-3 backdrop-blur no-print">
      <SidebarTrigger aria-label="Toggle sidebar" />
      <div className="hidden min-w-0 items-center gap-1.5 text-sm sm:flex">
        <span className="text-muted-foreground">Sentinel AI</span>
        <span className="text-muted-foreground">/</span>
        <span className="truncate font-medium">{current?.title ?? "Page"}</span>
      </div>

      <div className="ml-auto flex items-center gap-1.5">
        {health?.overall_status === "LIVE" ? (
          <>
            <span className="hidden items-center gap-1.5 rounded-md border border-success/40 bg-success/10 px-2 py-1 text-[11px] font-bold tracking-wider text-success md:inline-flex">
              <span className="pulse-dot size-2 rounded-full bg-success" /> REAL TELEMETRY ACTIVE
            </span>
            <span className="hidden items-center gap-1.5 px-2 text-xs text-muted-foreground lg:inline-flex">
              {health.active_sensor_count} Host Sensor(s)
            </span>
          </>
        ) : health?.overall_status === "STANDBY" ? (
          <>
            <span className="hidden items-center gap-1.5 rounded-md border border-primary/40 bg-primary/10 px-2 py-1 text-[11px] font-bold tracking-wider text-primary md:inline-flex">
              <span className="size-2 rounded-full bg-primary animate-pulse" /> SENSOR STANDBY
            </span>
            <span className="hidden items-center gap-1.5 px-2 text-xs text-muted-foreground lg:inline-flex">
              Waiting for flows
            </span>
          </>
        ) : (
          <>
            <span className="hidden items-center gap-1.5 rounded-md border border-warning/40 bg-warning/10 px-2 py-1 text-[11px] font-bold tracking-wider text-warning md:inline-flex">
              <FlaskConical className="size-3.5" /> NO LIVE SENSOR
            </span>
            <span className="hidden items-center gap-1.5 px-2 text-xs text-muted-foreground lg:inline-flex">
              Sensor agent offline
            </span>
          </>
        )}
        <Button variant="outline" size="sm" className="gap-2 text-muted-foreground" onClick={() => setOpen(true)} aria-label="Search">
          <Search className="size-4" /><span className="hidden md:inline">Search</span>
          <kbd className="hidden rounded border bg-muted px-1 font-mono text-[10px] md:inline">⌘K</kbd>
        </Button>

        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative" aria-label={`Notifications, ${unread} unread`}>
              <Bell className="size-4" />
              {unread > 0 && <span className="absolute right-1 top-1 grid size-4 place-items-center rounded-full bg-critical text-[10px] font-bold text-destructive-foreground">{unread}</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-80 p-0">
            <div className="flex items-center justify-between border-b px-3 py-2">
              <span className="text-sm font-semibold">Notifications</span>
              <button className="text-xs text-primary hover:underline" onClick={() => setNotes((n) => n.map((x) => ({ ...x, read: true })))}>Mark all read</button>
            </div>
            <ul className="max-h-80 overflow-y-auto">
              {notes.map((n) => (
                <li key={n.id}>
                  <button className="flex w-full gap-2 border-b px-3 py-2.5 text-left hover:bg-muted/50" onClick={() => setNotes((all) => all.map((x) => x.id === n.id ? { ...x, read: true } : x))}>
                    {!n.read ? <span className="mt-1.5 size-2 shrink-0 rounded-full bg-primary" /> : <span className="size-2 shrink-0" />}
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center gap-2 text-xs font-medium">{n.title} <SeverityBadge severity={n.severity} /></span>
                      <span className="block text-xs text-muted-foreground">{n.body}</span>
                      <span className="block font-mono text-[10px] text-muted-foreground">{fmtTime(n.time)}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </PopoverContent>
        </Popover>

        <Button variant="ghost" size="icon" onClick={cycle} aria-label={`Theme: ${theme}`}><ThemeIcon className="size-4" /></Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button aria-label="Profile menu" className="rounded-full focus-visible:ring-2 focus-visible:ring-ring">
              <Avatar className="size-8"><AvatarFallback className="bg-accent text-xs font-semibold text-accent-foreground">{initials}</AvatarFallback></Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-60">
            <DropdownMenuLabel>
              <div className="flex items-center justify-between">
                <span className="truncate text-sm font-semibold">{displayName}</span>
                {user?.email_verified ? (
                  <span className="inline-flex items-center gap-1 rounded bg-success/15 px-1.5 py-0.5 text-[10px] font-medium text-success">
                    Verified
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded bg-warning/15 px-1.5 py-0.5 text-[10px] font-medium text-warning">
                    Unverified
                  </span>
                )}
              </div>
              <div className="truncate text-xs font-normal text-muted-foreground">
                {roleTitle} · {user?.email || "No email"}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "profile" }}><User className="size-4" />My Profile</Link></DropdownMenuItem>
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "security" }}><Settings className="size-4" />Account Settings</Link></DropdownMenuItem>
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "appearance" }}><Palette className="size-4" />Appearance</Link></DropdownMenuItem>
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "help" }}><HelpCircle className="size-4" />Help & Documentation</Link></DropdownMenuItem>
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "about" }}><Info className="size-4" />About Sentinel AI</Link></DropdownMenuItem>
            <DropdownMenuItem asChild><Link to="/settings" search={{ tab: "feedback" }}><MessageSquare className="size-4" />Send Feedback</Link></DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSignOut} className="text-destructive focus:bg-destructive/10 focus:text-destructive">
              <LogOut className="size-4" />Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Search pages, IPs, alerts, block requests…" />
        <CommandList>
          <CommandEmpty>No results.</CommandEmpty>
          <CommandGroup heading="Pages">
            {NAV.flatMap((g) => g.items).map((i) => (
              <CommandItem key={i.url} onSelect={() => go(i.url)}><i.icon />{i.title}</CommandItem>
            ))}
          </CommandGroup>
          <CommandGroup heading="Alerts (simulated)">
            {events.slice(0, 15).map((e) => (
              <CommandItem key={e.id} value={`${e.id} ${e.sourceIp} ${e.category}`} onSelect={() => go("/alerts")}>
                <span className="font-mono text-xs">{e.id}</span> {e.sourceIp} · {e.category}
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandGroup heading="Block requests">
            {blockRequests.slice(0, 6).map((b) => (
              <CommandItem key={b.id} value={`${b.id} ${b.sourceIp}`} onSelect={() => go("/firewall")}>
                <span className="font-mono text-xs">{b.id}</span> {b.sourceIp}
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </header>
  );
}
