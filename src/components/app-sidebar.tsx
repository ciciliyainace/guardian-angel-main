import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity, BarChart3, BellRing, BrainCircuit, FileText, Flame, HeartPulse, LayoutDashboard, ListChecks, Radar, Settings, ShieldCheck,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
} from "@/components/ui/sidebar";

type NavItem = { title: string; url: "/" | "/traffic" | "/threats" | "/alerts" | "/analytics" | "/rules" | "/firewall" | "/reports" | "/health" | "/settings"; icon: LucideIcon };
export const NAV: { group: string; items: NavItem[] }[] = [
  { group: "Monitor", items: [
    { title: "Overview", url: "/", icon: LayoutDashboard },
    { title: "Live Traffic", url: "/traffic", icon: Activity },
    { title: "Threat Detection", url: "/threats", icon: Radar },
    { title: "Security Alerts", url: "/alerts", icon: BellRing },
  ]},
  { group: "Intelligence", items: [
    { title: "AI Analytics", url: "/analytics", icon: BrainCircuit },
    { title: "Detection Rules", url: "/rules", icon: ListChecks },
  ]},
  { group: "Response", items: [
    { title: "Firewall Management", url: "/firewall", icon: Flame },
    { title: "Reports & Logs", url: "/reports", icon: FileText },
  ]},
  { group: "System", items: [
    { title: "System Health", url: "/health", icon: HeartPulse },
    { title: "Settings", url: "/settings", icon: Settings },
  ]},
];

export function AppSidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <Link to="/" className="flex items-center gap-2 px-1 py-1.5">
          <span className="grid size-8 shrink-0 place-items-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck className="size-5" />
          </span>
          <span className="truncate group-data-[collapsible=icon]:hidden">
            <span className="block text-sm font-semibold leading-tight">Sentinel AI</span>
            <span className="block text-[11px] text-muted-foreground">Firewall Security Center</span>
          </span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        {NAV.map((g) => (
          <SidebarGroup key={g.group}>
            <SidebarGroupLabel>{g.group}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {g.items.map((item) => (
                  <SidebarMenuItem key={item.url}>
                    <SidebarMenuButton asChild isActive={path === item.url} tooltip={item.title}>
                      <Link to={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-2 rounded-md border border-primary/30 bg-primary/10 px-2 py-1.5 text-[11px] font-semibold text-primary group-data-[collapsible=icon]:hidden">
          <BarChart3 className="size-3.5" /> SentinelAI · Host Telemetry
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
