// frontend/src/modules/dashboard/WidgetCustomizerModal.jsx
import React from 'react';
import {
  X,
  Sliders,
  Eye,
  EyeOff,
  ArrowUp,
  ArrowDown,
  Pin,
  RotateCcw,
  Check,
} from 'lucide-react';

export default function WidgetCustomizerModal({
  isOpen,
  onClose,
  widgetRegistry,
  preferences,
  onSavePreferences,
  onResetPreferences,
}) {
  if (!isOpen) return null;

  const currentOrder = preferences.widget_order || [];
  const currentVisibility = preferences.widget_visibility || {};
  const currentSizes = preferences.widget_sizes || {};
  const pinnedWidgets = preferences.pinned_widgets || [];

  const handleToggleVisibility = (widgetId) => {
    // Critical widgets like attention_required cannot be hidden if critical
    const newVis = {
      ...currentVisibility,
      [widgetId]: currentVisibility[widgetId] === false ? true : false,
    };
    onSavePreferences({
      ...preferences,
      widget_visibility: newVis,
    });
  };

  const handleToggleSize = (widgetId) => {
    const currentSize = currentSizes[widgetId] || 'full';
    const newSize = currentSize === 'full' ? 'half' : 'full';
    onSavePreferences({
      ...preferences,
      widget_sizes: {
        ...currentSizes,
        [widgetId]: newSize,
      },
    });
  };

  const handleTogglePin = (widgetId) => {
    const isPinned = pinnedWidgets.includes(widgetId);
    const newPinned = isPinned
      ? pinnedWidgets.filter((id) => id !== widgetId)
      : [...pinnedWidgets, widgetId];
    onSavePreferences({
      ...preferences,
      pinned_widgets: newPinned,
    });
  };

  const handleMove = (index, direction) => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= currentOrder.length) return;

    const newOrder = [...currentOrder];
    const [moved] = newOrder.splice(index, 1);
    newOrder.splice(targetIndex, 0, moved);

    onSavePreferences({
      ...preferences,
      widget_order: newOrder,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
              <Sliders className="w-4 h-4 text-[#1e40af]" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 tracking-tight">
                Customize Unified Dashboard Layout
              </h3>
              <p className="text-xs text-slate-500">
                Organize, pin, or toggle visibility of widgets across your workspace.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition cursor-pointer"
            aria-label="Close customizer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: List of Widgets */}
        <div className="p-5 overflow-y-auto space-y-3 divide-y divide-slate-100">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider pb-1">
            Active Widget Hierarchy &amp; Visibility
          </div>

          <div className="space-y-2 pt-2">
            {currentOrder.map((widgetId, idx) => {
              const widgetMeta = widgetRegistry[widgetId] || {
                title: widgetId.replace(/_/g, ' '),
                description: 'Dashboard module widget',
                category: 'General',
                isEligible: true,
              };

              const isVisible = currentVisibility[widgetId] !== false;
              const isPinned = pinnedWidgets.includes(widgetId);
              const isEligible = widgetMeta.isEligible !== false;

              return (
                <div
                  key={widgetId}
                  className={`p-3.5 rounded-xl border transition flex items-center justify-between gap-3 ${
                    !isEligible
                      ? 'bg-slate-50/60 border-slate-200/60 opacity-60'
                      : isVisible
                      ? 'bg-white border-slate-200 shadow-2xs hover:border-slate-300'
                      : 'bg-slate-50 border-dashed border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-500 text-xs font-mono font-bold flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-xs font-bold truncate ${isVisible ? 'text-slate-900' : 'text-slate-500'}`}>
                          {widgetMeta.title}
                        </span>
                        {isPinned && (
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
                            <Pin className="w-2.5 h-2.5" /> Pinned
                          </span>
                        )}
                        {!isEligible && (
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            Lifecycle Locked
                          </span>
                        )}
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-500 capitalize">
                          {widgetMeta.category || 'General'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5 truncate">
                        {widgetMeta.description}
                      </p>
                    </div>
                  </div>

                  {/* Actions Bar */}
                  <div className="flex items-center gap-1.5 shrink-0">
                    {/* Size Selector */}
                    <button
                      type="button"
                      onClick={() => handleToggleSize(widgetId)}
                      disabled={!isVisible}
                      className="px-2 py-1 rounded text-[11px] font-mono font-semibold border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 disabled:opacity-40 transition cursor-pointer"
                      title="Toggle between Full width (100%) and Half width (50%)"
                    >
                      {size.toUpperCase()}
                    </button>

                    {/* Pin Toggle */}
                    <button
                      type="button"
                      onClick={() => handleTogglePin(widgetId)}
                      disabled={!isVisible}
                      className={`p-1.5 rounded-lg border transition cursor-pointer ${
                        isPinned
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-white text-slate-400 hover:text-slate-700 border-slate-200'
                      }`}
                      title={isPinned ? 'Unpin from priority area' : 'Pin to top of dashboard'}
                    >
                      <Pin className="w-3.5 h-3.5" />
                    </button>

                    {/* Move Up */}
                    <button
                      type="button"
                      onClick={() => handleMove(idx, -1)}
                      disabled={idx === 0}
                      className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-700 disabled:opacity-30 transition cursor-pointer"
                      title="Move widget up"
                    >
                      <ArrowUp className="w-3.5 h-3.5" />
                    </button>

                    {/* Move Down */}
                    <button
                      type="button"
                      onClick={() => handleMove(idx, 1)}
                      disabled={idx === currentOrder.length - 1}
                      className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-700 disabled:opacity-30 transition cursor-pointer"
                      title="Move widget down"
                    >
                      <ArrowDown className="w-3.5 h-3.5" />
                    </button>

                    {/* Visibility Toggle */}
                    <button
                      type="button"
                      onClick={() => handleToggleVisibility(widgetId)}
                      className={`p-1.5 rounded-lg border transition cursor-pointer ${
                        isVisible
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-slate-100 text-slate-400 border-slate-200'
                      }`}
                      title={isVisible ? 'Hide widget from dashboard' : 'Show widget on dashboard'}
                    >
                      {isVisible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onResetPreferences}
            className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-100 shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            <span>Restore Defaults</span>
          </button>

          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-white bg-[#1e40af] hover:bg-[#1d4ed8] rounded-lg shadow-xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Done Customizing</span>
          </button>
        </div>
      </div>
    </div>
  );
}
