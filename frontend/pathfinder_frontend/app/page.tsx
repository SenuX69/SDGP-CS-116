import Link from "next/link";
import Image from "next/image";
import TestimonialCarousel from "./components/TestimonialCarousel";
// import HeroHeroUI from "./components/ui/HeroHeroUI";

export default function HomePage() {
  const navLinks = [
    { href: "/skill-assessment", label: "Assessment" },
    { href: "/resumes", label: "Resumes" },
    { href: "/mentors", label: "Mentors" },
  ];

  const testimonials = [
    {
      name: "Nishan Perera",
      role: "Backend Developer — Colombo",
      text: "PathFinder+ helped me identify the exact short courses I needed to move from a part-time developer role to a full-time position.",
      img: "/team/p1.jpg"
    },
    {
      name: "Kasun Samantha",
      role: "Data Analyst — Kandy",
      text: "As someone switching from marketing, the personalised pathway made my learning plan clear. I landed an data analyst role in months.",
      img: "/team/p2.jpg"
    },
    {
      name: "Amaara Silva",
      role: "Junior Developer — Galle",
      text: "The recommendations matched live job descriptions I was targeting. I moved from intern to junior dev in three months.",
      img: "/team/p3.jpg"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-purple-100">
      <div className="mx-auto max-w-7xl px-6">
        <nav className="flex items-center justify-between py-8">
          <Link href="/" className="flex items-center gap-2 group cursor-pointer">
            <Image src="/logonb.png" alt="PathFinder+ Logo" width={32} height={32} className="object-contain" />
            <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600">
              PathFinder+
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-10">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href} className="text-sm font-semibold text-slate-600 hover:text-purple-600 transition-all">
                {link.label}
              </Link>
            ))}
          </div>
          <div className="md:hidden">
            <button className="text-slate-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" /></svg>
            </button>
          </div>
        </nav>
      </div>

      <div className="mx-auto max-w-7xl px-6">
        {/* Testimonials - Carousel */}
        <section className="py-32 border-t border-slate-100 relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-24 bg-gradient-to-b from-purple-200 to-transparent" />
          <div className="text-center mb-16 animate-fade-up">
            <h2 className="text-4xl font-black text-slate-900 tracking-tight">Success Stories</h2>
            <p className="text-slate-500 mt-4 text-lg">Join 1,000+ professionals across Sri Lanka</p>
          </div>
          <TestimonialCarousel items={testimonials} />
        </section>
      </div>
    </div>
  );
}
