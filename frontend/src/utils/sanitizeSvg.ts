/**
 * Client-side SVG Sanitizer to prevent XSS and unsafe DOM injection.
 * Strips script tags, foreignObjects, event handlers, and javascript: protocols.
 */
export function sanitizeSvg(rawSvg: string): string {
  if (!rawSvg || typeof rawSvg !== 'string') return '';

  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(rawSvg, 'image/svg+xml');

    // Check for parser errors
    const parserError = doc.querySelector('parsererror');
    if (parserError) {
      console.warn('SVG parse warning:', parserError.textContent);
      return '';
    }

    const svgElement = doc.documentElement;
    if (!svgElement || svgElement.nodeName.toLowerCase() !== 'svg') {
      return '';
    }

    // List of banned tags
    const bannedTags = ['script', 'foreignobject', 'object', 'embed', 'iframe', 'meta', 'link'];
    bannedTags.forEach((tagName) => {
      const elements = doc.querySelectorAll(tagName);
      elements.forEach((el) => el.remove());
    });

    // Clean attributes on all elements
    const allElements = doc.querySelectorAll('*');
    allElements.forEach((el) => {
      const attrs = Array.from(el.attributes);
      attrs.forEach((attr) => {
        const name = attr.name.toLowerCase();
        const value = attr.value.trim().toLowerCase();

        // Remove any inline event handler (onload, onclick, onerror, etc.)
        if (name.startsWith('on')) {
          el.removeAttribute(attr.name);
        }

        // Remove dangerous URI protocols
        if (
          (name === 'href' || name === 'xlink:href' || name === 'src') &&
          (value.startsWith('javascript:') || value.startsWith('vbscript:') || value.startsWith('data:text/html'))
        ) {
          el.removeAttribute(attr.name);
        }
      });
    });

    return new XMLSerializer().serializeToString(svgElement);
  } catch (err) {
    console.error('SVG sanitization error:', err);
    return '';
  }
}
