import { NextAuthOptions } from "next-auth";
import GithubProvider from "next-auth/providers/github";
import { prisma } from "./prisma";

export const authOptions: NextAuthOptions = {
  debug: true,
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: { scope: "read:user user:email repo" },
      },
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider !== "github" || !profile) return false;

      const githubProfile = profile as {
        id: number;
        login: string;
        avatar_url: string;
        bio?: string;
        email?: string;
      };

      try {
        await prisma.user.upsert({
          where: { githubId: String(githubProfile.id) },
          update: {
            username: githubProfile.login,
            avatar: githubProfile.avatar_url,
            bio: githubProfile.bio ?? null,
            email: githubProfile.email ?? user.email ?? null,
          },
          create: {
            githubId: String(githubProfile.id),
            username: githubProfile.login,
            avatar: githubProfile.avatar_url,
            bio: githubProfile.bio ?? null,
            email: githubProfile.email ?? user.email ?? null,
          },
        });
      } catch (err) {
        console.error("[auth] signIn DB error:", err);
        return false;
      }

      return true;
    },
    async jwt({ token, account, profile }) {
      if (account?.provider === "github" && profile) {
        const githubProfile = profile as { id: number; login: string; avatar_url: string };
        try {
          const dbUser = await prisma.user.findUnique({
            where: { githubId: String(githubProfile.id) },
          });
          if (dbUser) {
            token.userId = dbUser.id;
            token.username = dbUser.username;
            token.avatar = dbUser.avatar ?? undefined;
          }
        } catch (err) {
          console.error("[auth] jwt DB error:", err);
          // fall back to GitHub profile data so login still works
          token.username = githubProfile.login;
          token.avatar = githubProfile.avatar_url;
        }
        if (account.access_token) token.accessToken = account.access_token;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.userId = token.userId as string;
        session.user.username = token.username as string;
        session.user.avatar = token.avatar as string;
        session.user.accessToken = token.accessToken as string;
      }
      return session;
    },
  },
  pages: { signIn: "/" },
};
