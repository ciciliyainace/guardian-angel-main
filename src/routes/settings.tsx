import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import {
  Loader2,
  Plus,
  ShieldCheck,
  Cpu,
  Edit3,
  Save,
  X,
  AlertTriangle,
  Mail,
  LifeBuoy,
  HelpCircle,
  Info,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Send,
  KeyRound,
  ShieldAlert,
  Building,
  Copy,
  Check,
  Terminal,
  Key,
  RefreshCw,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader, Panel } from "@/components/soc";
import { useTheme } from "@/lib/theme";
import { useAuth } from "@/lib/auth-context";
import { api, getAuthToken } from "@/lib/api";

const TABS = ["profile", "sensors", "security", "appearance", "help", "about", "feedback"] as const;
type Tab = (typeof TABS)[number];
const T = "Settings — Sentinel AI";
const D = "Profile, workspace sensors, security operations, and support settings.";

export const Route = createFileRoute("/settings")({
  validateSearch: (s: Record<string, unknown>): { tab?: Tab } =>
    TABS.includes(s["tab"] as Tab) ? { tab: s["tab"] as Tab } : {},
  head: () => ({
    meta: [
      { title: T },
      { name: "description", content: D },
      { property: "og:title", content: T },
      { property: "og:description", content: D },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Settings,
});

function Settings() {
  const { tab = "profile" } = Route.useSearch();
  const navigate = useNavigate({ from: "/settings" });
  const { theme, setTheme } = useTheme();
  const { user, resendVerification, logout, refreshUser } = useAuth();

  // Profile State
  const [profile, setProfile] = useState<{
    displayName?: string;
    email?: string;
    role?: string;
    username?: string;
    email_verified?: boolean;
    auth_providers?: string[];
    default_workspace_id?: string;
    workspace_name?: string;
    last_login_at?: string;
  }>({
    displayName: user?.display_name || user?.username || "",
    email: user?.email || "",
    role: user?.role || "analyst",
    username: user?.username || "",
    email_verified: Boolean(user?.email_verified ?? (user as any)?.emailVerified ?? false),
    auth_providers: user?.auth_providers || ["password"],
    default_workspace_id: user?.default_workspace_id,
    workspace_name: user?.workspace_name,
  });
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [resendingVerification, setResendingVerification] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editDisplayName, setEditDisplayName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  // Sensors State
  const [sensorsList, setSensorsList] = useState<any[]>([]);
  const [loadingSensors, setLoadingSensors] = useState(false);
  const [newSensorId, setNewSensorId] = useState("");
  const [newSensorName, setNewSensorName] = useState("");
  const [enrollingSensor, setEnrollingSensor] = useState(false);
  const [revealedCredential, setRevealedCredential] = useState<{
    sensorId: string;
    sensorName: string;
    enrollmentCredential?: string;
    sensorToken?: string;
    expiresAt?: string;
    workspaceName?: string;
    workspaceId?: string;
    isRotation?: boolean;
  } | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = async (text: string, fieldName: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(fieldName);
      toast.success(`${fieldName} copied to clipboard`);
      setTimeout(() => setCopiedField(null), 2500);
    } catch {
      toast.error(`Failed to copy ${fieldName}`);
    }
  };

  const dismissCredential = () => {
    setRevealedCredential(null);
    setCopiedField(null);
    toast.info("Credential dismissed and purged from view.");
  };

  // Security Login Form State
  const [loginUser, setLoginUser] = useState("admin");
  const [loginPass, setLoginPass] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);
  const [hasToken, setHasToken] = useState(!!getAuthToken());

  // Support & Feedback Form State
  const [supportSubject, setSupportSubject] = useState("");
  const [supportCategory, setSupportCategory] = useState("Account & Verification");
  const [supportContactEmail, setSupportContactEmail] = useState("");
  const [supportMessage, setSupportMessage] = useState("");
  const [submittingSupport, setSubmittingSupport] = useState(false);
  const [supportTicketSubmitted, setSupportTicketSubmitted] = useState<{
    ticket_id: string;
    subject: string;
    contact_email: string;
  } | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoadingProfile(true);
    api
      .getProfile()
      .then((p) => {
        if (isMounted && p) {
          const verified = Boolean(p.email_verified ?? (p as any).emailVerified ?? user?.email_verified ?? false);
          setProfile({
            ...p,
            email_verified: verified,
            displayName: p.displayName || (p as any).display_name || p.username,
            workspace_name: p.workspace_name || (p as any).workspaceName,
            default_workspace_id: p.default_workspace_id || (p as any).defaultWorkspaceId,
          });
          if (!supportContactEmail) {
            setSupportContactEmail(p.email || user?.email || "");
          }
        }
      })
      .catch(() => {})
      .finally(() => {
        if (isMounted) setLoadingProfile(false);
      });
    return () => {
      isMounted = false;
    };
  }, [user]);

  useEffect(() => {
    if (tab === "sensors") {
      setLoadingSensors(true);
      api
        .sensors()
        .then((s) => setSensorsList(s || []))
        .catch(() => setSensorsList([]))
        .finally(() => setLoadingSensors(false));
    }
  }, [tab]);

  const handleEnrollSensor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSensorId.trim() || !newSensorName.trim()) {
      toast.error("Sensor Identifier and Display Name are required");
      return;
    }
    setEnrollingSensor(true);
    try {
      const res = await api.enrollSensor({
        sensor_id: newSensorId.trim(),
        name: newSensorName.trim(),
        collector_types: ["windows_sockets", "suricata"],
      });

      // Clear separation of one-time desktop enrollment credential vs runtime sensor token
      const cred = res.enrollment_credential || (res.api_key?.startsWith("sen_enroll_") ? res.api_key : undefined);
      const token = res.sensor_token || (res.api_key?.startsWith("sen_live_") ? res.api_key : undefined);

      setRevealedCredential({
        sensorId: res.sensor_id || newSensorId.trim(),
        sensorName: res.name || newSensorName.trim(),
        enrollmentCredential: cred || res.api_key,
        sensorToken: token,
        expiresAt: res.expires_at,
        workspaceName: res.workspace_name || profile.workspace_name,
        workspaceId: res.workspace_id,
        isRotation: false,
      });

      toast.success("Sensor Registered — One-Time Credential Generated", {
        description: `Enrollment credential generated for '${res.sensor_id}'. Paste into Step 8 of Windows Sensor Setup.`,
      });
      setNewSensorId("");
      setNewSensorName("");
      const updated = await api.sensors();
      setSensorsList(updated || []);
    } catch (err: any) {
      toast.error(err?.message || "Failed to enroll sensor");
    } finally {
      setEnrollingSensor(false);
    }
  };

  const handleRotateSensorKey = async (sensorId: string) => {
    try {
      const res = await api.rotateSensorKey(sensorId);
      const cred = res.enrollment_credential || (res.api_key?.startsWith("sen_enroll_") ? res.api_key : undefined);
      const token = res.sensor_token || (res.api_key?.startsWith("sen_live_") ? res.api_key : undefined);

      setRevealedCredential({
        sensorId: res.sensor_id || sensorId,
        sensorName: res.name || sensorId,
        enrollmentCredential: cred || res.api_key,
        sensorToken: token,
        expiresAt: res.expires_at,
        workspaceName: res.workspace_name || profile.workspace_name,
        workspaceId: res.workspace_id,
        isRotation: true,
      });

      toast.success(`Fresh Enrollment Credential Generated for '${sensorId}'`, {
        description: "Paste into Step 8 of your Windows Sensor Setup wizard.",
      });
      const updated = await api.sensors();
      setSensorsList(updated || []);
    } catch (err: any) {
      toast.error(err?.message || "Failed to rotate sensor key");
    }
  };

  const handleRevokeSensor = async (sensorId: string) => {
    if (!confirm(`Are you sure you want to revoke sensor '${sensorId}'?`)) return;
    try {
      await api.revokeSensor(sensorId);
      toast.success(`Sensor '${sensorId}' has been revoked`);
      const updated = await api.sensors();
      setSensorsList(updated || []);
    } catch (err: any) {
      toast.error(err?.message || "Failed to revoke sensor");
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    try {
      await api.login(loginUser, loginPass);
      setHasToken(true);
      toast.success(`Authenticated as ${loginUser}`);
      const updatedProfile = await api.getProfile();
      if (updatedProfile) setProfile(updatedProfile);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed";
      toast.error(msg);
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    setHasToken(false);
    toast.info("Logged out");
    navigate({ to: "/login" });
  };

  const handleResendVerification = async () => {
    const targetEmail = profile.email || user?.email;
    if (!targetEmail) return;
    setResendingVerification(true);
    try {
      const data = await resendVerification(targetEmail);
      if (data.email_status === "awaiting_configuration") {
        toast.warning("Email Delivery Service Pending Configuration", {
          description:
            "SMTP credentials for revenreven287@gmail.com are not configured on the backend hosting provider. Please set SMTP_PASSWORD in your backend environment settings.",
          duration: 9000,
        });
      } else {
        toast.info("Verification Request Dispatched", {
          description: data.message || `A verification link has been dispatched to ${targetEmail}.`,
        });
      }
    } catch (err: any) {
      toast.error(err?.message || "Failed to resend verification email.");
    } finally {
      setResendingVerification(false);
    }
  };

  const handleStartEdit = () => {
    setEditDisplayName(profile.displayName || profile.username || "");
    setEditEmail(profile.email || "");
    setIsEditingProfile(true);
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editEmail.trim()) {
      toast.error("Email address cannot be empty.");
      return;
    }
    try {
      setSavingProfile(true);
      const updated = await api.updateProfile({
        displayName: editDisplayName.trim(),
        email: editEmail.trim().toLowerCase(),
      });
      setProfile(updated);
      setIsEditingProfile(false);
      await refreshUser();
      toast.success("Profile Updated", {
        description: `Your profile has been saved. ${
          updated.email !== profile.email
            ? "A cryptographic verification link has been dispatched to " + updated.email
            : ""
        }`,
      });
    } catch (err: any) {
      toast.error("Update Failed", {
        description: err?.message || "Failed to update profile.",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  const handleSendSupportMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const targetEmail = supportContactEmail.trim() || profile.email || user?.email || "";
    if (!targetEmail) {
      toast.error("Please provide a valid contact email address.");
      return;
    }
    if (!supportSubject.trim()) {
      toast.error("Please enter a subject for your support inquiry.");
      return;
    }
    if (!supportMessage.trim()) {
      toast.error("Please describe your question or issue in detail.");
      return;
    }

    setSubmittingSupport(true);
    try {
      const res = await api.submitSupportMessage({
        subject: supportSubject.trim(),
        category: supportCategory,
        email: targetEmail,
        name: profile.displayName || profile.username || undefined,
        message: supportMessage.trim(),
      });
      setSupportTicketSubmitted({
        ticket_id: res.ticket_id,
        subject: res.subject,
        contact_email: res.contact_email,
      });
      toast.success("Support Ticket Logged", {
        description: `Reference: ${res.ticket_id}. Confirmation dispatched to ${res.contact_email}.`,
        duration: 8000,
      });
      setSupportSubject("");
      setSupportMessage("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit support message";
      toast.error(msg);
    } finally {
      setSubmittingSupport(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" description={D} />

      <Tabs value={tab} onValueChange={(v) => navigate({ search: { tab: v as Tab } })}>
        <TabsList className="flex-wrap">
          {TABS.map((t) => (
            <TabsTrigger key={t} value={t} className="capitalize">
              {t === "feedback" ? "Contact Support" : t}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* ------------------------------------------------------------- */}
        {/* Profile Tab                                                   */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="profile">
          <Panel
            title="User Profile"
            actions={
              !isEditingProfile && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleStartEdit}
                  className="h-8 gap-1.5 text-xs"
                >
                  <Edit3 className="size-3.5" /> Edit Profile
                </Button>
              )
            }
          >
            {loadingProfile ? (
              <div className="flex h-20 items-center text-sm text-muted-foreground">
                <Loader2 className="mr-2 size-4 animate-spin" /> Loading profile...
              </div>
            ) : isEditingProfile ? (
              <form onSubmit={handleSaveProfile} className="space-y-4 max-w-md">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-foreground">Display Name</label>
                  <Input
                    value={editDisplayName}
                    onChange={(e) => setEditDisplayName(e.target.value)}
                    placeholder="Your Name"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-foreground">Email Address</label>
                  <Input
                    type="email"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    placeholder="you@domain.com"
                    required
                    className="h-9 text-sm"
                  />
                  <p className="text-[11px] text-muted-foreground">
                    Changing your email address will reset its status to unverified until confirmed via the link sent to your inbox.
                  </p>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <Button type="submit" size="sm" disabled={savingProfile} className="h-8 gap-1.5 text-xs">
                    {savingProfile ? <Loader2 className="size-3.5 animate-spin" /> : <Save className="size-3.5" />}
                    Save Changes
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditingProfile(false)}
                    disabled={savingProfile}
                    className="h-8 gap-1 text-xs"
                  >
                    <X className="size-3.5" /> Cancel
                  </Button>
                </div>
              </form>
            ) : (
              <div className="space-y-3.5 text-sm">
                {profile.email?.endsWith("@sentinelai.local") && (
                  <div className="flex items-start gap-2.5 rounded-lg border border-warning/40 bg-warning/10 p-3 text-xs text-warning">
                    <AlertTriangle className="mt-0.5 size-4 shrink-0" />
                    <div>
                      <strong>Placeholder Email Detected: </strong>
                      Your account is currently using the seeded local address (<code>{profile.email}</code>).
                      Click <strong>Edit Profile</strong> above to set your genuine email address so you can receive verification links and security alerts.
                    </div>
                  </div>
                )}
                <div>
                  <span className="font-medium text-foreground">Name: </span>
                  <span className="text-muted-foreground">{profile.displayName || profile.username}</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">Username: </span>
                  <span className="font-mono text-xs text-muted-foreground">{profile.username}</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">Email: </span>
                  <span className="font-mono text-xs text-muted-foreground">{profile.email}</span>
                  {Boolean(profile.email_verified) ? (
                    <span className="ml-2 inline-flex items-center rounded bg-success/15 px-1.5 py-0.5 text-[10px] font-medium text-success">
                      ✓ Verified
                    </span>
                  ) : (
                    <span className="ml-2 inline-flex items-center gap-2 flex-wrap">
                      <span className="rounded bg-warning/15 px-1.5 py-0.5 text-[10px] font-medium text-warning">
                        ⚠ Unverified
                      </span>
                      <Button
                        variant="link"
                        size="sm"
                        onClick={handleResendVerification}
                        disabled={resendingVerification}
                        className="h-auto p-0 text-xs text-primary underline"
                      >
                        {resendingVerification ? "Sending..." : "Resend Link"}
                      </Button>
                    </span>
                  )}
                </div>
                <div>
                  <span className="font-medium text-foreground">Workspace: </span>
                  <span className="text-foreground">{profile.workspace_name || "Personal Workspace"}</span>
                  <span className="ml-2 font-mono text-xs text-muted-foreground">({profile.default_workspace_id || "private"})</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">Assigned Role: </span>
                  <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold capitalize text-foreground">
                    {profile.role}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-foreground">Authentication: </span>
                  <span className="inline-flex items-center gap-1">
                    {(profile.auth_providers || ["password"]).map((p) => (
                      <span
                        key={p}
                        className="rounded border bg-muted/50 px-1.5 py-0.5 font-mono text-[11px] text-muted-foreground capitalize"
                      >
                        {p}
                      </span>
                    ))}
                  </span>
                </div>
              </div>
            )}
          </Panel>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* Sensors Tab                                                   */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="sensors">
          <div className="space-y-4">
            <Panel title="Enrolled Network Sensors">
              <div className="space-y-4">
                <p className="text-xs text-muted-foreground">
                  Sensors deployed across your network stream genuine raw packet telemetry and Suricata intrusion detection events into your isolated tenant workspace.
                </p>

                {loadingSensors ? (
                  <div className="flex h-20 items-center justify-center text-xs text-muted-foreground">
                    <Loader2 className="mr-2 size-4 animate-spin" /> Loading enrolled sensors...
                  </div>
                ) : sensorsList.length === 0 ? (
                  <div className="rounded-md border border-dashed p-6 text-center text-xs text-muted-foreground">
                    No active sensors enrolled in this workspace yet. Use the enrollment form below to register a Windows socket or Suricata collector.
                  </div>
                ) : (
                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-left text-xs">
                      <thead className="border-b bg-muted/40 text-muted-foreground">
                        <tr>
                          <th className="p-2.5 font-medium">Sensor ID</th>
                          <th className="p-2.5 font-medium">Sensor Name</th>
                          <th className="p-2.5 font-medium">Registration</th>
                          <th className="p-2.5 font-medium">Connectivity</th>
                          <th className="p-2.5 font-medium">Collectors</th>
                          <th className="p-2.5 font-medium">Last Heartbeat</th>
                          <th className="p-2.5 font-medium text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {sensorsList.map((s) => {
                          const conn = s.connectivity_status || (s.last_heartbeat_at ? "online" : "awaiting_heartbeat");
                          return (
                            <tr key={s.sensor_id} className="hover:bg-muted/20">
                              <td className="p-2.5 font-mono text-foreground font-medium">{s.sensor_id}</td>
                              <td className="p-2.5">{s.name}</td>
                              <td className="p-2.5">
                                <span
                                  className={`inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium ${
                                    s.status === "registered" || s.status === "active"
                                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                      : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                  }`}
                                >
                                  {s.status === "pending_enrollment" ? "Pending Setup" : "Registered"}
                                </span>
                              </td>
                              <td className="p-2.5">
                                {conn === "online" && (
                                  <span className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                                    <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                    Online
                                  </span>
                                )}
                                {conn === "awaiting_heartbeat" && (
                                  <span className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[10px] font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30">
                                    <span className="size-1.5 rounded-full bg-amber-400" />
                                    Awaiting Heartbeat
                                  </span>
                                )}
                                {conn === "pending_enrollment" && (
                                  <span className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[10px] font-medium bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
                                    <span className="size-1.5 rounded-full bg-cyan-400" />
                                    Pending Setup
                                  </span>
                                )}
                                {conn === "offline" && (
                                  <span className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[10px] font-medium bg-zinc-500/15 text-zinc-400 border border-zinc-500/30">
                                    <span className="size-1.5 rounded-full bg-zinc-400" />
                                    Offline
                                  </span>
                                )}
                                {conn === "revoked" && (
                                  <span className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[10px] font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30">
                                    <span className="size-1.5 rounded-full bg-rose-400" />
                                    Revoked
                                  </span>
                                )}
                              </td>
                              <td className="p-2.5 text-muted-foreground">
                                {(s.collector_types || []).join(", ") || "suricata, windows_sockets"}
                              </td>
                              <td className="p-2.5 font-mono text-[11px] text-muted-foreground">
                                {s.last_heartbeat_at ? new Date(s.last_heartbeat_at).toLocaleString() : "Awaiting First Heartbeat"}
                              </td>
                              <td className="p-2.5 text-right space-x-1.5">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="h-7 text-[11px] px-2"
                                  onClick={() => handleRotateSensorKey(s.sensor_id)}
                                >
                                  Rotate Key
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 text-[11px] px-2 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
                                  onClick={() => handleRevokeSensor(s.sensor_id)}
                                >
                                  Revoke
                                </Button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Enrollment Form */}
                <div className="rounded-lg border bg-card p-4">
                  <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5 mb-2">
                    <Plus className="size-3.5 text-primary" /> Enroll New Network Sensor
                  </h4>
                  <form onSubmit={handleEnrollSensor} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                      <label className="text-[11px] text-muted-foreground">Sensor Identifier</label>
                      <Input
                        value={newSensorId}
                        onChange={(e) => setNewSensorId(e.target.value)}
                        placeholder="e.g. sensor-win-edge-01"
                        className="h-8 text-xs mt-1"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-muted-foreground">Display Name</label>
                      <Input
                        value={newSensorName}
                        onChange={(e) => setNewSensorName(e.target.value)}
                        placeholder="e.g. Gateway Packet Collector"
                        className="h-8 text-xs mt-1"
                        required
                      />
                    </div>
                    <div className="flex items-end">
                      <Button type="submit" size="sm" disabled={enrollingSensor} className="h-8 text-xs w-full gap-1.5">
                        {enrollingSensor ? <Loader2 className="size-3.5 animate-spin" /> : <Plus className="size-3.5" />}
                        Generate Sensor Key
                      </Button>
                    </div>
                  </form>

                  {/* One-Time Credential Reveal Modal / Banner */}
                  {revealedCredential && (
                    <div className="mt-4 rounded-lg border-2 border-primary/50 bg-card p-4 space-y-4 shadow-lg animate-in fade-in">
                      {/* Top Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/80 pb-3">
                        <div className="flex items-center gap-2">
                          <KeyRound className="size-4 text-primary shrink-0" />
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-foreground text-xs">
                                {revealedCredential.isRotation ? "Sensor Credential Rotated" : "New Sensor Enrolled"}
                              </span>
                              <span className="rounded bg-primary/15 text-primary border border-primary/30 px-1.5 py-0.5 text-[10px] font-medium">
                                One-Time Reveal
                              </span>
                            </div>
                            <p className="text-[11px] text-muted-foreground mt-0.5">
                              Sensor ID: <span className="font-mono text-foreground font-semibold">{revealedCredential.sensorId}</span>
                              {" · "}Workspace: <span className="text-foreground">{revealedCredential.workspaceName || "Personal Workspace"}</span>
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={dismissCredential}
                          className="h-7 px-2 text-[11px] text-muted-foreground hover:text-foreground shrink-0 self-start sm:self-auto"
                        >
                          <X className="size-3.5 mr-1" /> Dismiss &amp; Purge
                        </Button>
                      </div>

                      {/* 1. One-Time Desktop Enrollment Credential */}
                      {revealedCredential.enrollmentCredential && (
                        <div className="rounded-md border border-amber-500/30 bg-amber-500/10 p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Key className="size-3.5 text-amber-400" />
                              <span className="text-xs font-semibold text-amber-300">
                                Enrollment Credential (One-Time Desktop Setup)
                              </span>
                            </div>
                            <span className="text-[10px] text-amber-300/80 font-mono">
                              Single-Use · Valid 7 Days
                            </span>
                          </div>
                          <p className="text-[11px] text-muted-foreground leading-relaxed">
                            This is your temporary authorization code. Copy and paste this credential into <strong className="text-foreground">Step 8: Connect &amp; Enroll Sensor</strong> of your Windows Sensor Setup desktop wizard.
                          </p>
                          <div className="flex items-center gap-2">
                            <code className="flex-1 font-mono text-xs bg-background/90 p-2 rounded border border-amber-500/30 text-amber-200 select-all break-all font-medium">
                              {revealedCredential.enrollmentCredential}
                            </code>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyToClipboard(revealedCredential.enrollmentCredential!, "Enrollment Credential")}
                              className="h-8 text-xs shrink-0 gap-1.5 border-amber-500/40 text-amber-300 hover:bg-amber-500/20"
                            >
                              {copiedField === "Enrollment Credential" ? <Check className="size-3.5 text-emerald-400" /> : <Copy className="size-3.5" />}
                              {copiedField === "Enrollment Credential" ? "Copied" : "Copy Credential"}
                            </Button>
                          </div>
                          {revealedCredential.expiresAt && (
                            <p className="text-[10px] text-muted-foreground">
                              Expires: {new Date(revealedCredential.expiresAt).toLocaleString()}
                            </p>
                          )}
                        </div>
                      )}

                      {/* 2. Sensor Authentication Token (if issued) */}
                      {revealedCredential.sensorToken && (
                        <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <ShieldCheck className="size-3.5 text-emerald-400" />
                              <span className="text-xs font-semibold text-emerald-300">
                                Sensor Authentication Token (Long-Lived Collector Key)
                              </span>
                            </div>
                            <span className="text-[10px] text-emerald-300/80 font-mono">
                              Collector Daemon Runtime
                            </span>
                          </div>
                          <p className="text-[11px] text-muted-foreground leading-relaxed">
                            Persistent token used exclusively by the background daemon (<code className="text-foreground font-mono">sensor_agent.py</code> or Windows Service) to authenticate heartbeats and telemetry via the <code className="text-foreground font-mono">X-Sensor-Key</code> header.
                          </p>
                          <div className="flex items-center gap-2">
                            <code className="flex-1 font-mono text-xs bg-background/90 p-2 rounded border border-emerald-500/30 text-emerald-200 select-all break-all font-medium">
                              {revealedCredential.sensorToken}
                            </code>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyToClipboard(revealedCredential.sensorToken!, "Sensor Token")}
                              className="h-8 text-xs shrink-0 gap-1.5 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/20"
                            >
                              {copiedField === "Sensor Token" ? <Check className="size-3.5 text-emerald-400" /> : <Copy className="size-3.5" />}
                              {copiedField === "Sensor Token" ? "Copied" : "Copy Token"}
                            </Button>
                          </div>
                        </div>
                      )}

                      {/* 3. Step 8 Windows Sensor Setup Instructions */}
                      <div className="rounded-md border bg-muted/30 p-3 space-y-2 text-xs">
                        <div className="flex items-center gap-1.5 font-semibold text-foreground">
                          <Terminal className="size-3.5 text-primary" />
                          Windows Sensor Setup Wizard — Step 8 Instructions
                        </div>
                        <ol className="list-decimal list-inside space-y-1.5 text-muted-foreground text-[11px] pl-1 leading-relaxed">
                          <li>
                            Open the <strong>SentinelAI Windows Sensor Setup</strong> desktop application as Administrator.
                          </li>
                          <li>
                            Proceed through the setup wizard (Prerequisites, Npcap, Suricata, Network Adapter) until you arrive at <strong className="text-foreground">Step 8: Connect &amp; Enroll Sensor</strong>.
                          </li>
                          <li>
                            Ensure the <strong>Backend URL</strong> is set to: <code className="font-mono text-foreground font-medium">https://guardian-angel-main-1.onrender.com</code>
                          </li>
                          <li>
                            Set <strong>Sensor Name</strong> to match: <code className="font-mono text-foreground font-medium">{revealedCredential.sensorId}</code>
                          </li>
                          <li>
                            Paste the <strong>Enrollment Credential</strong> (<code className="font-mono text-foreground font-medium">sen_enroll_...</code>) copied above into the <em>Sensor Enrollment Credential</em> field.
                          </li>
                          <li>
                            Click <strong>Connect &amp; Enroll Sensor</strong>. The desktop application will automatically exchange the credential for a persistent Sensor Authentication Token and activate live packet forwarding.
                          </li>
                        </ol>
                      </div>

                      {/* 4. One-Time Reveal Policy Notice */}
                      <div className="flex items-start gap-2 rounded border border-amber-500/20 bg-amber-500/5 p-2.5 text-[11px] text-muted-foreground">
                        <AlertTriangle className="size-4 text-amber-400 shrink-0 mt-0.5" />
                        <div className="space-y-1">
                          <strong className="text-foreground">Security Safeguard:</strong> This credential is displayed once and is never stored in plaintext on the server. If you close this tab or navigate away before enrolling the sensor, you will need to click <span className="font-medium text-foreground">Rotate Key</span> in the table above to generate a new enrollment credential.
                        </div>
                      </div>

                      <div className="flex justify-end">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={dismissCredential}
                          className="h-7 text-xs"
                        >
                          I have copied the credential — Dismiss &amp; Purge from View
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Permanent Credential Architecture Reference Card */}
                <div className="rounded-lg border bg-muted/15 p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <ShieldCheck className="size-3.5 text-primary" /> SentinelAI Authentication &amp; Credential Architecture
                  </h4>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    To maintain zero-trust security and multi-tenant workspace isolation, SentinelAI strictly separates user browser sessions from host sensor operations.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
                    <div className="rounded border bg-background/60 p-3 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-medium text-foreground text-[11px]">
                        <KeyRound className="size-3 text-cyan-400" /> User Access JWT
                      </div>
                      <p className="text-[10px] font-mono text-muted-foreground">Header: Authorization: Bearer &lt;jwt&gt;</p>
                      <p className="text-[11px] text-muted-foreground leading-relaxed">
                        Issued upon analyst login to the web dashboard. Grants UI and API query permissions. Expires in 24 hours. <strong>Never</strong> provide your user JWT to the sensor agent.
                      </p>
                    </div>
                    <div className="rounded border bg-background/60 p-3 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-medium text-foreground text-[11px]">
                        <Key className="size-3 text-amber-400" /> Enrollment Credential
                      </div>
                      <p className="text-[10px] font-mono text-muted-foreground">Format: sen_enroll_&lt;32_hex&gt;</p>
                      <p className="text-[11px] text-muted-foreground leading-relaxed">
                        Generated in this dashboard. Single-use and valid for 7 days. Paste this into <strong>Step 8</strong> of the Windows Sensor Setup application to claim ownership of the sensor.
                      </p>
                    </div>
                    <div className="rounded border bg-background/60 p-3 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-medium text-foreground text-[11px]">
                        <ShieldCheck className="size-3 text-emerald-400" /> Sensor Authentication Token
                      </div>
                      <p className="text-[10px] font-mono text-muted-foreground">Header: X-Sensor-Key: sen_live_...</p>
                      <p className="text-[11px] text-muted-foreground leading-relaxed">
                        Issued automatically to the Windows agent upon successful Step 8 enrollment. Used continuously by background daemons to transmit genuine packet telemetry and heartbeats.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Panel>
          </div>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* Security Tab                                                  */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="security">
          <Panel title="SOC Security & Authentication Controls">
            <div className="space-y-4 max-w-lg">
              <div className="rounded-lg border p-4 space-y-2 text-xs">
                <div className="flex items-center gap-2 font-medium text-foreground">
                  <KeyRound className="size-4 text-primary" /> Multi-Factor & Session Security
                </div>
                <p className="text-muted-foreground">
                  Authentication tokens are signed using HMAC-SHA256 and expire after 24 hours. Rate limiting automatically locks accounts for 15 minutes after 5 failed authentication attempts to protect against brute-force intrusion.
                </p>
              </div>

              {hasToken ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-xs text-success">
                    <CheckCircle2 className="size-4" /> Active Authenticated Session
                  </div>
                  <Button variant="outline" size="sm" onClick={handleLogout} className="text-xs">
                    Terminate Current Session (Sign Out)
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleLogin} className="space-y-3">
                  <div>
                    <label className="text-xs text-muted-foreground">Username</label>
                    <Input
                      value={loginUser}
                      onChange={(e) => setLoginUser(e.target.value)}
                      placeholder="Username"
                      required
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Password</label>
                    <Input
                      type="password"
                      value={loginPass}
                      onChange={(e) => setLoginPass(e.target.value)}
                      placeholder="••••••••"
                      required
                    />
                  </div>
                  <Button type="submit" size="sm" disabled={loggingIn} className="w-full">
                    {loggingIn ? <Loader2 className="mr-2 size-3 animate-spin" /> : null}
                    Authenticate
                  </Button>
                </form>
              )}
            </div>
          </Panel>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* Appearance Tab                                                */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="appearance">
          <Panel title="Display Theme">
            <div className="space-y-3 max-w-md">
              <p className="text-xs text-muted-foreground">
                Customize the high-contrast dashboard appearance for optimal SOC operational visibility in day and night environments.
              </p>
              <div className="flex gap-2">
                {(["dark", "light", "system"] as const).map((t) => (
                  <Button
                    key={t}
                    variant={theme === t ? "default" : "outline"}
                    onClick={() => setTheme(t)}
                    className="capitalize text-xs"
                  >
                    {t}
                  </Button>
                ))}
              </div>
            </div>
          </Panel>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* Help Tab — Comprehensive Troubleshooting Guide               */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="help">
          <Panel title="SentinelAI SOC Help & Authentication Guide">
            <div className="space-y-6 text-sm text-muted-foreground">
              {/* Section 1: Authentication */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <ShieldCheck className="size-4 text-primary" /> SentinelAI Authentication & Multi-Tenant Workspaces
                </h3>
                <p className="text-xs leading-relaxed">
                  SentinelAI enforces strict zero-trust tenant workspace isolation. Every registered security analyst operates within a dedicated workspace identifier (e.g. <code>ws_usr_*</code>). All telemetry streams, enrolled sensors, machine learning alert classifications, and firewall block proposals are strictly scoped to the authenticated tenant.
                </p>
              </div>

              {/* Section 2: Email Verification */}
              <div className="space-y-2 rounded-lg border bg-muted/20 p-4">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <Mail className="size-4 text-primary" /> Email Verification Lifecycle & Security Policy
                </h3>
                <p className="text-xs leading-relaxed">
                  To protect enterprise SOC environments from spoofing and unauthorized alert dispatching, account identities must be cryptographically confirmed:
                </p>
                <ul className="list-disc list-inside text-xs space-y-1.5 pl-1">
                  <li>
                    <strong>Single-Use Cryptographic Tokens:</strong> Verification links contain a high-entropy, random cryptographic token whose SHA-256 hash is validated against MongoDB Atlas.
                  </li>
                  <li>
                    <strong>Strict Token Expiration:</strong> Verification tokens expire exactly 24 hours after issuance.
                  </li>
                  <li>
                    <strong>Atomic Consumption:</strong> Each token can only be redeemed once. Once redeemed, the user account is atomically updated with verified status and an audit event is recorded.
                  </li>
                  <li>
                    <strong>Genuine Verification Proof:</strong> The green <span className="text-success font-medium">✓ Verified</span> badge is awarded <em>only</em> upon authentic token redemption via email or validated Google OpenID Connect claim.
                  </li>
                </ul>
              </div>

              {/* Section 3: Resending Verification Links */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <HelpCircle className="size-4 text-primary" /> Resending Verification Links & Rate Limiting
                </h3>
                <p className="text-xs leading-relaxed">
                  If you have not received your verification email, click <strong>Resend Link</strong> under <em>Settings &gt; Profile</em>. Note the following operational safeguards:
                </p>
                <ul className="list-disc list-inside text-xs space-y-1 pl-1">
                  <li>A 60-second cooldown is enforced between consecutive resend attempts.</li>
                  <li>A maximum of 3 verification emails can be requested within any 15-minute window to avoid spam flooding.</li>
                  <li>Check your spam, junk, or promotional folders for dispatches from <code>revenreven287@gmail.com</code>.</li>
                </ul>
              </div>

              {/* Section 4: Access Recovery */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <KeyRound className="size-4 text-primary" /> Account Access Recovery & Password Reset
                </h3>
                <p className="text-xs leading-relaxed">
                  If credentials are lost, use the <strong>Forgot Password</strong> link on the login portal. Password reset tokens expire in 30 minutes, are strictly single-use, and invalidate all prior reset tokens upon issuance.
                </p>
              </div>

              {/* Section 5: Troubleshooting & Support Contact */}
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-4 text-xs space-y-2">
                <div className="font-semibold text-foreground flex items-center gap-1.5">
                  <LifeBuoy className="size-4 text-primary" /> Official Support & Incident Escalation
                </div>
                <p className="text-muted-foreground">
                  If you encounter delivery issues, identity synchronization errors, or require sensor provisioning assistance, our cybersecurity support team is directly reachable at:
                </p>
                <p className="font-mono text-xs">
                  <a
                    href="mailto:revenreven287@gmail.com"
                    className="inline-flex items-center gap-1.5 font-semibold text-primary hover:underline"
                  >
                    <Mail className="size-3.5" /> revenreven287@gmail.com
                  </a>
                </p>
              </div>
            </div>
          </Panel>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* About Tab — Full Architecture & Details                       */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="about">
          <Panel title="About Sentinel AI — SOC Defense System">
            <div className="space-y-5 text-sm text-muted-foreground">
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-foreground">
                  Enterprise AI-Powered Network Firewall Attack Detection System
                </h3>
                <p className="text-xs leading-relaxed">
                  SentinelAI is an advanced intrusion detection and autonomous firewall response platform designed to protect computer network infrastructure against port scans, distributed denial of service (DDoS), credential brute-force attacks, and lateral reconnaissance.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="rounded border bg-card p-3.5 space-y-1.5">
                  <div className="font-semibold text-foreground flex items-center gap-1.5">
                    <Cpu className="size-3.5 text-primary" /> Telemetry & Sensor Architecture
                  </div>
                  <p className="text-muted-foreground">
                    Native multi-engine telemetry ingestion utilizing Suricata IDS EVE JSON parsers alongside real-time Windows raw socket packet capture collectors with safe offset checkpointing.
                  </p>
                </div>

                <div className="rounded border bg-card p-3.5 space-y-1.5">
                  <div className="font-semibold text-foreground flex items-center gap-1.5">
                    <ShieldAlert className="size-3.5 text-primary" /> Hybrid Machine Learning Engine
                  </div>
                  <p className="text-muted-foreground">
                    Supervised Random Forest / Decision Tree multi-class attack classifiers combined with unsupervised Isolation Forest anomaly detectors for zero-day threat discovery.
                  </p>
                </div>
              </div>

              <div className="rounded-lg border p-4 space-y-2 text-xs">
                <div className="font-semibold text-foreground">System & Build Specifications</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-muted-foreground font-mono text-[11px]">
                  <div>Platform: v1.0.0</div>
                  <div>API Protocol: v1.0.0</div>
                  <div>ML Engine: v1.2.0</div>
                  <div>Database: MongoDB Atlas</div>
                </div>
              </div>

              <div className="rounded-lg border border-primary/30 bg-primary/5 p-4 text-xs space-y-1.5">
                <div className="font-semibold text-foreground flex items-center gap-1.5">
                  <Mail className="size-4 text-primary" /> Primary Security & Support Contact
                </div>
                <p className="text-muted-foreground">
                  For administrative inquiries, production sensor keys, or SOC assistance, contact the SentinelAI Security Team:
                </p>
                <p className="font-mono text-xs">
                  <a
                    href="mailto:revenreven287@gmail.com"
                    className="inline-flex items-center gap-1.5 font-semibold text-primary hover:underline"
                  >
                    revenreven287@gmail.com <ExternalLink className="size-3" />
                  </a>
                </p>
              </div>
            </div>
          </Panel>
        </TabsContent>

        {/* ------------------------------------------------------------- */}
        {/* Contact Support & Feedback Tab                                */}
        {/* ------------------------------------------------------------- */}
        <TabsContent value="feedback">
          <Panel title="Contact Security Support & Report False Positives">
            <div className="space-y-5">
              {/* Official Banner */}
              <div className="rounded-lg border border-primary/40 bg-primary/10 p-4 text-xs space-y-2">
                <div className="flex items-center gap-2 font-semibold text-primary">
                  <LifeBuoy className="size-4" /> Dedicated SentinelAI Support Channel
                </div>
                <p className="text-foreground leading-relaxed">
                  Have questions about email verification, sensor deployment, or false-positive firewall alerts? Submit a ticket below or write directly to our designated team at{" "}
                  <a href="mailto:revenreven287@gmail.com" className="font-bold underline text-primary">
                    revenreven287@gmail.com
                  </a>
                  . Every submission is recorded in our audit log and acknowledged via email.
                </p>
              </div>

              {supportTicketSubmitted && (
                <div className="rounded-lg border border-success/40 bg-success/10 p-4 text-xs space-y-1.5">
                  <div className="flex items-center gap-2 font-semibold text-success">
                    <CheckCircle2 className="size-4" /> Ticket Submitted Successfully [{supportTicketSubmitted.ticket_id}]
                  </div>
                  <p className="text-muted-foreground">
                    Your inquiry regarding <strong>{supportTicketSubmitted.subject}</strong> has been logged. An automated acknowledgment has been dispatched to <code>{supportTicketSubmitted.contact_email}</code>.
                  </p>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSendSupportMessage} className="max-w-lg space-y-4">
                <div>
                  <label className="text-xs font-medium text-foreground">Inquiry Category</label>
                  <select
                    value={supportCategory}
                    onChange={(e) => setSupportCategory(e.target.value)}
                    className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-xs ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="Account & Verification">Account & Email Verification</option>
                    <option value="Sensor & Telemetry Ingestion">Sensor & Telemetry Ingestion</option>
                    <option value="Firewall & Detection Rules">Firewall & Detection Rules</option>
                    <option value="False Positive Alert Report">False Positive Alert Report</option>
                    <option value="General Support">General Support Inquiry</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-foreground">Contact Email Address</label>
                  <Input
                    type="email"
                    value={supportContactEmail}
                    onChange={(e) => setSupportContactEmail(e.target.value)}
                    placeholder="you@domain.com"
                    required
                    className="mt-1 h-9 text-xs"
                  />
                  <p className="mt-1 text-[11px] text-muted-foreground">
                    A ticket receipt and response will be dispatched to this address.
                  </p>
                </div>

                <div>
                  <label className="text-xs font-medium text-foreground">Subject / Summary</label>
                  <Input
                    value={supportSubject}
                    onChange={(e) => setSupportSubject(e.target.value)}
                    placeholder="Brief summary of your inquiry (e.g. Email verification assistance)"
                    required
                    className="mt-1 h-9 text-xs"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-foreground">Detailed Explanation</label>
                  <Textarea
                    value={supportMessage}
                    onChange={(e) => setSupportMessage(e.target.value)}
                    placeholder="Describe your issue, steps to reproduce, or questions..."
                    rows={5}
                    required
                    className="mt-1 text-xs"
                  />
                </div>

                <Button type="submit" size="sm" disabled={submittingSupport} className="gap-1.5 text-xs">
                  {submittingSupport ? <Loader2 className="size-3.5 animate-spin" /> : <Send className="size-3.5" />}
                  Submit Support Ticket
                </Button>
              </form>
            </div>
          </Panel>
        </TabsContent>
      </Tabs>
    </div>
  );
}
