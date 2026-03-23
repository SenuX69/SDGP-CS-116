"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardBody, Button, Chip, Progress } from "@heroui/react";
import { Upload, Target, TrendingUp, Sparkles, BookOpen, Briefcase, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";


/--#Welcome Greetings #----/ 
export default function Dashboard() {
  const [name, setName] = useState("User");
  const [greeting, setGreeting] = useState("Hello");
  const [profileStatus, setProfileStatus] = useState<any>({
    completion: 0,
    message: "Upload your CV or take the Quiz to unlock your personalized career roadmap.",
    state: "NEW",
    missing: ["cv", "quiz"],
    cachedResults: {}
  });

  const [marketTrends, setMarketTrends] = useState<any[]>([
    { title: "Software Engineering", jobs_active: 150 },
    { title: "Data Analytics", jobs_active: 85 },
    { title: "UI/UX Design", jobs_active: 75 },
    { title: "Product Management", jobs_active: 60 }
  ]);

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if(storedName){
      setName(storedName);
    }
    
    // Explicit Profile State Engine Hydration
    const fetchProfileStatus = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login";
          return;
        }

        const res = await fetch("http://localhost:8000/api/profile/status", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        if (res.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setProfileStatus({
            completion: data.completion_percentage || 0,
            message: data.message || "Complete your profile to unlock actionable ML insights.",
            state: data.state || "NEW",
            missing: data.missing_components || [],
            cachedResults: data.cached_results || {}
          });
        }
      } catch (e) {
        console.error("Failed to fetch profile status", e);
      }
    };
    fetchProfileStatus();
    
    // Dynamically pull real market trends from PyTorch backend based natively on User Domain
    const fetchMarketTrends = async () => {
      try {
        let url = "http://localhost:8000/api/market-trends";
        const savedDomain = localStorage.getItem("userDomain");
        if (savedDomain && savedDomain !== "undefined") {
          url += `?domain=${encodeURIComponent(savedDomain)}`;
        }

        const res = await fetch(url);
        const data = await res.json();
        if (data && data.trends) {
          setMarketTrends(data.trends);
        }
      } catch (e) {
        console.error("Using localized trends fallback", e);
      }
    };
    
    fetchMarketTrends();
    
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <main className="min-h-screen relative bg-slate-50 dark:bg-zinc-950 pattern-bg flex flex-col">
      <Navbar />
      <div className="max-w-7xl mx-auto space-y-12 py-10 px-4 sm:px-8 lg:px-16 w-full">
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-3 text-secondary-500 font-semibold mb-2">
            <Sparkles size={20} className="text-secondary-500" />
            <span className="uppercase tracking-widest text-sm">Your Progress So Far</span>
          </div>
          <h1 className="text-5xl font-black font-sora bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
            {greeting}, <span className="text-secondary-500">{name}</span>!
          </h1>
          <p className="text-xl text-foreground/60 font-medium">What are we focusing on today?</p>
        </motion.div>

        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <motion.div variants={itemVariants}>
            <Card className="border border-divider bg-gradient-to-br from-indigo-500/10 to-purple-600/10 backdrop-blur-xl shadow-xl hover:shadow-2xl hover:border-indigo-500/50 transition-all cursor-pointer group">
              <CardBody className="p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-8 md:gap-12">
                <div className="flex-1 space-y-4 text-center md:text-left">
                  <div className="flex flex-col md:flex-row items-center gap-3 justify-center md:justify-start">
                    <div className="p-3 rounded-2xl bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-500 group-hover:text-white transition-all duration-300">
                      <Target size={28} />
                    </div>
                    <Chip color="secondary" variant="flat" size="sm" className="font-bold tracking-widest uppercase">Core Hub</Chip>
                  </div>
                  <div>
                    <h3 className="text-3xl font-black font-sora text-slate-800 dark:text-slate-100">Career Assessment Center</h3>
                    <p className="text-foreground/70 text-lg mt-2 max-w-2xl mx-auto md:mx-0 font-medium">
                      Take the deep behavioral PyTorch quiz or fast-track the pipeline by uploading your Resume PDF. Our SBERT models will automatically map your vectors into the live Sri Lankan market.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
                  <Button 
                    as={Link} 
                    href="/skill-assessment" 
                    color="secondary" 
                    size="lg"
                    className="font-bold shadow-xl shadow-indigo-500/20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-8 text-md transition-transform hover:scale-[1.02]"
                    endContent={<ArrowRight size={20} />}
                  >
                    Enter Assessment
                  </Button>
                  <Button 
                    as={Link} 
                    href="/resumes" 
                    color="primary" 
                    variant="flat"
                    size="lg"
                    className="font-bold px-8 py-8 text-md border-2 border-primary-500/30 bg-primary-50/50 dark:bg-primary-900/10 transition-transform hover:scale-[1.02]"
                  >
                    ATS CV Analyzer
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </motion.div>

        {/* Current Trends & Stats */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 lg:grid-cols-4 gap-6"
        >
          <Card className="lg:col-span-3 border border-divider bg-content2/30 backdrop-blur-md shadow-lg">
            <CardBody className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp size={24} className="text-warning-500" />
                <h3 className="text-xl font-bold font-sora">Market Trends</h3>
              </div>
              <div className="grid sm:grid-cols-2 gap-6">
                {marketTrends.map((trend, i) => (
                  <div key={i} className="p-5 rounded-2xl bg-background shadow-sm border border-divider">
                    <p className="text-sm font-semibold text-foreground/60 uppercase tracking-wider mb-2">Demand Surge</p>
                    <p className="text-2xl font-black text-foreground truncate" title={trend.title}>{trend.title}</p>
                    <p className="text-success-500 font-bold mt-2 flex items-center gap-1"><TrendingUp size={16}/> {trend.jobs_active || "70+"} active jobs</p>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card className="border border-divider bg-content2/30 backdrop-blur-md shadow-lg">
            <CardBody className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <BookOpen size={24} className="text-secondary-500" />
                <h3 className="text-xl font-bold font-sora">Your Activity</h3>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span>Profile Completion</span>
                    <span className="text-secondary-500">{profileStatus.completion}%</span>
                  </div>
                  <Progress aria-label="Profile Completion Status" id="static-profile-progress-bar" value={profileStatus.completion || 0} color="secondary" size="sm" classNames={{ indicator: "bg-gradient-to-r from-secondary-400 to-primary-500" }} />
                </div>
                <div>
                  <p className="text-sm text-foreground/70 mb-4 font-medium">
                    {profileStatus.message}
                  </p>

                  {/* Dynamic Action Buttons based on missing core ML dependencies */}
                  {profileStatus.completion < 100 && (
                     <div className="flex gap-3 mt-4">
                       {profileStatus.missing?.includes("cv") && (
                         <Button as={Link} href="/upload-cv" color="secondary" variant="flat" size="sm" className="font-bold flex-1" endContent={<Upload size={16} />}>Upload CV</Button>
                       )}
                     </div>
                  )}

                  {profileStatus.completion >= 100 && profileStatus.cachedResults?.career_readiness && (
                    <div className="mt-6 space-y-4">
                      <div className="p-4 rounded-xl bg-indigo-50 dark:bg-zinc-800/50 border border-indigo-100 dark:border-zinc-700">
                        <p className="text-xs uppercase font-bold text-indigo-500 mb-1 tracking-wider">Calculated Readiness</p>
                        <h4 className="text-2xl font-black">{profileStatus.cachedResults.career_readiness.overall}/100</h4>
                      </div>
                      <Button as={Link} href="/results" color="secondary" size="md" className="font-bold shadow-md shadow-indigo-500/30 bg-gradient-to-r from-indigo-500 to-purple-500 text-white w-full h-12">
                        View Complete Roadmap <ArrowRight size={18} className="ml-2" />
                      </Button>
                    </div>
                  )}
                  {profileStatus.completion >= 100 && !profileStatus.cachedResults?.career_readiness && (
                    <Button as={Link} href="/results" color="secondary" size="md" className="font-bold shadow-md shadow-indigo-500/30 bg-gradient-to-r from-indigo-500 to-purple-500 text-white w-full h-12">
                      View Computed Roadmap <ArrowRight size={18} className="ml-2" />
                    </Button>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>
        </motion.div>

      </div>
    </main>
  );
}
