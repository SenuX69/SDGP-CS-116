"use client";

import Image from "next/image";

export default function Dashboard() {

return (

<div className="min-h-screen bg-gray-50 text-black">

{/* NAVBAR */}

<nav className="flex justify-between items-center px-10 py-4 border-b bg-white">

<div className="flex items-center gap-3">

<Image
src="/images/logo.png"
alt="logo"
width={40}
height={40}
/>

<span className="font-semibold text-lg">
PathFinder
</span>

</div>

<div className="flex gap-8 text-gray-700">

<p className="text-blue-500 font-medium">Home</p>
<p>Career Path</p>
<p>Courses</p>
<p>Jobs</p>
<p>Mentorship</p>
<p>Dashboard</p>

</div>

<div className="flex items-center gap-4">

<Image
src="/images/user.png"
alt="user"
width={35}
height={35}
className="rounded-full"
/>

</div>

</nav>


{/* CONTENT */}

<div className="px-16 py-10">

<h2 className="text-xl text-gray-600">
Your Progress so far
</h2>

<h1 className="text-3xl font-semibold mt-2">
Hello John! What are you up for today?
</h1>


{/* PROGRESS CARDS */}

<div className="flex gap-20 mt-12">

<div className="text-center">

<p className="text-2xl font-semibold">56%</p>
<p className="text-gray-500">Career Readiness</p>

</div>

<div className="text-center">

<p className="text-2xl font-semibold">8/12</p>
<p className="text-gray-500">Skill Analysis</p>

</div>

<div className="text-center">

<p className="text-2xl font-semibold">8/12</p>
<p className="text-gray-500">Job Recommendations</p>

</div>

</div>


{/* CURRENT TRENDS */}

<h2 className="text-2xl font-semibold mt-16">
Current Trends
</h2>

<p className="text-gray-600 mt-3">
UI/UX opportunities from last month +11%
</p>

<button className="mt-8 bg-cyan-500 text-white px-6 py-3 rounded-full">
Resume Creation / Analysis
</button>

</div>


{/* CHATBOT BUTTON */}

<div className="fixed bottom-8 right-8">

<button className="bg-blue-500 w-16 h-16 rounded-full flex items-center justify-center">

<Image
src="/images/chatbot.png"
alt="chatbot"
width={30}
height={30}
/>

</button>

</div>

</div>

);

}