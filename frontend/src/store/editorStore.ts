import { create } from 'zustand';
import type {
  BrandProfile,
  LogoItem,
  ProfileItem,
  CustomField,
  FooterDesign,
  PosterAnalysis,
  Project,
  FooterElement,
  LogoPalette,
} from '../types';

interface EditorState {
  currentPage: string;
  posterFile: File | null;
  posterDataUrl: string;
  posterWidth: number;
  posterHeight: number;
  brand: BrandProfile;
  logos: LogoItem[];
  profiles: ProfileItem[];
  footerVariations: FooterDesign[];
  selectedFooterIndex: number;
  activeFooter: FooterDesign | null;
  selectedElementId: string | null;
  isGenerating: boolean;
  isAnalyzing: boolean;
  isExporting: boolean;
  isExtractingColors: boolean;
  extractedPalette: LogoPalette | null;
  posterAnalysis: PosterAnalysis | null;
  projects: Project[];
  undoStack: FooterDesign[];
  redoStack: FooterDesign[];
  zoomLevel: number;

  setCurrentPage: (page: string) => void;
  setPosterFile: (file: File | null) => void;
  setPosterDataUrl: (url: string) => void;
  setPosterDimensions: (w: number, h: number) => void;
  setBrand: (brand: BrandProfile) => void;
  updateBrandField: (field: string, value: unknown) => void;
  setExtractedPalette: (p: LogoPalette | null) => void;
  setIsExtractingColors: (v: boolean) => void;
  addLogo: (logo: LogoItem) => void;
  removeLogo: (id: string) => void;
  addProfile: (profile: ProfileItem) => void;
  removeProfile: (id: string) => void;
  addCustomField: (field: CustomField) => void;
  removeCustomField: (id: string) => void;
  updateCustomField: (id: string, field: Partial<CustomField>) => void;
  setFooterVariations: (variations: FooterDesign[]) => void;
  selectFooter: (index: number) => void;
  setActiveFooter: (footer: FooterDesign | null) => void;
  updateActiveFooterElement: (elementId: string, updates: Partial<FooterElement>) => void;
  selectElement: (id: string | null) => void;
  setIsGenerating: (v: boolean) => void;
  setIsAnalyzing: (v: boolean) => void;
  setIsExporting: (v: boolean) => void;
  setPosterAnalysis: (analysis: PosterAnalysis | null) => void;
  undo: () => void;
  redo: () => void;
  pushUndo: () => void;
  setZoom: (level: number) => void;
  saveProject: (project: Project) => void;
  loadProjects: (projects: Project[]) => void;
}

const defaultBrand: BrandProfile = {
  id: 'default',
  brand_name: '',
  tagline: '',
  phone: '',
  whatsapp: '',
  email: '',
  website: '',
  address: '',
  cta: '',
  social_handles: {},
  qr_code_content: '',
  primary_color: '#1e293b',
  secondary_color: '#3b82f6',
  accent_color: '#f59e0b',
  font_family: 'Inter',
  logos: [],
  profiles: [],
  custom_fields: [],
};

