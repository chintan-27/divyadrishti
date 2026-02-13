"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

const links = [
  { href: "/", label: "Trending" },
  { href: "/metrics", label: "Metrics" },
  { href: "/rankings", label: "Rankings" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-1">
      {links.map(({ href, label }) => {
        const isActive =
          href === "/" ? pathname === "/" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className={`nav-link ${isActive ? "nav-link-active" : ""}`}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
