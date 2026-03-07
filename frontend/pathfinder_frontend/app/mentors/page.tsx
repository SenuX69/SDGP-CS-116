
import Link from 'next/link';
import Image from 'next/image';

const MOCK_MENTORS = [
    {
        id: 1,
        name: "Dr. Aruni Gunawardena",
        title: "Senior Machine Learning Engineer",
        company: "WSO2",
        expertise: ["Computer Vision", "PyTorch", "MLOps"],
        matching_score: 98,
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Aruni",
        bio: "Passionate about building scalable AI systems and mentoring the next generation of Sri Lankan tech leaders."
    },
    {
        id: 2,
        name: "Kumari Ranasinghe",
        title: "Lead Data Scientist",
        company: "Dialog Axiata",
        expertise: ["Predictive Analytics", "Tableau", "SQL"],
        matching_score: 92,
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Kumari",
        bio: "Helping professionals transition into data roles through practical project mentorship."
    },
    {
        id: 3,
        name: "Dilshan Fernando",
        title: "Software Architect",
        company: "LSEG Technology",
        expertise: ["Cloud Arch", "Go", "Kubernetes"],
        matching_score: 85,
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Dilshan",
        bio: "Specialist in high-frequency trading platforms and distributed systems."
    }
];

export default function MentorsPage() {
    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2">
                    <Image src="/logonb.png" alt="PathFinder+ Logo" width={32} height={32} />
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600">
                        PathFinder+
                    </span>
                </Link>
                <div className="flex gap-8 text-sm font-medium text-gray-500">
                    <Link href="/skill-assessment" className="hover:text-purple-600 transition-colors">Assessment</Link>
                    <Link href="/resumes" className="hover:text-purple-600 transition-colors">Resumes</Link>
                    <Link href="/mentors" className="text-purple-600 font-semibold border-b-2 border-purple-600 pb-1">Mentors</Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="max-w-7xl mx-auto px-6 py-16 text-center animate-fade-in">
                <h1 className="text-5xl font-black tracking-tight text-gray-900 mb-4">
                    Expert Mentors for Your <span className="text-purple-600">Growth</span>
                </h1>
                <p className="text-xl text-gray-500 max-w-2xl mx-auto">
                    Connect with industry leaders from Sri Lanka's top tech companies,
                    handpicked to match your specific career goals.
                </p>
            </section>

            {/* Mentor Grid */}
            <main className="max-w-7xl mx-auto px-6 pb-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {MOCK_MENTORS.map((mentor) => (
                    <div
                        key={mentor.id}
                        className="group relative bg-white border border-gray-100 rounded-3xl p-8 hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-500 ease-out hover:-translate-y-2 overflow-hidden"
                    >
                        {/* Background Decoration */}
                        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-purple-50 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />

                        <div className="flex items-start justify-between mb-6">
                            <div className="w-20 h-20 rounded-2xl overflow-hidden ring-4 ring-white shadow-lg transition-transform group-hover:scale-110 duration-500">
                                <img src={mentor.avatar} alt={mentor.name} className="w-full h-full object-cover" />
                            </div>
                            <div className="bg-purple-50 text-purple-600 px-3 py-1 rounded-full text-xs font-bold ring-1 ring-purple-100">
                                {mentor.matching_score}% Match
                            </div>
                        </div>

                        <h3 className="text-xl font-bold text-gray-900 mb-1 leading-tight">{mentor.name}</h3>
                        <p className="text-sm font-semibold text-purple-600 mb-4">{mentor.title} @ <span className="text-gray-900">{mentor.company}</span></p>

                        <p className="text-sm text-gray-500 mb-6 line-clamp-2 italic leading-relaxed">
                            "{mentor.bio}"
                        </p>

                        <div className="flex flex-wrap gap-2 mb-8">
                            {mentor.expertise.map((skill) => (
                                <span key={skill} className="px-3 py-1 bg-gray-50 text-gray-600 text-[10px] font-bold uppercase tracking-wider rounded-lg ring-1 ring-gray-100 group-hover:bg-white transition-colors">
                                    {skill}
                                </span>
                            ))}
                        </div>

                        <button className="w-full py-4 bg-gray-900 text-white font-bold rounded-2xl hover:bg-purple-600 transition-all duration-300 transform active:scale-95 shadow-xl shadow-gray-200">
                            Connect on LinkedIn
                        </button>
                    </div>
                ))}
            </main>

            <style jsx>{`
        .animate-fade-in {
          animation: fadeIn 0.8s ease-out forwards;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
        </div>
    );
}
