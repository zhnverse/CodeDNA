"use client";

import { useState } from "react";
import { Session } from "next-auth";
import { signOut } from "next-auth/react";
import {
  Github,
  CheckCircle,
  User,
  Settings2,
  AlertTriangle,
  Save,
  Trash2,
  Unlink,
  Code2,
  Check,
  Copy,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface Props {
  session: Session;
}

export function SettingsClient({ session }: Props) {
  const [bio, setBio] = useState("");
  const [email, setEmail] = useState(session.user.email ?? "");
  const [includePrivate, setIncludePrivate] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const username = session.user.username ?? "";
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "https://codedna.dev";

  const snippets = {
    iframe: `<iframe\n  src="${baseUrl}/api/widget/${username}"\n  width="400"\n  height="320"\n  frameborder="0"\n  style="border-radius:16px"\n/>`,
    markdown: `[![CodeDNA](${baseUrl}/api/widget/${username})](${baseUrl}/genome/${username})`,
    link: `${baseUrl}/genome/${username}`,
  };

  function copySnippet(key: keyof typeof snippets) {
    navigator.clipboard.writeText(snippets[key]).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    });
  }

  const handleSave = async () => {
    setSaving(true);
    await new Promise((r) => setTimeout(r, 800));
    setSaving(false);
  };

  return (
    <div className="container py-10 max-w-3xl space-y-8">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account and analysis preferences.</p>
      </div>

      {/* Connected accounts */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Github className="h-5 w-5" />
            Connected Accounts
          </CardTitle>
          <CardDescription>Manage your linked OAuth providers.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 rounded-lg border border-border/60 bg-muted/20">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-foreground/10 flex items-center justify-center">
                <Github className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium">GitHub</p>
                  <Badge variant="dna" className="text-xs">Connected</Badge>
                </div>
                <p className="text-sm text-muted-foreground">@{session.user.username}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-dna-green">
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm font-medium">Active</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <User className="h-5 w-5" />
            Profile
          </CardTitle>
          <CardDescription>Update your public profile information.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={session.user.avatar || session.user.image || ""} />
              <AvatarFallback className="bg-dna-green/20 text-dna-green text-lg">
                {session.user.username?.[0]?.toUpperCase() ?? "U"}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold text-lg">{session.user.username}</p>
              <p className="text-sm text-muted-foreground">Avatar synced from GitHub</p>
            </div>
          </div>

          <div className="grid gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Tell the world about your coding journey..."
                rows={3}
              />
            </div>
          </div>

          <Button onClick={handleSave} disabled={saving} className="gap-2">
            <Save className="h-4 w-4" />
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis preferences */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Settings2 className="h-5 w-5" />
            Analysis Preferences
          </CardTitle>
          <CardDescription>Control how CodeDNA analyzes your repositories.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Include private repositories</Label>
              <p className="text-sm text-muted-foreground">
                Analyze private repos in addition to public ones.
              </p>
            </div>
            <Switch
              checked={includePrivate}
              onCheckedChange={setIncludePrivate}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-sync on push</Label>
              <p className="text-sm text-muted-foreground">
                Automatically re-analyze repos when you push new commits.
              </p>
            </div>
            <Switch checked={autoSync} onCheckedChange={setAutoSync} />
          </div>

          <Separator />

          <div className="space-y-3">
            <Label>Excluded repositories</Label>
            <p className="text-sm text-muted-foreground">
              Repos listed here will be skipped during analysis.
            </p>
            <div className="p-4 rounded-lg border border-dashed border-border/60 text-center text-sm text-muted-foreground">
              No repositories excluded. Import repos first to manage exclusions.
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Embed & Share */}
      <Card className="bg-card/50 border-border/60">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Code2 className="h-5 w-5" />
            Share Your Genome
          </CardTitle>
          <CardDescription>Embed your developer profile anywhere — GitHub README, portfolio, or blog.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {[
            { key: "iframe" as const, label: "Embed (iframe)", desc: "Drop into any HTML page" },
            { key: "markdown" as const, label: "Markdown badge", desc: "For GitHub READMEs" },
            { key: "link" as const, label: "Profile URL", desc: "Direct link to your public genome" },
          ].map(({ key, label, desc }) => (
            <div key={key} className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <Label>{label}</Label>
                  <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-8 gap-1.5 text-xs shrink-0 ml-4"
                  onClick={() => copySnippet(key)}
                >
                  {copied === key ? <><Check className="h-3 w-3 text-dna-green" />Copied!</> : <><Copy className="h-3 w-3" />Copy</>}
                </Button>
              </div>
              <pre className="p-3 rounded-lg bg-muted/30 text-xs font-mono overflow-x-auto border border-border/40 text-muted-foreground whitespace-pre-wrap break-all">
                {snippets[key]}
              </pre>
            </div>
          ))}

          {/* Live preview */}
          <div className="space-y-2">
            <Label>Live widget preview</Label>
            <div className="rounded-xl overflow-hidden border border-border/40 w-fit">
              <img
                src={`/api/widget/${username}`}
                alt="CodeDNA widget preview"
                width={400}
                height={320}
                style={{ display: "block" }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Card className="bg-card/50 border-destructive/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>Irreversible actions. Proceed with caution.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-lg border border-border/60">
            <div>
              <p className="font-medium">Disconnect GitHub</p>
              <p className="text-sm text-muted-foreground">
                Removes GitHub access. Your data is preserved.
              </p>
            </div>
            <Button variant="outline" size="sm" className="gap-2 border-destructive/40 text-destructive hover:bg-destructive/10">
              <Unlink className="h-4 w-4" />
              Disconnect
            </Button>
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg border border-destructive/20 bg-destructive/5">
            <div>
              <p className="font-medium">Delete Account</p>
              <p className="text-sm text-muted-foreground">
                Permanently deletes your account and all genome data.
              </p>
            </div>
            <Button
              variant="destructive"
              size="sm"
              className="gap-2"
              onClick={() => {
                if (confirm("Are you sure? This cannot be undone.")) {
                  signOut({ callbackUrl: "/" });
                }
              }}
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
