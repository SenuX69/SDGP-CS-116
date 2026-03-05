import Link from "next/link";
import Image from "next/image";
import { Linkedin, Github, Facebook } from "lucide-react";

const Footer = () => {
  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/data-sources", label: "Data Sources" },
    { href: "/about", label: "About" },
    { href: "/how-this-works", label: "How this Works" },
  ];

  return (
    <footer className="w-full border-t border-[#9578d3] bg-[#dfd7f1] backdrop-blur-sm">
      <div className="mx-auto w-full max-w-7xl p-4 py-6 lg:py-8">
        <div className="md:flex md:justify-between">
          <div className="mb-6 md:mb-0">
            <Link href="/" className="flex items-center gap-2">
              <div className="relative w-16 h-16 overflow-hidden">
                <Image
                  src="/logonb.png"
                  alt="PathFinder+ Logo"
                  fill
                  className="object-contain"
                />
              </div>
              <span className="text-3xl font-bold tracking-tight text-[#633db4]">
                PathFinder+
              </span>
            </Link>
            <p className="mt-1 max-w-xs text-sm font-medium text-[#4f318f]">
              Your Path is ours to make.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8 sm:gap-6 sm:grid-cols-3">
            <div>
              <h2 className="mb-6 text-sm font-semibold text-[#30203d] uppercase">Platform</h2>
              <ul className="text-[#4f318f] font-medium">
                {navLinks.map((link) => (
                  <li key={link.href} className="mb-4">
                    <Link href={link.href} className="hover:text-[#3898ff] transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h2 className="mb-6 text-sm font-semibold text-[#30203d] uppercase">Legal</h2>
              <ul className="text-[#4f318f] font-medium">
                <li className="mb-4">
                  <Link href="/privacy" className="hover:underline">Privacy Policy</Link>
                </li>
                <li>
                  <Link href="/terms" className="hover:underline">Terms &amp; Conditions</Link>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <hr className="my-6 border-purple-100 sm:mx-auto lg:my-8" />

        <div className="sm:flex sm:items-center sm:justify-between">
          <span className="text-sm text-gray-500 sm:text-center">
            © {new Date().getFullYear()} <Link href="/" className="hover:underline">PathFinder+™</Link>. All Rights Reserved.
          </span>
          <div className="flex mt-4 sm:justify-center sm:mt-0 gap-4">
            <a href="https://linkedin.com" className="flex items-center justify-center w-9 h-9 rounded-full text-gray-500 hover:text-purple-600 hover:bg-white/30">
              <Linkedin size={18} className="align-middle" />
              <span className="sr-only">LinkedIn account</span>
            </a>
            <a href="https://facebook.com" className="flex items-center justify-center w-9 h-9 rounded-full text-gray-500 hover:text-purple-600 hover:bg-white/30">
              <Facebook size={18} className="align-middle" />
              <span className="sr-only">Facebook account</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;