export const useEditorStore = create<EditorState>((set) => ({
  currentPage: 'studio',
  posterFile: null,
  posterDataUrl: '',
  posterWidth: 1080,
  posterHeight: 1080,
  brand: { ...defaultBrand },
  logos: [],
  profiles: [],
  footerVariations: [],
  selectedFooterIndex: 0,
  activeFooter: null,
  selectedElementId: null,
  isGenerating: false,
  isAnalyzing: false,
  isExporting: false,
  isExtractingColors: false,
  extractedPalette: null,
  posterAnalysis: null,
  projects: [],
  undoStack: [],
  redoStack: [],
  zoomLevel: 1,

  setCurrentPage: (page) => set({ currentPage: page }),
  setPosterFile: (file) => set({ posterFile: file }),
  setPosterDataUrl: (url) => set({ posterDataUrl: url }),
  setPosterDimensions: (w, h) => set({ posterWidth: w, posterHeight: h }),
  setBrand: (brand) => set({ brand }),
  updateBrandField: (field, value) =>
    set((state) => ({ brand: { ...state.brand, [field]: value } })),
  setExtractedPalette: (p) => set({ extractedPalette: p }),
  setIsExtractingColors: (v) => set({ isExtractingColors: v }),
  addLogo: (logo) =>
    set((state) => {
      const logos = [...state.logos, logo];
      return { logos, brand: { ...state.brand, logos } };
    }),
  removeLogo: (id) =>
    set((state) => {
      const logos = state.logos.filter((l) => l.id !== id);
      return { logos, brand: { ...state.brand, logos } };
    }),
  addProfile: (profile) =>
    set((state) => {
      const profiles = [...state.profiles, profile];
      return { profiles, brand: { ...state.brand, profiles } };
    }),
  removeProfile: (id) =>
    set((state) => {
      const profiles = state.profiles.filter((p) => p.id !== id);
      return { profiles, brand: { ...state.brand, profiles } };
    }),
  addCustomField: (field) =>
    set((state) => {
      const custom_fields = [...state.brand.custom_fields, field];
      return { brand: { ...state.brand, custom_fields } };
    }),
  removeCustomField: (id) =>
    set((state) => {
      const custom_fields = state.brand.custom_fields.filter((f) => f.id !== id);
      return { brand: { ...state.brand, custom_fields } };
    }),
  updateCustomField: (id, updates) =>
    set((state) => {
      const custom_fields = state.brand.custom_fields.map((f) =>
        f.id === id ? { ...f, ...updates } : f
      );
      return { brand: { ...state.brand, custom_fields } };
    }),
  setFooterVariations: (variations) => set({ footerVariations: variations }),
  selectFooter: (index) =>
    set((state) => ({
      selectedFooterIndex: index,
      activeFooter: state.footerVariations[index] ?? null,
      selectedElementId: null,
    })),
  setActiveFooter: (footer) => set({ activeFooter: footer }),
  updateActiveFooterElement: (elementId, updates) =>
    set((state) => {
      if (!state.activeFooter) return {};
      const elements = state.activeFooter.elements.map((el) =>
        el.id === elementId ? { ...el, ...updates } : el
      );
      return { activeFooter: { ...state.activeFooter, elements } };
    }),
  selectElement: (id) => set({ selectedElementId: id }),
  setIsGenerating: (v) => set({ isGenerating: v }),
  setIsAnalyzing: (v) => set({ isAnalyzing: v }),
  setIsExporting: (v) => set({ isExporting: v }),
  setPosterAnalysis: (analysis) => set({ posterAnalysis: analysis }),
  undo: () =>
    set((state) => {
      if (state.undoStack.length === 0) return {};
      const prev = state.undoStack[state.undoStack.length - 1];
      return {
        undoStack: state.undoStack.slice(0, -1),
        redoStack: state.activeFooter
          ? [...state.redoStack, state.activeFooter]
          : state.redoStack,
        activeFooter: prev,
      };
    }),
  redo: () =>
    set((state) => {
      if (state.redoStack.length === 0) return {};
      const next = state.redoStack[state.redoStack.length - 1];
      return {
        redoStack: state.redoStack.slice(0, -1),
        undoStack: state.activeFooter
          ? [...state.undoStack, state.activeFooter]
          : state.undoStack,
        activeFooter: next,
      };
    }),
  pushUndo: () =>
    set((state) => ({
      undoStack: state.activeFooter
        ? [...state.undoStack.slice(-19), state.activeFooter]
        : state.undoStack,
      redoStack: [],
    })),
  setZoom: (level) => set({ zoomLevel: Math.max(0.1, Math.min(3, level)) }),
  saveProject: (project) =>
    set((state) => {
      const existing = state.projects.findIndex((p) => p.id === project.id);
      if (existing >= 0) {
        const projects = [...state.projects];
        projects[existing] = project;
        return { projects };
      }
      return { projects: [...state.projects, project] };
    }),
  loadProjects: (projects) => set({ projects }),
}));

if (typeof window !== 'undefined') {
  (window as any).useEditorStore = useEditorStore;
}
