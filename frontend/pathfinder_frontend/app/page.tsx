import Link from "next/link";
import Image from "next/image";
import TestimonialCarousel from "./components/TestimonialCarousel";

// Using Lucide-style icons (simplified as SVGs) adds a "pro" feel
const icons = {
  assessment: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
  ),
  resume: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
  ),
  mentor: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
  ),
  data: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
  ),
};

export default function HomePage() {
  const navLinks = [
    { href: "/skill-assessment", label: "Assessment" },
    { href: "/resumes", label: "Resumes" },
    { href: "/mentors", label: "Mentors" },
  ];

  const features = [
    { title: "Skill Assessment", desc: "Identify your strengths and bridge industry gaps.", icon: icons.assessment },
    { title: "Resume Builder", desc: "Create high-converting, ATS-friendly resumes.", icon: icons.resume },
    { title: "AI Mentors", desc: "24/7 career advice from specialized industry bots.", icon: icons.mentor },
    { title: "Data Insights", desc: "Market-driven data to guide your next move.", icon: icons.data },
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
      text: "As someone switching from marketing, the personalised pathway made my learning plan clear. I landed an data analyst role in  months.",
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

      <div className="absolute top-0 left-1/2 -z-10 h-[1000px] w-full -translate-x-1/2 [background:radial-gradient(100%_50%_at_50%_0%,rgba(168,85,247,0.15)_0,rgba(255,255,255,0)_100%)]" />

      <div className="mx-auto max-w-7xl px-6">

        <nav className="flex items-center justify-between py-8">
          <div className="flex items-center gap-2 group cursor-pointer">

            <Image src="/logonb.png" alt="PathFinder+ Logo" width={32} height={32} className="object-contain" />

            <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600">
              PathFinder+
            </span>
          </div>
          <div className="hidden md:flex items-center gap-10">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href} className="text-sm font-semibold text-slate-600 hover:text-purple-600 transition-all">
                {link.label}
              </Link>
            ))}

          </div>
        </nav>
        {/* 
  

       
        <section className="py-24">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, i) => (
              <div key={i} className="group flex flex-col rounded-3xl border border-slate-100 bg-white p-8 transition-all hover:border-purple-200 hover:shadow-2xl hover:shadow-purple-500/10">
                <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-purple-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-slate-900">{feature.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate-500">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section> */}

        {/* Testimonials - Carousel */}
        <section className="py-24 border-t border-slate-100">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Success Stories</h2>
            <p className="text-slate-500 mt-2">Join 1,000+ professionals across Sri Lanka</p>
          </div>
          <TestimonialCarousel items={testimonials} />
        </section>
      </div>
    </div>
  );
}