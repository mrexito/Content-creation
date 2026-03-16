import { NextRequest, NextResponse } from "next/server"
import { readResult } from "@/lib/python-runner"

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params
  const frameworks = ["langchain", "langgraph", "hybrid", "agent_orchestrator", "agent_multi", "hybrid_agent"]
  const result: Record<string, unknown> = {}

  for (const fw of frameworks) {
    const data = readResult(runId, fw)
    if (data) result[fw] = data
  }

  return NextResponse.json(result)
}
