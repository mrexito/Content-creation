"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, History, Home } from "lucide-react"

const links = [
  { href: "/", label: "Run", icon: Home },
  { href: "/history", label: "History", icon: History },
]

export function NavBar() {
  const pathname = usePathname()

  return (
    <nav className="border-b border-slate-600 bg-slate-700/90 backdrop-blur sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-7xl flex items-center justify-between h-14">
        <div className="flex items-center gap-2 font-semibold text-slate-100">
          <BarChart3 className="h-5 w-5 text-blue-400" />
          <span className="hidden sm:block">LangChain vs LangGraph</span>
          <span className="sm:hidden">LC vs LG</span>
        </div>
        <div className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                pathname === href
                  ? "bg-slate-600 text-slate-50"
                  : "text-slate-300 hover:text-slate-50 hover:bg-slate-600/50"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}
