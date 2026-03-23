"use client";

import React, {useState} from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Navbar as HeroNavbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
  NavbarMenu,
  NavbarMenuItem,
} from "@heroui/navbar";
import {Button} from "@heroui/react";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  React.useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) setIsLoggedIn(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    setIsLoggedIn(false);
    window.location.href = "/";
  };

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/resumes", label: "Resumes" },
    { href: "/mentors", label: "Mentors" },
  ];

  return (
    <HeroNavbar maxWidth="xl" isBordered className="bg-content1/90 backdrop-blur-xl z-50 w-full" onMenuOpenChange={setIsMenuOpen}>
      <NavbarContent>
        <NavbarMenuToggle aria-label={isMenuOpen ? "Close menu" : "Open menu"} className="sm:hidden" />
        <NavbarBrand as={Link} href="/" className="gap-2 group cursor-pointer max-w-[200px] overflow-visible">
          <div className="w-10 h-10 flex items-center justify-center overflow-visible">
            <Image src="/logonb.png" alt="PathFinder+ Logo" width={48} height={48} className="object-contain scale-150 transform origin-center drop-shadow-md" />
          </div>
          <span className="text-xl font-sora font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-purple-700 to-indigo-600 dark:from-purple-400 dark:to-indigo-400">
            PathFinder+
          </span>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent className="hidden sm:flex gap-10" justify="center">
        <NavbarItem>
          <Link href="/" className="text-sm font-semibold text-foreground hover:text-pf-purple-600 transition-colors">
            Home
          </Link>
        </NavbarItem>
        <NavbarItem><Link href="/dashboard" className="text-sm font-semibold text-foreground hover:text-pf-purple-600 transition-colors">Dashboard</Link></NavbarItem>
        <NavbarItem><Link href="/resumes" className="text-sm font-semibold text-foreground hover:text-pf-purple-600 transition-colors">Resumes</Link></NavbarItem>
        <NavbarItem><Link href="/mentors" className="text-sm font-semibold text-foreground hover:text-pf-purple-600 transition-colors">Mentors</Link></NavbarItem>
      </NavbarContent>

      <NavbarContent justify="end" className="gap-3">
        {isLoggedIn ? (
          <NavbarItem>
            <Button
              onPress={handleLogout}
              color="danger"
              variant="flat"
              className="font-bold text-sm px-6 h-10 shadow-sm border border-danger-500/20"
            >
              Sign Out
            </Button>
          </NavbarItem>
        ) : (
          <>
            <NavbarItem className="hidden lg:flex">
              <Link href="/login" className="text-sm font-bold text-foreground hover:text-pf-purple-600 transition-colors">
                Login
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Button
                as={Link}
                color="secondary"
                href="/register"
                variant="solid"
                className="font-bold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/30 px-6 h-10 hover:shadow-purple-500/50 transition-all hover:-translate-y-0.5"
              >
                Sign Up
              </Button>
            </NavbarItem>
          </>
        )}
      </NavbarContent>

      <NavbarMenu className="bg-background/95 backdrop-blur-xl pt-6">
        {navLinks.map((item, index) => (
          <NavbarMenuItem key={`${item}-${index}`}>
            <Link
              className="w-full text-foreground/80 hover:text-pf-purple-600 text-lg font-medium transition-colors"
              href={item.href}
            >
              {item.label}
            </Link>
          </NavbarMenuItem>
        ))}
      </NavbarMenu>
    </HeroNavbar>
  );
}
