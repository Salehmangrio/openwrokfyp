import { useEffect } from 'react';
import { pageMetadata, updatePageMetadata } from '../utils/metadata';

/**
 * Custom hook to update page metadata on route change
 * Usage: usePageMetadata('/jobs') or usePageMetadata({title: 'Custom Title', ...})
 */
export const usePageMetadata = (metadataOrPath, overrides = {}) => {
  useEffect(() => {
    let metadata = metadataOrPath;

    // If string path provided, look up from pageMetadata config
    if (typeof metadataOrPath === 'string') {
      metadata = pageMetadata[metadataOrPath];
    }

    // Merge with overrides (useful for dynamic pages like job details)
    if (metadata) {
      metadata = { ...metadata, ...overrides };
    }

    // Update document head
    if (metadata) {
      updatePageMetadata(metadata);
    }

    // Scroll to top
    window.scrollTo(0, 0);
  }, [metadataOrPath, overrides]);
};
