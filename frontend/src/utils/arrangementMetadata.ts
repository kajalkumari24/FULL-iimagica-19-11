export interface ArrangementMeta {
  id: string;
  name: string;
  category: 'columns' | 'centred' | 'profile' | 'cards' | 'stacked' | 'all';
  logoPos: string;
  profilePos: string;
  contactPos: string;
  tag: string;
  description: string;
}

export const ARRANGEMENT_METADATA: Record<string, ArrangementMeta> = {
  classic_horizontal: {
    id: 'classic_horizontal',
    name: 'Classic Horizontal',
    category: 'columns',
    logoPos: 'Left side',
    profilePos: 'Beside logo',
    contactPos: '3 Columns (Right)',
    tag: 'Balanced',
    description: 'Logo left, brand details center, contacts right'
  },
  vertical_stacked: {
    id: 'vertical_stacked',
    name: 'Vertical Stacked',
    category: 'stacked',
    logoPos: 'Top centre',
    profilePos: 'Top left',
    contactPos: 'Bottom strip',
    tag: 'Hierarchy',
    description: 'Hero logo at top, brand name below, contact details underneath'
  },
  two_column: {
    id: 'two_column',
    name: 'Two-Column',
    category: 'columns',
    logoPos: 'Top left',
    profilePos: 'Left side',
    contactPos: 'Two columns (Right)',
    tag: 'Clean Split',
    description: 'Branding on left panel, structured contact matrix on right'
  },
  three_column: {
    id: 'three_column',
    name: 'Three-Column',
    category: 'columns',
    logoPos: 'Left side',
    profilePos: 'Left column',
    contactPos: 'Three columns',
    tag: 'Standard',
    description: 'Logo/brand left, contact details center, social links & QR right'
  },
  four_column: {
    id: 'four_column',
    name: 'Four-Column',
    category: 'columns',
    logoPos: 'Top left',
    profilePos: 'Left column',
    contactPos: 'Four columns',
    tag: 'Data Dense',
    description: 'Dedicated columns for branding, phone, address, and social links'
  },
  centred: {
    id: 'centred',
    name: 'Centred Layout',
    category: 'centred',
    logoPos: 'Top centre',
    profilePos: 'Centre floating',
    contactPos: 'Centred underneath',
    tag: 'Symmetric',
    description: 'Logo & brand centered, contact details arranged below'
  },
  left_aligned_stack: {
    id: 'left_aligned_stack',
    name: 'Left-Aligned Stack',
    category: 'stacked',
    logoPos: 'Bottom left',
    profilePos: 'Left side',
    contactPos: 'Vertical list (Left)',
    tag: 'Editorial',
    description: 'All content aligned vertically along the left margin'
  },
  right_aligned_stack: {
    id: 'right_aligned_stack',
    name: 'Right-Aligned Stack',
    category: 'stacked',
    logoPos: 'Top right',
    profilePos: 'Right side',
    contactPos: 'Vertical list (Right)',
    tag: 'Modern',
    description: 'Right-aligned stack with QR and avatar on left'
  },
  logo_centre: {
    id: 'logo_centre',
    name: 'Logo-Centre Layout',
    category: 'centred',
    logoPos: 'Centre floating',
    profilePos: 'Left side',
    contactPos: 'Distributed left & right',
    tag: 'Hero Anchor',
    description: 'Hero logo in center with info distributed on both sides'
  },
  profile_focused: {
    id: 'profile_focused',
    name: 'Profile-Focused',
    category: 'profile',
    logoPos: 'Bottom right',
    profilePos: 'Overlapping footer edge',
    contactPos: 'Right panel',
    tag: 'Speaker/Host',
    description: 'Large hero profile photo with brand details & contact info'
  },
  profile_circle: {
    id: 'profile_circle',
    name: 'Profile-Circle Layout',
    category: 'profile',
    logoPos: 'Top right',
    profilePos: 'Inside circular frame',
    contactPos: 'Surrounding details',
    tag: 'Badge Avatar',
    description: 'Circular profile photo with surrounding contact information'
  },
  logo_top: {
    id: 'logo_top',
    name: 'Logo-Top Layout',
    category: 'columns',
    logoPos: 'Top left / centre',
    profilePos: 'Top right',
    contactPos: 'Two columns below',
    tag: 'Tiered',
    description: 'Logo at the top tier with two content columns below'
  },
  contact_card: {
    id: 'contact_card',
    name: 'Contact-Card Layout',
    category: 'cards',
    logoPos: 'Left side',
    profilePos: 'Left side',
    contactPos: 'Separate contact cards',
    tag: 'Modular Cards',
    description: 'Each contact detail inside its own styled card badge'
  },
  social_bottom: {
    id: 'social_bottom',
    name: 'Social-Bottom Layout',
    category: 'columns',
    logoPos: 'Top left',
    profilePos: 'Top left',
    contactPos: 'Bottom strip',
    tag: 'Social Strip',
    description: 'Brand & contacts above, social icons in a distinct bottom strip'
  },
  qr_focused: {
    id: 'qr_focused',
    name: 'QR-Focused Layout',
    category: 'cards',
    logoPos: 'Top left',
    profilePos: 'Left side',
    contactPos: 'Beside QR card',
    tag: 'Scannable',
    description: 'Prominent QR card on right with contact details beside it'
  },
  split_panel: {
    id: 'split_panel',
    name: 'Split-Panel Layout',
    category: 'cards',
    logoPos: 'Left panel',
    profilePos: 'Left panel',
    contactPos: 'Right panel',
    tag: 'Dual Tone',
    description: 'Branding in one colored panel and contacts in another'
  },
  vertical_sidebar: {
    id: 'vertical_sidebar',
    name: 'Vertical-Sidebar Layout',
    category: 'cards',
    logoPos: 'Sidebar top',
    profilePos: 'Sidebar bottom',
    contactPos: 'Main area',
    tag: 'Sidebar Strip',
    description: 'Logo & brand in vertical sidebar, contacts in main area'
  },
  floating_elements: {
    id: 'floating_elements',
    name: 'Floating-Elements Layout',
    category: 'cards',
    logoPos: 'Floating island',
    profilePos: 'Floating island',
    contactPos: 'Separate floating sections',
    tag: 'Decoupled',
    description: 'Logo, contacts, and profile arranged in separate floating cards'
  },
  asymmetric: {
    id: 'asymmetric',
    name: 'Asymmetric Layout',
    category: 'columns',
    logoPos: 'Top right',
    profilePos: 'Left side',
    contactPos: 'Unequal columns (60/40)',
    tag: 'Dynamic Ratio',
    description: 'Unequal columns with bold headline typography'
  },
  compact: {
    id: 'compact',
    name: 'Compact Layout',
    category: 'stacked',
    logoPos: 'Left side (compact)',
    profilePos: 'Left side (small)',
    contactPos: 'Single horizontal row',
    tag: 'Low Profile',
    description: 'Small logo and single-row text for limited footer space'
  },
};
