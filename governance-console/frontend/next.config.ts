import type { NextConfig } from "next";
import path from "path";
import { fileURLToPath } from "url";

const root = path.dirname(fileURLToPath(import.meta.url));

const wwwWorkspaceBuild = process.env.NF_WWW_WORKSPACE_BUILD === "1";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  outputFileTracingRoot: path.join(root, "../.."),
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,
  ...(wwwWorkspaceBuild
    ? {
        basePath: "/workspace",
        assetPrefix: "/workspace",
      }
    : {}),
};

export default nextConfig;
