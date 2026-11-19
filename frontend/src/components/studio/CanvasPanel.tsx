import React, { useRef, useState, useEffect } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Layers,
  Trash2,
  Lock,
  Unlock,
  ArrowUp,
  ArrowDown,
  RotateCcw,
  RotateCw,
  Edit3,
  Eye,
} from 'lucide-react';
import { fabric } from 'fabric';
import { useEditorStore } from '../../store/editorStore';
import { sanitizeSvg } from '../../utils/sanitizeSvg';

export const CanvasPanel: React.FC = () => {
  const {
    posterDataUrl,
    posterWidth,
    posterHeight,
    activeFooter,
    selectedElementId,
    zoomLevel,
    undoStack,
    redoStack,
    setZoom,
    selectElement,
    updateActiveFooterElement,
    undo,
    redo,
    pushUndo,
  } = useEditorStore();

  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [mode, setMode] = useState<'fabric' | 'vector'>('fabric');
  const [isLocked, setIsLocked] = useState(false);
  const startPanRef = useRef({ x: 0, y: 0 });

  const canvasElRef = useRef<HTMLCanvasElement | null>(null);
  const fabricCanvasRef = useRef<any>(null);
  const isUpdatingFabricRef = useRef(false);

  // Initialize Fabric Canvas
  useEffect(() => {
    if (!canvasElRef.current) return;

    const c = new fabric.Canvas(canvasElRef.current, {
      width: posterWidth,
      height: posterHeight,
      selection: true,
      preserveObjectStacking: true,
      backgroundColor: '#0f172a',
    });

    fabricCanvasRef.current = c;

    // Selection event
    c.on('selection:created', (e: any) => {
      const active = e.selected?.[0];
      if (active && (active as any).customId) {
        selectElement((active as any).customId);
      }
    });

    c.on('selection:updated', (e: any) => {
      const active = e.selected?.[0];
      if (active && (active as any).customId) {
        selectElement((active as any).customId);
      }
    });

    c.on('selection:cleared', () => {
      selectElement(null);
    });

    // Object modification sync back to Zustand
    c.on('object:modified', (e: any) => {
      const obj = e.target;
      if (!obj || !(obj as any).customId || !activeFooter) return;

      pushUndo();
      const elId = (obj as any).customId;
      const fx = activeFooter.x;
      const fy = activeFooter.y;

      const newLeft = (obj.left || 0) - fx;
      const newTop = (obj.top || 0) - fy;
      const newWidth = (obj.width || 0) * (obj.scaleX || 1);
      const newHeight = (obj.height || 0) * (obj.scaleY || 1);

      updateActiveFooterElement(elId, {
        x: Math.max(0, newLeft),
        y: Math.max(0, newTop),
        width: Math.max(10, newWidth),
        height: Math.max(10, newHeight),
      });
    });

    // Text inline edited
    c.on('text:changed', (e: any) => {
      const target = e.target as any;
      if (target && target.customId) {
        updateActiveFooterElement(target.customId, {
          text: target.text || '',
        });
      }
    });

    return () => {
      c.dispose();
      fabricCanvasRef.current = null;
    };
  }, [posterWidth, posterHeight]);

  // Sync poster background and footer elements into Fabric Canvas
  useEffect(() => {
    const c = fabricCanvasRef.current;
    if (!c || isUpdatingFabricRef.current) return;

    isUpdatingFabricRef.current = true;
    c.clear();
    c.setWidth(posterWidth);
    c.setHeight(posterHeight);

    // 1. Poster background
    if (posterDataUrl) {
      fabric.Image.fromURL(
        posterDataUrl,
        (img: any) => {
          img.set({
            left: 0,
            top: 0,
            selectable: false,
            evented: false,
            scaleX: posterWidth / (img.width || posterWidth),
            scaleY: posterHeight / (img.height || posterHeight),
          });
          c.setBackgroundImage(img, c.renderAll.bind(c));
        },
        { crossOrigin: 'anonymous' }
      );
    } else {
      c.setBackgroundColor('#0f172a', c.renderAll.bind(c));
    }

    // 2. Footer background & elements
    if (activeFooter) {
      const fx = activeFooter.x;
      const fy = activeFooter.y;
      const fw = activeFooter.width;
      const fh = activeFooter.height;

      // Footer background rect
      const bgRect = new fabric.Rect({
        left: fx,
        top: fy,
        width: fw,
        height: fh,
        fill: activeFooter.background.color || '#0f172a',
        opacity: activeFooter.background.opacity ?? 1,
        rx: activeFooter.background.border_radius || 0,
        ry: activeFooter.background.border_radius || 0,
        selectable: true,
        customId: 'footer_background',
        stroke: '#334155',
        strokeWidth: 1,
      } as any);
      c.add(bgRect);

      // Footer elements
      activeFooter.elements.forEach((el) => {
        if (!el.visible) return;

        const elX = fx + el.x;
        const elY = fy + el.y;

        if (el.type === 'text' || el.type === 'icon_text') {
          const itext = new fabric.IText(el.text || '', {
            left: elX,
            top: elY,
            fontSize: el.style.font_size || 14,
            fill: el.style.color || '#ffffff',
            fontFamily: el.style.font_family || 'Inter, sans-serif',
            fontWeight: (el.style.font_weight as any) || 'normal',
            customId: el.id,
            editable: true,
          } as any);
          c.add(itext);
        } else if (el.type === 'badge' || el.type === 'cta') {
          const btnRect = new fabric.Rect({
            width: el.width,
            height: el.height,
            fill: el.style.background_color || '#f59e0b',
            rx: el.style.border_radius || 6,
            ry: el.style.border_radius || 6,
          });
          const btnText = new fabric.IText(el.text || 'Action', {
            fontSize: el.style.font_size || 13,
            fill: el.style.color || '#000000',
            fontFamily: 'Inter',
            fontWeight: 'bold',
            originX: 'center',
            originY: 'center',
            left: el.width / 2,
            top: el.height / 2,
          });
          const group = new fabric.Group([btnRect, btnText], {
            left: elX,
            top: elY,
            customId: el.id,
          } as any);
          c.add(group);
        } else if ((el.type === 'logo' || el.type === 'profile' || el.type === 'qr') && el.image_url) {
          fabric.Image.fromURL(
            el.image_url,
            (img: any) => {
              const scale = Math.min(el.width / (img.width || 1), el.height / (img.height || 1));
              img.set({
                left: elX,
                top: elY,
                scaleX: scale,
                scaleY: scale,
                customId: el.id,
              } as any);
              c.add(img);
              c.renderAll();
            },
            { crossOrigin: 'anonymous' }
          );
        }
      });
    }

    c.renderAll();
    isUpdatingFabricRef.current = false;
  }, [activeFooter, posterDataUrl, posterWidth, posterHeight]);

  // Pan controls
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 1 || e.altKey) {
      setIsPanning(true);
      startPanRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({ x: e.clientX - startPanRef.current.x, y: e.clientY - startPanRef.current.y });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleFit = () => {
    setZoom(0.65);
    setPan({ x: 0, y: 0 });
  };

  // Fabric object manipulation helpers
  const getSelectedFabricObject = (): any => {
    const c = fabricCanvasRef.current;
    if (!c) return undefined;
    return c.getActiveObject() || undefined;
  };

  const handleDeleteSelected = () => {
    const c = fabricCanvasRef.current;
    const active = getSelectedFabricObject();
    if (!c || !active || !(active as any).customId) return;

    const elId = (active as any).customId;
    if (elId === 'footer_background') return;

    pushUndo();
    c.remove(active);
    c.discardActiveObject();
    c.renderAll();
    selectElement(null);
    updateActiveFooterElement(elId, { visible: false });
  };

  const handleToggleLock = () => {
    const active = getSelectedFabricObject();
    if (!active) return;
    const nextLocked = !isLocked;
    setIsLocked(nextLocked);
    active.set({
      lockMovementX: nextLocked,
      lockMovementY: nextLocked,
      lockScalingX: nextLocked,
      lockScalingY: nextLocked,
      lockRotation: nextLocked,
      hasControls: !nextLocked,
    });
    fabricCanvasRef.current?.renderAll();
  };

  const handleBringForward = () => {
    const c = fabricCanvasRef.current;
    const active = getSelectedFabricObject();
    if (c && active) {
      c.bringForward(active);
      c.renderAll();
    }
  };

  const handleSendBackward = () => {
    const c = fabricCanvasRef.current;
    const active = getSelectedFabricObject();
    if (c && active) {
      c.sendBackwards(active);
      c.renderAll();
    }
  };

  return (
    <div
      className="flex-1 h-full bg-slate-950 relative overflow-hidden flex items-center justify-center select-none"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      {/* Top Floating Editing Toolbar */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-1.5 bg-slate-800/90 border border-slate-700/80 rounded-xl p-1.5 shadow-2xl backdrop-blur-md z-30">
        <div className="flex items-center bg-slate-900/80 rounded-lg p-0.5 border border-slate-700/60 mr-2">
          <button
            onClick={() => setMode('fabric')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition ${mode === 'fabric' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            title="Interactive Drag & Resize Mode"
          >
            <Edit3 className="w-3.5 h-3.5" /> Interactive
          </button>
          <button
            onClick={() => setMode('vector')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition ${mode === 'vector' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            title="Clean SVG Vector Preview Mode"
          >
            <Eye className="w-3.5 h-3.5" /> Vector Preview
          </button>
        </div>

        {/* Undo / Redo */}
        <button
          onClick={undo}
          disabled={undoStack.length === 0}
          className="p-1.5 hover:bg-slate-700/80 rounded text-slate-300 disabled:opacity-40 transition"
          title="Undo (Ctrl+Z)"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button
          onClick={redo}
          disabled={redoStack.length === 0}
          className="p-1.5 hover:bg-slate-700/80 rounded text-slate-300 disabled:opacity-40 transition"
          title="Redo (Ctrl+Y)"
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <div className="w-[1px] h-4 bg-slate-700 mx-1" />

        {/* Layer Controls */}
        <button
          onClick={handleBringForward}
          disabled={!selectedElementId}
          className="p-1.5 hover:bg-slate-700/80 rounded text-slate-300 disabled:opacity-40 transition"
          title="Bring Forward"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
        <button
          onClick={handleSendBackward}
          disabled={!selectedElementId}
          className="p-1.5 hover:bg-slate-700/80 rounded text-slate-300 disabled:opacity-40 transition"
          title="Send Backward"
        >
          <ArrowDown className="w-4 h-4" />
        </button>

        {/* Lock / Unlock */}
        <button
          onClick={handleToggleLock}
          disabled={!selectedElementId}
          className={`p-1.5 hover:bg-slate-700/80 rounded transition ${isLocked ? 'text-amber-400 bg-amber-500/20' : 'text-slate-300'
            } disabled:opacity-40`}
          title={isLocked ? 'Unlock Element' : 'Lock Element'}
        >
          {isLocked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
        </button>

        {/* Delete */}
        <button
          onClick={handleDeleteSelected}
          disabled={!selectedElementId || selectedElementId === 'footer_background'}
          className="p-1.5 hover:bg-rose-500/20 hover:text-rose-400 rounded text-slate-300 disabled:opacity-40 transition"
          title="Delete Element (Del)"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Zoom / Pan viewport */}
      <div
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoomLevel})`,
          transformOrigin: 'center center',
          transition: isPanning ? 'none' : 'transform 0.15s ease-out',
        }}
        className="relative shadow-2xl rounded-sm overflow-hidden border border-slate-800 bg-slate-900"
      >
        {/* Canvas container */}
        <div
          style={{
            width: `${posterWidth}px`,
            height: `${posterHeight}px`,
          }}
          className="relative overflow-hidden bg-slate-900 flex items-center justify-center"
        >
          {mode === 'fabric' ? (
            <canvas ref={canvasElRef} />
          ) : (
            <div className="relative w-full h-full">
              {posterDataUrl ? (
                <img
                  src={posterDataUrl}
                  alt="Uploaded Poster"
                  className="w-full h-full object-cover pointer-events-none"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-600">
                  <Layers className="w-16 h-16 mb-4 opacity-40 text-indigo-400" />
                  <p className="text-xl font-semibold text-slate-400">Poster Canvas</p>
                </div>
              )}
              {activeFooter?.svg_markup && (
                <div
                  style={{
                    position: 'absolute',
                    left: `${activeFooter.x}px`,
                    top: `${activeFooter.y}px`,
                    width: `${activeFooter.width}px`,
                    height: `${activeFooter.height}px`,
                  }}
                  dangerouslySetInnerHTML={{ __html: sanitizeSvg(activeFooter.svg_markup) }}
                />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Floating Canvas Zoom Controls */}
      <div className="absolute bottom-6 right-6 flex items-center gap-1.5 bg-slate-800/95 border border-slate-700/80 rounded-lg p-1.5 shadow-xl backdrop-blur-md z-30">
        <button
          onClick={() => setZoom(zoomLevel - 0.1)}
          className="p-2 hover:bg-slate-700/80 rounded text-slate-300 hover:text-white transition"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-xs font-mono font-medium px-2 text-slate-400">
          {Math.round(zoomLevel * 100)}%
        </span>
        <button
          onClick={() => setZoom(zoomLevel + 0.1)}
          className="p-2 hover:bg-slate-700/80 rounded text-slate-300 hover:text-white transition"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <div className="w-[1px] h-4 bg-slate-700 mx-1" />
        <button
          onClick={handleFit}
          className="p-2 hover:bg-slate-700/80 rounded text-slate-300 hover:text-white transition"
          title="Zoom to Fit"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
