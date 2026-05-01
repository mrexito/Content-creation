"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

function JsonNode({ data, depth = 0 }: { data: unknown; depth?: number }) {
  const [collapsed, setCollapsed] = useState(depth > 1);

  if (data === null) return <span className="text-gray-400">null</span>;
  if (typeof data === "boolean")
    return <span className="text-orange-500">{String(data)}</span>;
  if (typeof data === "number")
    return <span className="text-blue-600">{data}</span>;
  if (typeof data === "string")
    return <span className="text-emerald-600">&quot;{data}&quot;</span>;

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="text-gray-400">[]</span>;
    return (
      <span>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="inline-flex items-center text-gray-500 hover:text-gray-800"
        >
          {collapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          <span className="text-gray-400 text-xs ml-0.5">[{data.length}]</span>
        </button>
        {!collapsed && (
          <div className="ml-4 border-l border-gray-200 pl-3">
            {data.map((item, i) => (
              <div key={i} className="py-0.5">
                <span className="text-gray-400 text-xs mr-1">{i}:</span>
                <JsonNode data={item} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </span>
    );
  }

  if (typeof data === "object") {
    const keys = Object.keys(data as object);
    if (keys.length === 0) return <span className="text-gray-400">{"{}"}</span>;
    return (
      <span>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="inline-flex items-center text-gray-500 hover:text-gray-800"
        >
          {collapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          <span className="text-gray-400 text-xs ml-0.5">
            {"{"}…{"}"}
          </span>
        </button>
        {!collapsed && (
          <div className="ml-4 border-l border-gray-200 pl-3">
            {keys.map((k) => (
              <div key={k} className="py-0.5">
                <span className="text-purple-600 text-xs">&quot;{k}&quot;</span>
                <span className="text-gray-400 text-xs">: </span>
                <JsonNode
                  data={(data as Record<string, unknown>)[k]}
                  depth={depth + 1}
                />
              </div>
            ))}
          </div>
        )}
      </span>
    );
  }

  return <span className="text-gray-700">{String(data)}</span>;
}

interface JsonViewerProps {
  data: unknown;
  title?: string;
}

export function JsonViewer({ data, title }: JsonViewerProps) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden shadow-sm">
      {title && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white">
          <span className="text-xs font-mono text-gray-500">{title}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={copy}
            className="h-6 px-2 text-xs text-gray-500 hover:text-gray-900"
          >
            {copied ? (
              <Check className="h-3 w-3 text-emerald-500" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>
        </div>
      )}
      <div className="p-4 font-mono text-xs leading-relaxed overflow-auto max-h-96">
        <JsonNode data={data} />
      </div>
    </div>
  );
}
