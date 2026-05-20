/**
 * Page metadata configuration for SEO
 * Each route should have a corresponding metadata entry
 */

export const pageMetadata = {
  '/': {
    title: 'OpenWork — Decentralized Job Marketplace on Blockchain',
    description: 'Hire vetted freelancers or get paid securely with smart-contract escrow on OpenWork — the decentralized job marketplace built for global, trustless work.',
    canonical: 'https://www.openworkfyp.me/',
    ogType: 'website',
  },
  '/jobs': {
    title: 'Browse Jobs | OpenWork',
    description: 'Search freelance and full-time jobs paid in crypto with on-chain escrow. Filter by skill, budget, and chain on OpenWork.',
    canonical: 'https://www.openworkfyp.me/jobs',
    ogType: 'website',
  },
  '/about': {
    title: 'About OpenWork — Building the Future of Decentralized Work',
    description: 'Learn about OpenWork\'s mission to democratize global work through blockchain technology and smart-contract escrow.',
    canonical: 'https://www.openworkfyp.me/about',
    ogType: 'website',
  },
  '/blog': {
    title: 'Blog | OpenWork',
    description: 'Read insights on decentralized work, blockchain technology, and the future of freelancing on OpenWork.',
    canonical: 'https://www.openworkfyp.me/blog',
    ogType: 'website',
  },
  '/contact': {
    title: 'Contact Us | OpenWork',
    description: 'Get in touch with the OpenWork team. We\'re here to help with any questions about our decentralized marketplace.',
    canonical: 'https://www.openworkfyp.me/contact',
    ogType: 'website',
  },
  '/help': {
    title: 'Help & Support | OpenWork',
    description: 'Find answers to common questions about using OpenWork, escrow, payments, and smart contracts.',
    canonical: 'https://www.openworkfyp.me/help',
    ogType: 'website',
  },
  '/terms': {
    title: 'Terms of Service | OpenWork',
    description: 'Read OpenWork\'s terms of service and understand your rights and responsibilities on our marketplace.',
    canonical: 'https://www.openworkfyp.me/terms',
    ogType: 'website',
  },
  '/privacy': {
    title: 'Privacy Policy | OpenWork',
    description: 'OpenWork\'s privacy policy explains how we collect, use, and protect your personal data.',
    canonical: 'https://www.openworkfyp.me/privacy',
    ogType: 'website',
  },
  '/login': {
    title: 'Login | OpenWork',
    description: 'Sign in to your OpenWork account to manage jobs, proposals, and payments.',
    canonical: 'https://www.openworkfyp.me/login',
    ogType: 'website',
    robots: 'noindex', // Don't index auth pages
  },
  '/register': {
    title: 'Sign Up | OpenWork',
    description: 'Create a new OpenWork account and start earning or hiring on the decentralized marketplace.',
    canonical: 'https://www.openworkfyp.me/register',
    ogType: 'website',
    robots: 'noindex', // Don't index auth pages
  },
  '/dashboard': {
    title: 'Dashboard | OpenWork',
    canonical: 'https://www.openworkfyp.me/dashboard',
    ogType: 'website',
    robots: 'noindex', // Don't index user dashboard
  },
};

/**
 * Update document head metadata
 * @param {Object} metadata - Metadata object with title, description, canonical, etc.
 */
export const updatePageMetadata = (metadata) => {
  if (!metadata) return;

  // Update title
  if (metadata.title) {
    document.title = metadata.title;
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) ogTitle.setAttribute('content', metadata.title);
    const twitterTitle = document.querySelector('meta[name="twitter:title"]');
    if (twitterTitle) twitterTitle.setAttribute('content', metadata.title);
  }

  // Update description
  if (metadata.description) {
    const descMeta = document.querySelector('meta[name="description"]');
    if (descMeta) descMeta.setAttribute('content', metadata.description);
    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) ogDesc.setAttribute('content', metadata.description);
    const twitterDesc = document.querySelector('meta[name="twitter:description"]');
    if (twitterDesc) twitterDesc.setAttribute('content', metadata.description);
  }

  // Update canonical URL
  if (metadata.canonical) {
    let canonicalLink = document.querySelector('link[rel="canonical"]');
    if (!canonicalLink) {
      canonicalLink = document.createElement('link');
      canonicalLink.rel = 'canonical';
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.href = metadata.canonical;
    const ogUrl = document.querySelector('meta[property="og:url"]');
    if (ogUrl) ogUrl.setAttribute('content', metadata.canonical);
  }

  // Update OG type
  if (metadata.ogType) {
    const ogType = document.querySelector('meta[property="og:type"]');
    if (ogType) ogType.setAttribute('content', metadata.ogType);
  }

  // Update robots meta (for noindex pages like auth/dashboard)
  if (metadata.robots) {
    let robotsMeta = document.querySelector('meta[name="robots"]');
    if (!robotsMeta) {
      robotsMeta = document.createElement('meta');
      robotsMeta.name = 'robots';
      document.head.appendChild(robotsMeta);
    }
    robotsMeta.setAttribute('content', metadata.robots);
  }

  // Update OG image if provided
  if (metadata.ogImage) {
    const ogImage = document.querySelector('meta[property="og:image"]');
    if (ogImage) ogImage.setAttribute('content', metadata.ogImage);
    const twitterImage = document.querySelector('meta[name="twitter:image"]');
    if (twitterImage) twitterImage.setAttribute('content', metadata.ogImage);
  }
};
