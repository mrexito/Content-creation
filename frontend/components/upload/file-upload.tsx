"use client";

import { useCallback, useState } from "react";
import { Upload, X, FileText } from "lucide-react";
import { formatBytes } from "@/lib/file-utils";

interface FileUploadProps {
  files: File[];
  onChange: (files: File[]) => void;
}

export function FileUpload({ files, onChange }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);

  const addFiles = useCallback(
    (newFiles: FileList | File[]) => {
      const pdfs = Array.from(newFiles).filter((f) => f.name.endsWith(".pdf"));
      const merged = [...files, ...pdfs].filter(
        (f, i, arr) => arr.findIndex((x) => x.name === f.name) === i,
      );
      onChange(merged);
    },
    [files, onChange],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      addFiles(e.dataTransfer.files);
    },
    [addFiles],
  );

  const remove = (name: string) =>
    onChange(files.filter((f) => f.name !== name));

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          dragging
            ? "border-blue-400 bg-blue-50"
            : "border-gray-300 hover:border-blue-400 hover:bg-blue-50/40"
        }`}
        onClick={() => document.getElementById("pdf-input")?.click()}
      >
        <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
        <p className="text-sm font-medium text-gray-700">
          Drop PDFs here or click to browse
        </p>
        <p className="text-xs text-gray-400 mt-1">Multiple files supported</p>
        <input
          id="pdf-input"
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && addFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-1.5">
          {files.map((f) => (
            <li
              key={f.name}
              className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-md px-3 py-2"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-4 w-4 text-blue-500 shrink-0" />
                <span className="text-sm font-medium truncate text-gray-800">
                  {f.name}
                </span>
                <span className="text-xs text-gray-400 shrink-0">
                  {formatBytes(f.size)}
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  remove(f.name);
                }}
                className="ml-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
