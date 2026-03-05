"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, Variants } from "framer-motion";

const sources = [
    {
        category: "Learning Infrastructure",
        items: [
            {
                name: "Pickacourse",
                desc: "Primary aggregator for Sri Lankan higher education and vocational training paths.",
                logo: "/team/pickacourse.png"
            },
            {
                name: "Class Central",
                desc: "Global MOOC database providing normalized course metadata across 100+ platforms.",
                logo: "/team/cclogo.png"
            }
        ]
    },
    {
        category: "Employment Hubs",
        items: [
            {
                name: "XpressJobs",
                desc: "Connecting with active Sri Lankan job postings for real-world skill-gap verification.",
                logo: "/team/xpressjobs_logo.jpg"
            },
            {
                name: "TopJobs",
                desc: "Capturing structured data from established local recruitment interfaces.",
                logo: "/team/topjobs.jpg"
            }
        ]
    },
    {
        category: "Analytical Metadata",
        items: [
            {
                name: "Paylab",
                desc: "Salary benchmark engine feeding the recommendation ROI calculations.",
                logo: "/team/paylab.png"
            },
            {
                name: "ESCO Framework",
                desc: "The European Skills, Competences, and Occupations framework for career mapping.",
                logo: "/team/esco.webp"
            }
        ]
    }
];

const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.1 }
    }
};

const itemVariants: Variants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
        y: 0,
        opacity: 1,
        transition: { type: "spring", stiffness: 120 }
    }
};

export default function DataSourcesPage() {
    return (
        <main className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-violet-100 selection:text-violet-900">
            {/* Minimalist Background Texture */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,_#f1f5f9_0%,_transparent_100%)]"></div>
                <div className="absolute top-0 left-0 w-full h-full opacity-[0.4]" style={{ backgroundImage: 'radial-gradient(#e2e8f0 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
            </div>

            <div className="relative max-w-6xl mx-auto px-6 py-24">
                {/* Clean Professional Hero */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 5 }}
                    className="mb-32 text-center"
                >

                    <h1 className="text-4xl md:text-6xl font-bold text-slate-900 tracking-tight mb-8">
                        The data that power <span className="text-blue-600 font-bold">PathFinder+</span>
                    </h1>
                    <p className="text-slate-500 text-lg max-w-2xl mx-auto leading-relaxed font-medium">
                        We aggregate thousands of data points from local and global sources to build your career trajectory with clinical precision.
                    </p>
                </motion.div>

                {/* Sources Feed */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="space-y-24"
                >
                    {sources.map((section) => (
                        <div key={section.category}>
                            <div className="flex items-center gap-6 mb-12">
                                <h2 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.5em] whitespace-nowrap">{section.category}</h2>
                                <div className="h-[1px] flex-1 bg-slate-200"></div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-8">
                                {section.items.map((item) => (
                                    <motion.div
                                        key={item.name}
                                        variants={itemVariants}
                                        whileHover={{ y: -4, borderColor: '#8b5cf6' }}
                                        className="relative p-10 bg-white border border-slate-200 rounded-3xl shadow-sm hover:shadow-xl hover:shadow-violet-200/40 transition-all duration-300 group/card"
                                    >
                                        <div className="flex flex-col sm:flex-row items-start gap-10">
                                            <div className="flex-shrink-0 w-20 h-20 rounded-2xl bg-white border border-slate-100 flex items-center justify-center p-3 shadow-sm group-hover/card:border-violet-100 transition-colors">
                                                <Image
                                                    src={item.logo}
                                                    alt={item.name}
                                                    width={64}
                                                    height={64}
                                                    className="group-hover/card transition-all duration-500 scale-95 group-hover/card:scale-105"
                                                />
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="text-xl font-bold text-slate-900 mb-4 group-hover/card:text-violet-600 transition-colors">{item.name}</h3>
                                                <p className="text-slate-500 leading-relaxed text-sm">
                                                    {item.desc}
                                                </p>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    ))}
                </motion.div>


            </div>
        </main>
    );
}
