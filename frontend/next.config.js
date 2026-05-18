/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api-proxy/:path*",
        destination: "http://34.23.97.178:8001/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
