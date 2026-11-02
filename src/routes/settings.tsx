import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import { Loader2, Plus, ShieldCheck, Cpu, Edit3, Save, X, AlertTriangle } from "lucide-react";
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
const D = "Profile, workspace sensors, appearance and application settings.";
export const Route = createFileRoute("/settings")({
  validateSearch: (s: Record<string, unknown>): { tab?: Tab } =>
    TABS.includes(s["tab"] as Tab) ? { tab: s["tab"] as Tab } : {},
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
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
    email_verified: user?.email_verified ?? false,
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
  const [enrolledKey, setEnrolledKey] = useState<string | null>(null);

  // Feedback State
  const [fbCategory, setFbCategory] = useState("False Positive");
  const [fbMessage, setFbMessage] = useState("");
  const [submittingFb, setSubmittingFb] = useState(false);

  // Security Login Form State
  const [loginUser, setLoginUser] = useState("admin");
  const [loginPass, setLoginPass] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);
  const [hasToken, setHasToken] = useState(!!getAuthToken());

  useEffect(() => {
    let isMounted = true;
    setLoadingProfile(true);
    api
      .getProfile()
      .then((p) => {
        if (isMounted && p) setProfile(p);
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
      toast.error("Sensor ID and Name are required");
      return;
    }
    setEnrollingSensor(true);
    try {
      const res = await api.enrollSensor({
        sensor_id: newSensorId.trim(),
        name: newSensorName.trim(),
        collector_types: ["windows_sockets", "suricata"],
      });
      setEnrolledKey(res.api_key);
      toast.success("Sensor enrolled successfully!");
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

  const handleSendFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fbMessage.trim()) {
      toast.error("Please enter a feedback message");
      return;
    }
    setSubmittingFb(true);
    try {
      await api.submitFeedback(fbCategory, fbMessage);
      toast.success("Feedback submitted to SentinelAI security team");
      setFbMessage("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit feedback";
      toast.error(msg);
    } finally {
      setSubmittingFb(false);
    }
  };

  const handleResendVerification = async () => {
    const targetEmail = profile.email || user?.email;
    if (!targetEmail) return;
    setResendingVerification(true);
    try {
      const data = await resendVerification(targetEmail);
      toast.info("Verification Request Dispatched", {
        description: data.message || "A verification link has been sent to your email.",
      });
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
        description: `Your profile has been saved. ${updated.email !== profile.email ? "A verification link has been dispatched to " + updated.email : ""}`,
      });
    } catch (err: any) {
      toast.error("Update Failed", {
        description: err?.message || "Failed to update profile.",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" description={D} />
      <Tabs value={tab} onValueChange={(v) => navigate({ search: { tab: v as Tab } })}>
        <TabsList className="flex-wrap">
          {TABS.map((t) => (
            <TabsTrigger key={t} value={t} className="capitalize">
              {t}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Profile Tab */}
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
                    Updating your email will set its status to unverified until confirmed via the link sent to your inbox.
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
                  {profile.email_verified ? (
                    <span className="ml-2 inline-flex items-center rounded bg-success/15 px-1.5 py-0.5 text-[10px] font-medium text-success">
                      ✓ Verified
                    </span>
                  ) : (
                    <span className="ml-2 inline-flex items-center gap-1.5">
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

        {/* Sensors Tab */}
        <TabsContent value="sensors">
          <div className="space-y-4">
            <Panel title="Enrolled Network Sensors">
              <div className="space-y-4">
                <p className="text-xs text-muted-foreground">
                  Sensors deployed with your workspace token ingest genuine network telemetry from Suricata and Windows host sockets.
                </p>

                {loadingSensors ? (
                  <div className="flex h-16 items-center text-sm text-muted-foreground">
                    <Loader2 className="mr-2 size-4 animate-spin" /> Loading sensors...
                  </div>
                ) : sensorsList.length === 0 ? (
                  <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
                    No active sensors enrolled in this workspace. Enroll a sensor below to stream live telemetry.
                  </div>
                ) : (
                  <div className="divide-y rounded-lg border">
                    {sensorsList.map((s: any) => (
                      <div key={s.sensor_id} className="flex items-center justify-between p-3 text-sm">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-foreground">{s.name}</span>
                            <span className="font-mono text-xs text-muted-foreground">({s.sensor_id})</span>
                            {s.is_alive ? (
                              <span className="rounded bg-success/15 px-1.5 py-0.5 text-[10px] font-medium text-success">
                                Active / Live
                              </span>
                            ) : (
                              <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                                Offline
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Host: {s.hostname || "unknown"} · Collectors: {(s.collector_types || []).join(", ")} · Ingested: {s.total_events_ingested || 0} events
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Panel>

            <Panel title="Enroll New Network Sensor">
              {enrolledKey ? (
                <div className="space-y-3 rounded-lg border border-success/30 bg-success/5 p-4 text-sm">
                  <div className="font-semibold text-success">Sensor Enrolled Successfully!</div>
                  <p className="text-xs text-muted-foreground">
                    Copy and store this API key now. It will not be shown again:
                  </p>
                  <pre className="rounded bg-background p-2 font-mono text-xs select-all text-primary border">{enrolledKey}</pre>
                  <Button size="sm" variant="outline" onClick={() => setEnrolledKey(null)}>
                    Done
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleEnrollSensor} className="max-w-md space-y-3 text-sm">
                  <div>
                    <label className="text-xs font-medium text-muted-foreground">Sensor ID</label>
                    <Input
                      value={newSensorId}
                      onChange={(e) => setNewSensorId(e.target.value)}
                      placeholder="e.g. sensor-win-workstation-01"
                      required
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground">Friendly Name</label>
                    <Input
                      value={newSensorName}
                      onChange={(e) => setNewSensorName(e.target.value)}
                      placeholder="e.g. Primary Windows Analyst Workstation"
                      required
                    />
                  </div>
                  <Button type="submit" size="sm" disabled={enrollingSensor}>
                    {enrollingSensor && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
                    <Plus className="mr-1 size-3.5" /> Enroll Sensor
                  </Button>
                </form>
              )}
            </Panel>
          </div>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Panel title="Account & API Authentication">
            <div className="max-w-md space-y-4 text-sm">
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <div className="font-medium">Active Session Status</div>
                  <div className="text-xs text-muted-foreground">
                    {hasToken ? "JWT Token Active" : "Unauthenticated (Operating in Guest/Demo Mode)"}
                  </div>
                </div>
                {hasToken && (
                  <Button variant="outline" size="sm" onClick={handleLogout}>
                    Sign Out
                  </Button>
                )}
              </div>

              {!hasToken && (
                <form onSubmit={handleLogin} className="space-y-3 rounded-lg border p-4">
                  <div className="text-xs font-medium uppercase text-muted-foreground">Sign In to Backend</div>
                  <div>
                    <label className="text-xs text-muted-foreground">Username</label>
                    <Input
                      value={loginUser}
                      onChange={(e) => setLoginUser(e.target.value)}
                      placeholder="Username or email"
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
                  <p className="text-[11px] text-muted-foreground">
                    Default analyst: <code className="rounded bg-muted px-1">ciciliya-inace</code> / <code className="rounded bg-muted px-1">&lt;configured password&gt;</code>
                  </p>
                </form>
              )}
            </div>
          </Panel>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance">
          <Panel title="Theme">
            <div className="flex gap-2">
              {(["dark", "light", "system"] as const).map((t) => (
                <Button
                  key={t}
                  variant={theme === t ? "default" : "outline"}
                  onClick={() => setTheme(t)}
                  className="capitalize"
                >
                  {t}
                </Button>
              ))}
            </div>
          </Panel>
        </TabsContent>

        {/* Help Tab */}
        <TabsContent value="help">
          <Panel title="Help & Navigation">
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>• Press <kbd className="rounded border bg-muted px-1 font-mono text-xs">⌘K</kbd> or <kbd className="rounded border bg-muted px-1 font-mono text-xs">Ctrl+K</kbd> to search pages, alerts, and block requests.</p>
              <p>• Review and approve firewall block requests strictly from the Firewall Management tab.</p>
              <p>• Detection models and rules operate on an alert-first principle: automated blocking is disabled by default.</p>
            </div>
          </Panel>
        </TabsContent>

        {/* About Tab */}
        <TabsContent value="about">
          <Panel title="About Sentinel AI">
            <p className="text-sm text-muted-foreground">
              SentinelAI — AI-Powered Firewall Attack Detection System for Computer Networks.
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              Architecture: FastAPI Backend · Scikit-learn (Random Forest & Isolation Forest) · Suricata IDS Connector · Windows Defender Firewall Integration · React Frontend.
            </p>
          </Panel>
        </TabsContent>

        {/* Feedback Tab */}
        <TabsContent value="feedback">
          <Panel title="Submit Feedback & False Positives">
            <form onSubmit={handleSendFeedback} className="max-w-lg space-y-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground">Category</label>
                <select
                  value={fbCategory}
                  onChange={(e) => setFbCategory(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="False Positive">False Positive Report</option>
                  <option value="Rule Suggestion">Rule Suggestion</option>
                  <option value="Bug Report">System Bug Report</option>
                  <option value="Feature Request">Feature Request</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Message / Explanation</label>
                <Textarea
                  value={fbMessage}
                  onChange={(e) => setFbMessage(e.target.value)}
                  placeholder="Describe the issue, false positive event ID, or suggested rule parameter..."
                  rows={4}
                  required
                />
              </div>
              <Button type="submit" size="sm" disabled={submittingFb}>
                {submittingFb && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
                Submit Feedback
              </Button>
            </form>
          </Panel>
        </TabsContent>
      </Tabs>
    </div>
  );
}

