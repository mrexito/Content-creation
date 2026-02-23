import { NextRequest, NextResponse } from "next/server"
import { getUploadDir, saveUploadedFile } from "@/lib/server-utils"

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData()
    const files = formData.getAll("files") as File[]

    if (!files.length) {
      return NextResponse.json({ error: "No files provided" }, { status: 400 })
    }

    const uploadDir = getUploadDir()
    const saved: { name: string; path: string; size: number }[] = []

    for (const file of files) {
      if (!file.name.endsWith(".pdf")) {
        return NextResponse.json({ error: `File ${file.name} is not a PDF` }, { status: 400 })
      }
      const buffer = Buffer.from(await file.arrayBuffer())
      const savedPath = saveUploadedFile(buffer, file.name, uploadDir)
      saved.push({ name: file.name, path: savedPath, size: file.size })
    }

    return NextResponse.json({ success: true, files: saved })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
