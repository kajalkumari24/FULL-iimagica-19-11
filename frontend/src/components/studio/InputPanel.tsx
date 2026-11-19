import React, { useRef, useState } from 'react';
import {
  Upload,
  Image as ImageIcon,
  User,
  Building,
  Plus,
  Trash2,
  Sparkles,
  RefreshCw,
  Palette,
  QrCode,
  Link,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import * as api from '../../api/client';
import type { CustomField, LogoItem, ProfileItem } from '../../types';

export const InputPanel: React.FC = () => {
  const {
    posterFile,
    posterDataUrl,
    posterWidth,
    posterHeight,
    brand,
    logos,
    profiles,
    isGenerating,
    isAnalyzing,
    posterAnalysis,
    setPosterFile,
    setPosterDataUrl,
    setPosterDimensions,
    updateBrandField,
    addLogo,
    removeLogo,
    addProfile,
    removeProfile,
    addCustomField,
    removeCustomField,
    updateCustomField,
    activeFooter,
    setActiveFooter,
    setExtractedPalette,
    setIsExtractingColors,
    setFooterVariations,
    selectFooter,
    setIsGenerating,
    setIsAnalyzing,
    setPosterAnalysis,
  } = useEditorStore();

  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    poster: true,
    logo: true,
    profile: true,
    brand: true,
    colors: false,
    custom: false,
  });

  const [footerRatio, setFooterRatio] = useState<number>(0.12);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedArrangement, setSelectedArrangement] = useState<string>('all');

  const posterInputRef = useRef<HTMLInputElement>(null);
  const logoInputRef = useRef<HTMLInputElement>(null);
  const profileInputRef = useRef<HTMLInputElement>(null);

  const toggleSection = (sec: string) => {
    setExpandedSections((prev) => ({ ...prev, [sec]: !prev[sec] }));
  };

  // 1. Poster upload handler
  const handlePosterUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPosterFile(file);
    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target?.result as string;
      setPosterDataUrl(dataUrl);

      // Detect original dimensions
      const img = new Image();
      img.onload = () => {
        setPosterDimensions(img.naturalWidth || 1080, img.naturalHeight || 1080);
      };
      img.src = dataUrl;
    };
    reader.readAsDataURL(file);
  };

  // 2. Logo upload handler
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const url = event.target?.result as string;
        const img = new Image();
        img.onload = async () => {
          const aspect = img.naturalWidth / (img.naturalHeight || 1);
          const logoItem: LogoItem = {
            id: 'logo_' + Math.random().toString(36).substring(2, 8),
            name: file.name,
            url,
            width: img.naturalWidth,
            height: img.naturalHeight,
            aspect_ratio: aspect,
          };
          addLogo(logoItem);

          // Extract logo brand colors automatically
          try {
            setIsExtractingColors(true);
            const palette = await api.extractLogoColors(url);
            setExtractedPalette(palette);
            updateBrandField('primary_color', palette.primary);
            updateBrandField('secondary_color', palette.secondary);
            updateBrandField('accent_color', palette.accent);

            // Automatically apply matching theme to active footer if loaded
            if (activeFooter && palette.schemes.length > 0) {
              const updatedFooter = await api.applyLogoColors(activeFooter, palette.schemes[0]);
              setActiveFooter(updatedFooter);
            }
          } catch (err) {
            console.warn('Auto logo color extraction failed:', err);
          } finally {
            setIsExtractingColors(false);
          }
        };
        img.src = url;
      };
      reader.readAsDataURL(file);
    });
  };

  // 3. Profile photo upload handler
  const handleProfileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const url = event.target?.result as string;
      const profileItem: ProfileItem = {
        id: 'prof_' + Math.random().toString(36).substring(2, 8),
        name: file.name,
        url,
        frame_style: 'circle',
      };
      addProfile(profileItem);
    };
    reader.readAsDataURL(file);
  };

  // 4. Custom field add
  const handleAddCustomField = () => {
    const newField: CustomField = {
      id: 'cf_' + Math.random().toString(36).substring(2, 8),
      label: 'New Field',
      value: '',
      icon: 'info',
      order: brand.custom_fields.length,
      visible: true,
    };
    addCustomField(newField);
  };

  // 5. Generate Footers Action
  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      let analysisPalette: string[] | undefined = undefined;

      // Analyze poster if file uploaded
      if (posterFile) {
        setIsAnalyzing(true);
        try {
          const analysis = await api.analyzePoster(posterFile);
          setPosterAnalysis(analysis);
          analysisPalette = analysis.suggested_footer_palette;
        } catch (err) {
          console.warn('Poster analysis fallback:', err);
        } finally {
          setIsAnalyzing(false);
        }
      }

      // Generate variations
      const variations = await api.generateFooters({
        poster_width: posterWidth,
        poster_height: posterHeight,
        brand,
        style_preference: selectedCategory,
        arrangement_preference: selectedArrangement,
        custom_colors: analysisPalette,
        target_footer_height_ratio: footerRatio,
      });

      setFooterVariations(variations);
      if (variations.length > 0) {
        selectFooter(0);
      }
    } catch (err) {
      console.error('Failed to generate footer designs:', err);
      alert('Could not generate footers. Please verify backend is running on port 8000.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-80 h-full bg-slate-800 border-r border-slate-700 flex flex-col text-slate-200 select-none overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <h2 className="font-semibold text-sm tracking-wide text-white uppercase flex items-center gap-2">
          <Building className="w-4 h-4 text-indigo-400" /> Inputs & Branding
        </h2>
        {posterWidth > 0 && (
          <span className="text-[11px] font-mono px-2 py-0.5 bg-slate-900 rounded text-slate-400 border border-slate-700">
            {posterWidth} × {posterHeight}
          </span>
        )}
      </div>

      {/* Scrollable form controls */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {/* A. Poster Upload */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('poster')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-indigo-400" /> Upload Poster
            </span>
            {expandedSections.poster ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.poster && (
            <div className="p-3 space-y-3">
              {posterDataUrl ? (
                <div className="relative group rounded-md overflow-hidden border border-slate-600 bg-slate-900">
                  <img src={posterDataUrl} alt="Poster" className="w-full h-32 object-contain" />
                  <div className="absolute inset-0 bg-slate-900/70 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                    <button
                      onClick={() => posterInputRef.current?.click()}
                      className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded text-xs text-white"
                    >
                      Replace
                    </button>
                    <button
                      onClick={() => {
                        setPosterFile(null);
                        setPosterDataUrl('');
                      }}
                      className="px-2 py-1 bg-rose-600 hover:bg-rose-500 rounded text-xs text-white"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ) : (
                <div
                  onClick={() => posterInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-600 hover:border-indigo-500 rounded-lg p-5 text-center cursor-pointer transition bg-slate-900/40"
                >
                  <Upload className="w-6 h-6 mx-auto text-slate-400 mb-2" />
                  <p className="text-xs text-slate-300 font-medium">Click to upload poster</p>
                  <p className="text-[10px] text-slate-500 mt-1">PNG, JPG, or WebP</p>
                </div>
              )}
              {posterAnalysis && (
                <div className="p-2.5 bg-slate-900/90 rounded border border-slate-700/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-slate-300">Safe Zone Estimation</span>
                    <span className="text-[9px] bg-indigo-950 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-800">
                      Heuristic CV
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 leading-relaxed">
                    Visual edge density & gradient uniformity (heuristic estimate, no face/OCR). Estimated safe height: {Math.round(posterAnalysis.detected_empty_bottom_space || (posterHeight * (posterAnalysis.safe_zone?.suggested_footer_height_ratio || 0.12)))}px.
                  </p>
                  <div className="pt-1">
                    <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                      <span>Manual Footer Height Ratio</span>
                      <span className="font-mono text-indigo-400 font-semibold">{Math.round(footerRatio * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0.08"
                      max="0.25"
                      step="0.01"
                      value={footerRatio}
                      onChange={(e) => setFooterRatio(parseFloat(e.target.value))}
                      className="w-full accent-indigo-500 cursor-pointer"
                    />
                  </div>
                </div>
              )}
              <input ref={posterInputRef} type="file" accept="image/*" className="hidden" onChange={handlePosterUpload} />
            </div>
          )}
        </div>

        {/* B. Logo Upload */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('logo')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" /> Brand Logos ({logos.length})
            </span>
            {expandedSections.logo ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.logo && (
            <div className="p-3 space-y-2">
              <div className="grid grid-cols-2 gap-2">
                {logos.map((logo) => (
                  <div key={logo.id} className="relative group border border-slate-700 rounded p-1 bg-slate-900/60">
                    <img src={logo.url} alt={logo.name} className="h-12 w-full object-contain" />
                    <button
                      onClick={() => removeLogo(logo.id)}
                      className="absolute top-1 right-1 p-1 bg-rose-600/80 hover:bg-rose-600 rounded text-white opacity-0 group-hover:opacity-100 transition"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={() => logoInputRef.current?.click()}
                className="w-full py-1.5 border border-slate-600 hover:border-slate-500 rounded text-xs text-slate-300 flex items-center justify-center gap-1.5 hover:bg-slate-700/50 transition"
              >
                <Plus className="w-3.5 h-3.5" /> Add Logo
              </button>
              <input ref={logoInputRef} type="file" accept="image/*" multiple className="hidden" onChange={handleLogoUpload} />
            </div>
          )}
        </div>

        {/* C. Profile Photo */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('profile')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <User className="w-4 h-4 text-sky-400" /> Profile Photo ({profiles.length})
            </span>
            {expandedSections.profile ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.profile && (
            <div className="p-3 space-y-2">
              {profiles.length > 0 ? (
                profiles.map((prof) => (
                  <div key={prof.id} className="flex items-center gap-3 p-2 bg-slate-900 rounded border border-slate-700">
                    <img src={prof.url} alt="Profile" className="w-10 h-10 rounded-full object-cover border border-slate-600" />
                    <div className="flex-1">
                      <select
                        value={prof.frame_style}
                        onChange={(e) => {
                          const updated = { ...prof, frame_style: e.target.value };
                          removeProfile(prof.id);
                          addProfile(updated);
                        }}
                        className="bg-slate-800 border border-slate-700 text-xs rounded px-2 py-1 text-slate-300 w-full"
                      >
                        <option value="circle">Circle Frame</option>
                        <option value="rounded">Rounded Frame</option>
                        <option value="arch">Arch Frame</option>
                        <option value="square">Square Frame</option>
                      </select>
                    </div>
                    <button
                      onClick={() => removeProfile(prof.id)}
                      className="text-slate-400 hover:text-rose-400 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              ) : (
                <button
                  onClick={() => profileInputRef.current?.click()}
                  className="w-full py-2 border border-dashed border-slate-600 hover:border-sky-400 rounded text-xs text-slate-300 flex items-center justify-center gap-1.5 transition"
                >
                  <Upload className="w-3.5 h-3.5" /> Upload Person Photo
                </button>
              )}
              <input ref={profileInputRef} type="file" accept="image/*" className="hidden" onChange={handleProfileUpload} />
            </div>
          )}
        </div>

        {/* D. Brand Details */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('brand')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <Building className="w-4 h-4 text-emerald-400" /> Brand Information
            </span>
            {expandedSections.brand ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.brand && (
            <div className="p-3 space-y-2.5 text-xs">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Brand Name</label>
                <input
                  type="text"
                  value={brand.brand_name}
                  onChange={(e) => updateBrandField('brand_name', e.target.value)}
                  placeholder="e.g. Apex Sound Studio"
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Tagline</label>
                <input
                  type="text"
                  value={brand.tagline || ''}
                  onChange={(e) => updateBrandField('tagline', e.target.value)}
                  placeholder="e.g. Audio Engineering & Production"
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Phone</label>
                  <input
                    type="text"
                    value={brand.phone || ''}
                    onChange={(e) => updateBrandField('phone', e.target.value)}
                    placeholder="+1 555-0192"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">WhatsApp</label>
                  <input
                    type="text"
                    value={brand.whatsapp || ''}
                    onChange={(e) => updateBrandField('whatsapp', e.target.value)}
                    placeholder="+1 555-0192"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-slate-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Email</label>
                  <input
                    type="email"
                    value={brand.email || ''}
                    onChange={(e) => updateBrandField('email', e.target.value)}
                    placeholder="contact@apex.com"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Website</label>
                  <input
                    type="text"
                    value={brand.website || ''}
                    onChange={(e) => updateBrandField('website', e.target.value)}
                    placeholder="www.apex.com"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-slate-100"
                  />
                </div>
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Address / Location</label>
                <input
                  type="text"
                  value={brand.address || ''}
                  onChange={(e) => updateBrandField('address', e.target.value)}
                  placeholder="100 Main Blvd, Suite 400"
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Call to Action (CTA)</label>
                <input
                  type="text"
                  value={brand.cta || ''}
                  onChange={(e) => updateBrandField('cta', e.target.value)}
                  placeholder="e.g. Book Your Session"
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1 flex items-center gap-1.5">
                  <QrCode className="w-3.5 h-3.5 text-indigo-400" /> QR Code URL / Text
                </label>
                <input
                  type="text"
                  value={brand.qr_code_content || ''}
                  onChange={(e) => updateBrandField('qr_code_content', e.target.value)}
                  placeholder="https://apex.com/register"
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100"
                />
              </div>
              <div className="pt-1 border-t border-slate-700/60">
                <label className="text-[11px] font-semibold text-slate-300 block mb-1.5">Social Media Handles</label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-0.5">LinkedIn</label>
                    <input
                      type="text"
                      value={brand.social_handles?.linkedin || ''}
                      onChange={(e) =>
                        updateBrandField('social_handles', {
                          ...(brand.social_handles || {}),
                          linkedin: e.target.value,
                        })
                      }
                      placeholder="acme-corp"
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-0.5">Twitter / X</label>
                    <input
                      type="text"
                      value={brand.social_handles?.twitter || ''}
                      onChange={(e) =>
                        updateBrandField('social_handles', {
                          ...(brand.social_handles || {}),
                          twitter: e.target.value,
                        })
                      }
                      placeholder="@acme"
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-0.5">Instagram</label>
                    <input
                      type="text"
                      value={brand.social_handles?.instagram || ''}
                      onChange={(e) =>
                        updateBrandField('social_handles', {
                          ...(brand.social_handles || {}),
                          instagram: e.target.value,
                        })
                      }
                      placeholder="@acme_official"
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-0.5">Facebook</label>
                    <input
                      type="text"
                      value={brand.social_handles?.facebook || ''}
                      onChange={(e) =>
                        updateBrandField('social_handles', {
                          ...(brand.social_handles || {}),
                          facebook: e.target.value,
                        })
                      }
                      placeholder="fb/acme"
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* E. Brand Colors */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('colors')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <Palette className="w-4 h-4 text-purple-400" /> Palette & Theme
            </span>
            {expandedSections.colors ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.colors && (
            <div className="p-3 grid grid-cols-3 gap-2">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Primary</label>
                <input
                  type="color"
                  value={brand.primary_color || '#0f172a'}
                  onChange={(e) => updateBrandField('primary_color', e.target.value)}
                  className="w-full h-8 rounded border border-slate-700 cursor-pointer bg-slate-900"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Secondary</label>
                <input
                  type="color"
                  value={brand.secondary_color || '#3b82f6'}
                  onChange={(e) => updateBrandField('secondary_color', e.target.value)}
                  className="w-full h-8 rounded border border-slate-700 cursor-pointer bg-slate-900"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Accent</label>
                <input
                  type="color"
                  value={brand.accent_color || '#f59e0b'}
                  onChange={(e) => updateBrandField('accent_color', e.target.value)}
                  className="w-full h-8 rounded border border-slate-700 cursor-pointer bg-slate-900"
                />
              </div>
            </div>
          )}
        </div>

        {/* F. Custom Fields */}
        <div className="border border-slate-700 rounded-lg overflow-hidden bg-slate-800/80">
          <button
            onClick={() => toggleSection('custom')}
            className="w-full px-3 py-2.5 bg-slate-700/50 flex items-center justify-between text-xs font-semibold hover:bg-slate-700 transition"
          >
            <span className="flex items-center gap-2">
              <Link className="w-4 h-4 text-cyan-400" /> Custom Fields ({brand.custom_fields.length})
            </span>
            {expandedSections.custom ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          {expandedSections.custom && (
            <div className="p-3 space-y-2">
              {brand.custom_fields.map((cf) => (
                <div key={cf.id} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={cf.label}
                    onChange={(e) => updateCustomField(cf.id, { label: e.target.value })}
                    placeholder="Label"
                    className="w-24 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
                  />
                  <input
                    type="text"
                    value={cf.value}
                    onChange={(e) => updateCustomField(cf.id, { value: e.target.value })}
                    placeholder="Value"
                    className="flex-1 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
                  />
                  <button onClick={() => removeCustomField(cf.id)} className="text-slate-400 hover:text-rose-400">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
              <button
                onClick={handleAddCustomField}
                className="w-full py-1.5 border border-dashed border-slate-700 hover:border-slate-500 rounded text-xs text-slate-400 flex items-center justify-center gap-1.5 transition"
              >
                <Plus className="w-3 h-3" /> Add Custom Field
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="p-4 border-t border-slate-700 bg-slate-800/90 space-y-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">Style Filter:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-indigo-300 font-medium focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Styles (48 Designs)</option>
            <option value="wave">Wave Styles (10)</option>
            <option value="curved">Curved Styles (7)</option>
            <option value="modern">Modern Styles (13)</option>
            <option value="geometric">Geometric Styles (3)</option>
            <option value="minimal">Minimal Styles (4)</option>
            <option value="corporate">Corporate Styles (2)</option>
          </select>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">Arrangement:</span>
          <select
            value={selectedArrangement}
            onChange={(e) => setSelectedArrangement(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-cyan-300 font-medium focus:outline-none focus:border-cyan-500 cursor-pointer max-w-[170px]"
          >
            <option value="all">All Arrangements (20)</option>
            <option value="classic_horizontal">Classic Horizontal</option>
            <option value="vertical_stacked">Vertical Stacked</option>
            <option value="two_column">Two-Column</option>
            <option value="three_column">Three-Column</option>
            <option value="four_column">Four-Column</option>
            <option value="centred">Centred</option>
            <option value="left_aligned_stack">Left-Aligned Stack</option>
            <option value="right_aligned_stack">Right-Aligned Stack</option>
            <option value="logo_centre">Logo-Centre</option>
            <option value="profile_focused">Profile-Focused</option>
            <option value="profile_circle">Profile-Circle</option>
            <option value="logo_top">Logo-Top</option>
            <option value="contact_card">Contact-Card</option>
            <option value="social_bottom">Social-Bottom</option>
            <option value="qr_focused">QR-Focused</option>
            <option value="split_panel">Split-Panel</option>
            <option value="vertical_sidebar">Vertical-Sidebar</option>
            <option value="floating_elements">Floating-Elements</option>
            <option value="asymmetric">Asymmetric</option>
            <option value="compact">Compact</option>
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || isAnalyzing}
          className="w-full py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-50 text-white font-semibold rounded-lg shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition"
        >
          {isGenerating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" /> Generating Layouts...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" /> Generate Footers
            </>
          )}
        </button>
      </div>
    </div>
  );
};
