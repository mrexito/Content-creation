"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, History, Home } from "lucide-react";

const links = [
  { href: "/", label: "Run", icon: Home },
  { href: "/history", label: "History", icon: History },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 max-w-7xl flex items-center justify-between h-14">
        <div className="flex items-center gap-2 font-semibold text-gray-900">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <span className="hidden sm:block">LC vs LG vs Hybrid</span>
          <span className="sm:hidden">LC·LG·HY</span>
        </div>
        <div className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                pathname === href
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
