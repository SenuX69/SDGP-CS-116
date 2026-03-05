"use client";

import Stepper from "../components/Stepper";

const steps = [
  {
    title: "1) User Profile Input",
    description:
      "Start by sharing your background. Whether you're a student or a professional, we analyze your education level, current skills, and career aspirations to build a unique profile of where you stand today.",
  },
  {
    title: "2) Local Data Matching",
    description:
      "Our AI engine cross-references your profile against thousands of job market requirements, ESCO skill frameworks, and real-world career trajectories to find the perfect alignment for your goals.",
  },
  {
    title: "3) Personalized Pathway",
    description:
      "We calculate the exact knowledge gap you need to bridge. Using our recommendation engine, we rank courses and certifications that offer the highest employability 'ROI' for your specific target role.",
  },
  {
    title: "4) Success Guidance",
    description:
      "Get a clear, actionable roadmap. From resume optimization tips to direct learning links, we provide everything you need to confidently move forward in your career journey.",
  },
];

export default function HowThisWorksPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <div className="max-w-5xl mx-auto space-y-12 py-12 px-6">

        <section className="animate-fade-up text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-extrabold !text-slate-900 tracking-tight">
            The <span className="text-purple-600">PathFinder+</span> Advantage
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-slate-600 leading-relaxed">
            Experience a smarter way to plan your future. Our multi-stage AI process
            turns raw data into your personalized career roadmap.
          </p>
        </section>


        <section className="bg-white/60 rounded-[40px] p-2 md:p-8 border border-purple-300">
          <Stepper steps={steps} />
        </section>


        <section className="pt-4 grid md:grid-cols-2 gap-8 text-center md:text-left">
          <div className="p-8 rounded-3xl bg-white border border-purple-100 shadow-sm">
            <h3 className="text-xl font-bold text-slate-900">Why choose our AI?</h3>
            <p className="mt-3 text-slate-600">
              Unlike generic advice, we use real-time market data from LinkedIn, Paylab,
              and ESCO to ensure your recommendations are actually relevant.
            </p>
          </div>
          <div className="p-8 rounded-3xl bg-white border border-purple-100 shadow-sm">
            <h3 className="text-xl font-bold text-slate-900">Always Up-To-Date</h3>
            <p className="mt-3 text-slate-600">
              Our data scrapers run weekly to catch the latest job requirements
              and skill trends in the many industries we cover.
            </p>
          </div>
        </section>


        <section className="py-16 bg-white rounded-3xl border border-purple-100 px-6">
          <div className="w-full max-w-7xl px-4 md:px-5 mx-auto">
            <div className="w-full flex-col justify-start items-center lg:gap-12 gap-8 inline-flex">
              <div className="w-full flex-col justify-start items-center gap-3 flex">
                <span className="w-full text-center text-slate-500 text-base font-normal leading-relaxed">
                  How It Works
                </span>
                <h2 className="w-full text-center text-purple-700 text-4xl font-bold leading-normal">
                  Steps to Shape Your Career
                </h2>
              </div>

              <div className="w-full justify-start lg:items-start items-center lg:gap-16 gap-8 flex lg:flex-row flex-col">
                <img
                  className="object-cover max-w-md w-full rounded-2xl shadow-sm"
                  src="https://pagedone.io/asset/uploads/1720589731.png"
                  alt="How It Works illustration"
                />

                <div className="flex-1 w-full">
                  <div className="space-y-5">
                    {steps.map((step, i) => (
                      <div key={i} className="p-6 bg-white border border-purple-100 rounded-2xl shadow-sm">
                        <span className="text-purple-600 text-sm font-semibold tracking-wide uppercase">
                          Step {i + 1}
                        </span>
                        <h4 className="text-slate-900 text-lg font-semibold mt-1">
                          {step.title.replace(/^\d+\)\s*/, "")}
                        </h4>
                        <p className="mt-2 text-slate-500 text-sm leading-relaxed">{step.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Ambient grid of steps to show our processes for users to visualize */}
        <section className="relative bg-gradient-to-b from-purple-100 to-purple-50 py-16 rounded-[40px] overflow-hidden">

          <div
            className="absolute inset-0 m-auto max-w-xs h-[357px] blur-[118px] sm:max-w-md md:max-w-lg pointer-events-none"
            style={{
              background:
                "radial-gradient(ellipse at center, rgba(124,58,237,0.12) 0%, rgba(167,139,250,0.08) 50%, rgba(237,233,254,0.04) 100%)",
            }}
          />

          <div className="relative px-4 mx-auto max-w-5xl sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto text-center mb-12">
              <h2 className="text-4xl font-extrabold text-slate-900">How does it work?</h2>
              <p className="mt-4 text-slate-600 leading-relaxed">
                Our AI solution guides you from profile to placement with data-driven steps.
              </p>
            </div>

            <div className="relative">
              <div className="absolute inset-x-0 hidden top-8 md:block px-20 lg:px-28 xl:px-44">
                <img
                  alt="Curved dotted line"
                  loading="lazy"
                  width={1000}
                  height={500}
                  className="w-full opacity-30"
                  src="https://cdn.rareblocks.xyz/collection/celebration/images/steps/2/curved-dotted-line.svg"
                />
              </div>

              <div className="relative grid grid-cols-1 text-center gap-y-12 md:grid-cols-4 gap-x-8">
                {steps.map((s, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-center w-14 h-14 mx-auto bg-white border-2 border-purple-200 rounded-full shadow-sm">
                      <span className="text-lg font-bold text-purple-600">{i + 1}</span>
                    </div>
                    <h3 className="mt-6 text-base text-slate-900 font-semibold md:mt-10">
                      {s.title.replace(/^\d+\)\s*/, "")}
                    </h3>
                    <p className="mt-3 text-sm text-slate-600 leading-relaxed">{s.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}