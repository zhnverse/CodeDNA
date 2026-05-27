export { default } from "next-auth/middleware";

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/genome",
    "/projects/:path*",
    "/growth/:path*",
    "/settings/:path*",
    "/analysis/:path*",
  ],
};
