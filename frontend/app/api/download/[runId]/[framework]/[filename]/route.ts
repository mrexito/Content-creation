import { NextRequest, NextResponse } from "next/server"
import path from "path"
import fs from "fs"

const PROJECT_ROOT = path.resolve(process.cwd(), "..")
const DATA_OUTPUT_DIR = path.join(PROJECT_ROOT, "data", "output")

export async function GET(
  _req: NextRequest,
  {
    params,
  }: {
    params: Promise<{ runId: string; framework: string; filename: string }>
  }
) {
  const { runId, framework, filename } = await params

  // Nur .pdf-Dateien erlauben
  if (!filename.endsWith(".pdf")) {
    return NextResponse.json({ error: "Only PDF files are allowed" }, { status: 400 })
  }

  // Path-Traversal verhindern: normalisierter Pfad muss innerhalb DATA_OUTPUT_DIR liegen
  const filePath = path.resolve(DATA_OUTPUT_DIR, framework, runId, filename)
  if (!filePath.startsWith(path.resolve(DATA_OUTPUT_DIR))) {
    return NextResponse.json({ error: "Invalid path" }, { status: 400 })
  }

  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: "File not found" }, { status: 404 })
  }

  const fileBuffer = fs.readFileSync(filePath)

  return new NextResponse(fileBuffer, {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Content-Length": String(fileBuffer.length),
    },
  })
}
