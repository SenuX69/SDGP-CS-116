"use client";

import { useEffect, useRef } from "react";

export default function FeatureTimeline() {
    const features = [
        "Resume Analysis & Builder",
        "Career Recommendations & Matcher",
        "AI Chatbot for Career Questions",
        "Skills Assessment & Gap Analysis",
        "Career Path Visualizer",
        "Higher Education Planning",
        "Job Market Trends & Insights",
        "Mentorship System (Premium)",
    ];

    const itemsRef = useRef<(HTMLDivElement | null)[]>([]);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("reveal-active");
                    }
                });
            },
            { threshold: 0.15 }
        );

        itemsRef.current.forEach((el) => {
            if (el) observer.observe(el);
        });

        return () => observer.disconnect();
    }, []);

    return (
        <section className="bg-white py-24">
            <div className="max-w-5xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-20">
                    <h2 className="text-3xl md:text-4xl font-bold text-slate-900">
                        Your Career Journey with Pathfinder+
                    </h2>
                    <p className="mt-4 text-slate-600">
                        A step-by-step AI-powered path from exploration to success.
                    </p>
                </div>

                {/* Timeline */}
                <div className="relative mx-auto max-w-sm">

                    {/* Vertical Line */}
                    <div className="absolute left-6 top-0 h-full w-px bg-slate-200" />

                    <div className="space-y-14">
                        {features.map((feature, index) => (
                            <div
                                key={index} ref={(el) => {
                                    itemsRef.current[index] = el;
                                }}

                                className="reveal flex items-start gap-8"
                            >

                                {/* Icon */}
                                <div className="relative z-10 flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600 text-white font-semibold shadow-md">
                                    ✓
                                </div>

                                {/* Card */}
                                <div className="
                                        bg-slate-50 border border-slate-200 rounded-xl
                                        px-6 py-4 shadow-sm
                                        transition-all duration-300
                                        hover:-translate-y-1 hover:shadow-md
                                ">
                                    <p className="text-slate-900 font-medium">
                                        {feature}
                                    </p>
                                </div>

                            </div>
                        ))}
                    </div>

                </div>
            </div>
        </section>
    );
}
