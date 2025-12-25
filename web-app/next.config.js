/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // For GitHub Pages - set your repo name here
  basePath: process.env.NODE_ENV === 'production' ? '/adventures-in-space' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/adventures-in-space/' : '',
  
  // Next.js 15 - disable React strict mode double rendering in dev if needed
  reactStrictMode: true,
};

module.exports = nextConfig;
