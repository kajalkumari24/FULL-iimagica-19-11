import React, { useEffect, useState } from 'react';
import { Palette, Plus, Trash2, Check, Building, Phone, Mail, Globe } from 'lucide-react';
import { useEditorStore } from '../store/editorStore';
import * as api from '../api/client';
import type { BrandProfile } from '../types';

const BrandKitPage: React.FC = () => {
  const { brand, setBrand } = useEditorStore();
  const [brands, setBrands] = useState<BrandProfile[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEdit, setCurrentEdit] = useState<BrandProfile>({ ...brand });

  useEffect(() => {
    loadBrands();
  }, []);

  const loadBrands = async () => {
    try {
      const list = await api.listBrands();
      setBrands(list);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    try {
      const saved = await api.saveBrand(currentEdit);
      setBrand(saved);
      setIsEditing(false);
      loadBrands();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this brand profile?')) {
      await api.deleteBrand(id);
      loadBrands();
    }
  };

  return (
    <div className="h-full w-full bg-slate-900 p-8 overflow-y-auto text-slate-100 select-none">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
              <Palette className="w-6 h-6 text-purple-400" /> Brand Kit Management
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Store reusable brand identities, contact details, and color palettes across all projects.
            </p>
          </div>
          <button
            onClick={() => {
              setCurrentEdit({
                id: 'brand_' + Math.random().toString(36).substring(2, 8),
                brand_name: 'New Brand',
                phone: '',
                email: '',
                website: '',
                primary_color: '#0f172a',
                secondary_color: '#3b82f6',
                accent_color: '#f59e0b',
                font_family: 'Inter',
                social_handles: {},
                logos: [],
                profiles: [],
                custom_fields: [],
              });
              setIsEditing(true);
            }}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg shadow-purple-600/20 transition"
          >
            <Plus className="w-4 h-4" /> Create Brand Profile
          </button>
        </div>

        {/* Brand Editor Form Modal / View */}
        {isEditing && (
          <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 space-y-4">
            <h3 className="font-semibold text-sm text-white">Edit Brand Details</h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Brand Name</label>
                <input
                  type="text"
                  value={currentEdit.brand_name}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, brand_name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Tagline</label>
                <input
                  type="text"
                  value={currentEdit.tagline || ''}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, tagline: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Phone</label>
                <input
                  type="text"
                  value={currentEdit.phone || ''}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, phone: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Email</label>
                <input
                  type="email"
                  value={currentEdit.email || ''}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, email: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Website</label>
                <input
                  type="text"
                  value={currentEdit.website || ''}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, website: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Primary Color</label>
                <input
                  type="color"
                  value={currentEdit.primary_color || '#0f172a'}
                  onChange={(e) => setCurrentEdit({ ...currentEdit, primary_color: e.target.value })}
                  className="w-full h-9 bg-slate-900 border border-slate-700 rounded p-1 cursor-pointer"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-1.5 bg-slate-700 rounded text-xs text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 rounded text-xs font-semibold text-white"
              >
                Save Profile
              </button>
            </div>
          </div>
        )}

        {/* Existing Brand Profiles Grid */}
        <div className="grid grid-cols-2 gap-4">
          {brands.map((b) => {
            const isActive = brand.id === b.id;
            return (
              <div
                key={b.id}
                className={`p-5 rounded-xl bg-slate-800/80 border transition flex flex-col justify-between space-y-4 ${
                  isActive ? 'border-purple-500 shadow-md shadow-purple-500/10' : 'border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <span className="font-semibold text-base text-white flex items-center gap-2">
                      <Building className="w-4 h-4 text-purple-400" /> {b.brand_name || 'Untitled Brand'}
                    </span>
                    {b.tagline && <p className="text-xs text-slate-400">{b.tagline}</p>}
                  </div>
                  {isActive && (
                    <span className="text-[10px] bg-purple-900/60 text-purple-300 border border-purple-700 px-2 py-0.5 rounded-full font-medium">
                      Active
                    </span>
                  )}
                </div>

                <div className="space-y-1 text-xs text-slate-400">
                  {b.phone && (
                    <p className="flex items-center gap-2">
                      <Phone className="w-3.5 h-3.5 text-slate-500" /> {b.phone}
                    </p>
                  )}
                  {b.email && (
                    <p className="flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-slate-500" /> {b.email}
                    </p>
                  )}
                  {b.website && (
                    <p className="flex items-center gap-2">
                      <Globe className="w-3.5 h-3.5 text-slate-500" /> {b.website}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-700/60">
                  <button
                    onClick={() => setBrand(b)}
                    className="text-xs font-semibold text-purple-400 hover:text-purple-300"
                  >
                    Select as Active
                  </button>
                  <button
                    onClick={() => b.id && handleDelete(b.id)}
                    className="p-1 text-slate-500 hover:text-rose-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default BrandKitPage;
