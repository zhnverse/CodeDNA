import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

export async function getApiUser(req: NextRequest) {
  const token = await getToken({ req });
  if (!token?.userId) return null;
  return {
    userId: token.userId as string,
    accessToken: (token.accessToken as string | undefined) ?? "",
  };
}
