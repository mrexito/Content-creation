import { NextRequest, NextResponse } from "next/server"
import { readProgress, getProgressPath } from "@/lib/python-runner"

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params
  const frameworks = ["langchain", "langgraph"]
  const result: Record<string, unknown> = {}

  for (const fw of frameworks) {
    const progressPath = getProgressPath(runId, fw)
    const progress = readProgress(progressPath)
    if (progress) {
      result[fw] = progress
    }
  }

  return NextResponse.json(result)
}
