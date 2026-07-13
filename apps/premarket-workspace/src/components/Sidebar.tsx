"use client";

import { LockKeyhole } from "lucide-react";
import Link from "next/link";

import { navigationGroups, navigationItemForPath, navigationPath } from "@/lib/navigation";

export function Sidebar({pathname, selectedSymbol = "000333.SZ"}: {pathname: string; selectedSymbol?: string}) {
  const active = navigationItemForPath(pathname);
  return <aside className="sidebar" aria-label="Workspace navigation">
    <div className="sidebar-title"><strong>RESEARCH CONTROL</strong><span>LOCAL / READ ONLY</span></div>
    <nav>{navigationGroups.map((group) => <section key={group.label}><h2>{group.label}</h2>{group.items.map((item) => {const Icon = item.icon; return <Link key={item.id} href={navigationPath(item, selectedSymbol)} className={active.id === item.id ? "is-active" : ""} aria-current={active.id === item.id ? "page" : undefined}><Icon aria-hidden="true" /><span>{item.label}</span>{item.state === "LOCKED" ? <LockKeyhole className="nav-lock" aria-label="Locked" /> : null}</Link>;})}</section>)}</nav>
    <footer><strong>RESEARCH ONLY</strong><span>Not trading advice</span><span>No broker connection</span><span>No execution path</span></footer>
  </aside>;
}
