# SEO Pre-rendering Implementation Guide

## Overview
The site currently renders as a blank SPA shell to Google. To unlock SEO, public marketing pages must be **pre-rendered** (static HTML at build time) or **server-side rendered** (dynamic HTML per request).

**Recommended: Pre-rendering with `@vitejs/plugin-ssr`** for easy deployment to Netlify.

---

## Option 1: Pre-rendering with Vite SSR Plugin (RECOMMENDED)

### Quick Start

1. **Install the plugin:**
```bash
npm install -D @vitejs/plugin-ssr
```

2. **Update `vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { prerender } from '@vitejs/plugin-ssr'

export default defineConfig({
  plugins: [
    react(), 
    coopHeaderPlugin,
    prerender({
      routes: [
        '/',
        '/about',
        '/blog',
        '/contact',
        '/help',
        '/terms',
        '/privacy',
        '/jobs',
        '/freelancers',
      ],
      // Prerender only static/marketing pages, not user routes
      shouldPrerender: (route) => !route.includes('/dashboard') && !route.includes('/admin'),
    })
  ],
  // ... rest of config
})
```

3. **Update metadata per route** using the `usePageMetadata` hook in each page component:

**Example: `src/pages/AboutUs.jsx`**
```javascript
import { usePageMetadata } from '../hooks/usePageMetadata';

export default function AboutUs() {
  usePageMetadata('/about');
  
  return (
    <div>
      {/* About page content */}
    </div>
  );
}
```

4. **Build & deploy:**
```bash
npm run build
# This generates static .html files for each route in dist/
```

### Pros
- ✅ Simple, works perfectly with Netlify
- ✅ SEO-ready: Each route gets unique HTML with meta tags
- ✅ No server required
- ✅ Fast static hosting
- ✅ Can still fetch dynamic data (e.g., blog posts, jobs) from API after page loads

### Cons
- ❌ New pages require rebuilding & redeploying
- ❌ Can't show real-time data at build time (e.g., job count)

---

## Option 2: Server-Side Rendering (Dynamic, for dynamic content)

If you need real-time SEO (e.g., job listings that change hourly), use Node.js SSR.

### Quick Start

1. **Create `src/server.js`:**
```javascript
import express from 'express';
import { readFileSync } from 'fs';
import path from 'path';

const app = express();
const __dirname = path.dirname(new URL(import.meta.url).pathname);

// Pre-fetch job listings to inject into meta tags
async function getJobCount() {
  try {
    const response = await fetch('https://api.openworkfyp.me/jobs?limit=1');
    const data = await response.json();
    return data.total || 0;
  } catch (error) {
    return 0;
  }
}

app.get('*', async (req, res) => {
  const indexPath = path.join(__dirname, '../dist/index.html');
  let html = readFileSync(indexPath, 'utf8');

  // Inject route-specific metadata
  if (req.path === '/') {
    html = html.replace('<title>OpenWork</title>', '<title>OpenWork — Decentralized Job Marketplace</title>');
  }
  
  if (req.path === '/jobs') {
    const jobCount = await getJobCount();
    html = html.replace(
      '<meta name="description"',
      `<meta name="description" content="Browse ${jobCount} jobs paid in crypto on OpenWork"`
    );
  }

  res.send(html);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`SSR server running on port ${PORT}`));
```

2. **Deploy to Node host** (e.g., Railway, Render, Heroku) instead of Netlify static hosting.

### Pros
- ✅ Real-time SEO meta tags
- ✅ Dynamic page content at scale

### Cons
- ❌ Requires server infrastructure (costs money)
- ❌ Higher complexity
- ❌ Can't deploy to Netlify static hosting

---

## Option 3: Hybrid Approach (BEST for your use case)

**Pre-render static marketing pages, then progressively enhance with dynamic content:**

1. Pre-render: `/`, `/about`, `/blog`, `/help`, `/terms`, `/privacy`, `/contact`
2. Lazy-load dynamic listings: `/jobs`, `/freelancers`, `/offers` (render static shell + fetch data)

This gives you:
- ✅ SEO for static pages
- ✅ Dynamic job listings with API data
- ✅ No server required
- ✅ Fast static hosting on Netlify

**Setup:**
- Use Option 1 (vite-plugin-ssr)
- In `/jobs` page, render a static shell with metadata, then fetch jobs via API and update DOM
- Google will crawl the static shell; users see dynamic content

---

## Implementation Checklist

- [ ] **Pick strategy** (pre-render recommended)
- [ ] **Install plugin** (`npm install -D @vitejs/plugin-ssr`)
- [ ] **Update vite.config.js** with route list
- [ ] **Add usePageMetadata hook** to each public page
- [ ] **Test locally:** `npm run build && npm run preview`
- [ ] **Verify meta tags** with `curl http://localhost:4173/about`
- [ ] **Deploy to Netlify** (no config changes needed)
- [ ] **Test production** with Google Search Console URL Inspector
- [ ] **Submit sitemap** to Google Search Console

---

## Testing Pre-rendered Pages

```bash
# Build locally
npm run build

# Preview the built site
npm run preview
# Visit http://localhost:4173/

# Verify HTML has meta tags (not empty <div id="root">)
curl http://localhost:4173/about | head -50
```

Expected output should include:
```html
<title>About OpenWork — Building the Future of Decentralized Work</title>
<meta name="description" content="..." />
<meta property="og:url" content="https://www.openworkfyp.me/about" />
```

---

## Monitoring SEO After Deployment

1. **Submit to Google Search Console:**
   - Verify your domain
   - Submit the updated sitemap.xml
   - Use URL Inspector to test pages

2. **Monitor coverage:**
   - In GSC → Coverage, you should see 100% of your routes indexed
   - Before: 0 indexed pages (SPA problem)
   - After: All public routes indexed

3. **Wait 2-4 weeks** for full indexing and ranking

---

## Additional Quick Wins

- [ ] Create an actual 1200×630 og-image.png and upload to `/public/`
- [ ] Add `og:image:alt` tags with descriptions
- [ ] Verify `robots.txt` is served correctly: `curl https://www.openworkfyp.me/robots.txt`
- [ ] Test Twitter Card preview: https://cards-dev.twitter.com/validator
- [ ] Test Facebook preview: https://developers.facebook.com/tools/debug/
