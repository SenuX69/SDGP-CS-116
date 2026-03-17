"use client";

import { useEffect, useState } from "react";

export default function ResultsPage() {

  const [data, setData] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("resultData");
    if (stored) {
      setData(JSON.parse(stored));
    }
  }, []);

  if (!data) {
    return <div className="p-10">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 px-10 py-10">

      {/* TITLE */}
      <h1 className="text-3xl font-bold mb-8">
        🎯 Your Career Recommendation
      </h1>

      {/* MAIN CARD */}
      <div className="bg-white shadow-md rounded-xl p-8 mb-8">

        <h2 className="text-2xl font-semibold text-red-500 mb-2">
          {data.career}
        </h2>

        <p className="text-gray-600">
          {data.description}
        </p>

      </div>

      {/* GRID SECTIONS */}
      <div className="grid grid-cols-3 gap-6">

        {/* SKILLS */}
        <div className="bg-white shadow rounded-xl p-6">
          <h3 className="font-semibold mb-4 text-lg">🛠 Skills to Learn</h3>
          <ul className="space-y-2 text-gray-700">
            {data.skills.map((s, i) => (
              <li key={i} className="bg-gray-100 px-3 py-2 rounded">
                {s}
              </li>
            ))}
          </ul>
        </div>

        {/* COURSES */}
        <div className="bg-white shadow rounded-xl p-6">
          <h3 className="font-semibold mb-4 text-lg">🎓 Recommended Courses</h3>
          <ul className="space-y-2 text-gray-700">
            {data.courses.map((c, i) => (
              <li key={i} className="bg-gray-100 px-3 py-2 rounded">
                {c}
              </li>
            ))}
          </ul>
        </div>

        {/* JOBS */}
        <div className="bg-white shadow rounded-xl p-6">
          <h3 className="font-semibold mb-4 text-lg">💼 Job Opportunities</h3>
          <ul className="space-y-2 text-gray-700">
            {data.jobs.map((j, i) => (
              <li key={i} className="bg-gray-100 px-3 py-2 rounded">
                {j}
              </li>
            ))}
          </ul>
        </div>

      </div>

    </div>
  );
}