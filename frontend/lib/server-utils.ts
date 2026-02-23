// Server-only file utilities (Node.js built-ins)
import path from "path"
import fs from "fs"
import { sanitizeFilename } from "./file-utils"

export function getUploadDir(): string {
  const dir = path.join(path.resolve(process.cwd(), ".."), "data", "input", "frontend-uploads")
  fs.mkdirSync(dir, { recursive: true })
  return dir
}

export function saveUploadedFile(buffer: Buffer, filename: string, uploadDir: string): string {
  const safe = sanitizeFilename(filename)
  const dest = path.join(uploadDir, safe)
  fs.writeFileSync(dest, buffer)
  return dest
}
