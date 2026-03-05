export const metadata = {
  title: "Privacy Policy - PathFinder+",
  description: "Privacy policy for PathFinder+ - how we collect and use data.",
};

const CheckIcon = () => (
  <svg className="mt-1 size-5 flex-none text-purple-700" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
  </svg>
);

export default function PrivacyPage() {
  return (
    <div className="bg-purple-50 min-h-screen px-6 py-24 sm:py-32 lg:px-8">
      <div className="mx-auto max-w-3xl text-base leading-7 text-black">
        <p className="text-base font-bold leading-7 text-purple-700 uppercase tracking-widest">Legal Documents</p>
        <h1 className="mt-2 text-4xl font-extrabold tracking-tight text-black sm:text-5xl">Privacy Policy</h1>
        <p className="mt-6 text-xl leading-8 text-black/80">
          Last updated: March 20 2026. This policy explains what information PathFinder+ collects, why we collect it, and how you can manage your data.
        </p>

        <div className="mt-10 max-w-2xl">

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-black border-b border-purple-200 pb-2">Introduction</h2>
            <p className="mt-6 text-black">
              PathFinder+ respects your privacy and is committed to protecting your personal data. This policy applies to all users of our career guidance platform and AI-powered services.
            </p>
          </section>

          <section className="mt-16">
            <h2 className="text-2xl font-bold tracking-tight text-black border-b border-purple-200 pb-2">Information We Collect</h2>
            <p className="mt-6 text-black">
              To provide personalized career insights, we collect information you provide directly to us:
            </p>
            <ul role="list" className="mt-8 max-w-xl space-y-4 text-black">
              <li className="flex gap-x-3">
                <CheckIcon />
                <span><strong className="font-bold">Profile data:</strong> Your name, email, education history, and current skill sets.</span>
              </li>
              <li className="flex gap-x-3">
                <CheckIcon />
                <span><strong className="font-bold">Professional Interests:</strong> Job roles you are targeting and salary expectations.</span>
              </li>
              <li className="flex gap-x-3">
                <CheckIcon />
                <span><strong className="font-bold">External Metadata:</strong> Publicly available job postings and ESCO taxonomy links used for skill mapping.</span>
              </li>
            </ul>
          </section>


          <section className="mt-16">
            <h2 className="text-2xl font-bold tracking-tight text-black border-b border-purple-200 pb-2">How We Use Your Data</h2>
            <p className="mt-6 text-black">
              We process your information to deliver the core PathFinder+ experience, specifically for:
            </p>
            <ul role="list" className="mt-8 max-w-xl space-y-4 text-black">
              <li className="flex gap-x-3">
                <CheckIcon />
                <span>Generating personalized learning pathways and course rankings.</span>
              </li>
              <li className="flex gap-x-3">
                <CheckIcon />
                <span>Refining our AI Mentor responses based on aggregated user interactions.</span>
              </li>
              <li className="flex gap-x-3">
                <CheckIcon />
                <span>Matching your profile against live market trends and job descriptions.</span>
              </li>
            </ul>
          </section>


          <section className="mt-16">
            <h2 className="text-2xl font-bold tracking-tight text-black border-b border-purple-200 pb-2">Data Security & Disclosure</h2>
            <p className="mt-6 text-black">
              We take reasonable measures to protect data, including encryption at rest and in transit. <strong className="font-black underline">We do not sell your personal data to third parties.</strong> We may share anonymized, aggregated data with industry partners to improve regional employment insights.
            </p>
          </section>


          <section className="mt-16">
            <h2 className="text-2xl font-bold tracking-tight text-black border-b border-purple-200 pb-2">Your Rights</h2>
            <p className="mt-6 text-black font-medium">
              You have the right to access, correct, or request the deletion of your personal information at any time.
            </p>
            <div className="mt-10 flex">
              <a
                href="mailto:pathfinderplus@gmail.com"
                className="inline-flex items-center rounded-lg bg-black px-6 py-3 text-sm font-bold text-white shadow-sm hover:bg-purple-900 transition-colors"
              >
                Contact our data team <span className="ml-2" aria-hidden="true">&rarr;</span>
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}