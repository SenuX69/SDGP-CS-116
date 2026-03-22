"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function Dashboard() {

  const [name, setName] = useState("User");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if(storedName){
      setName(storedName);
    }
  }, []);

  return (
    <div className="min-h-screen bg-white text-black p-10">

      <p className="text-gray-500 mb-2">Your Progress so far</p>

      <h1 className="text-3xl font-bold mb-8">
        Hello {name}! What are you up for today?
      </h1>

      {/* ACTION BUTTONS */}
      <div className="flex gap-6 mb-10">

        <Link href="/upload-cv">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Upload CV
          </button>
        </Link>

        <Link href="/quiz">
          <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
            Take Quiz
          </button>
        </Link>

      </div>

      {/* YOUR EXISTING CONTENT BELOW */}
      <div className="mt-6">
        <p className="text-xl font-semibold">Current Trends</p>
        <p className="text-gray-600 mt-2">
          UI/UX opportunities from last month +11%
        </p>
      </div>

    </div>
  );
}