"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function ResultPage() {

  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {

    const saved = sessionStorage.getItem("careerData");

    if (!saved) {
      router.push("/career-path");
      return;
    }

    setData(JSON.parse(saved));

  }, []);

  if (!data) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        Loading career path....
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white px-16 py-14">

      <h1 className="text-3xl font-semibold text-gray-800 mb-16">
        Career Path Mapping
      </h1>

      <div className="relative flex items-end gap-8">

        {/* PERSON */}
        <div className="absolute left-[260px] -top-16">
          <Image
            src="/images/person.png"
            alt="person"
            width={120}
            height={120}
          />
        </div>

        {/* STEP 01 */}
        <Step
          number="01"
          title="Existing Career"
          content={[
            `Role: ${data.role}`,
            `Education: ${data.qualification}`
          ]}
        />

        {/* STEP 02 */}
        <Step
          number="02"
          title="Field of Interest"
          content={[data.interest]}
          offset="mb-10"
        />

        {/* STEP 03 */}
        <Step
          number="03"
          title="Potential Careers"
          content={[
            "Computer Systems Analyst",
            "Information Security Analyst",
            "Network Support Specialist"
          ]}
          offset="mb-20"
        />

        {/* STEP 04 */}
        <Step
          number="04"
          title="Recommended Actions"
          content={[
            "60 Hours Computer Training",
            "Employer Certifications",
            "6 Month Course"
          ]}
          offset="mb-30"
        />

        {/* STEP 05 */}
        <Step
          number="05"
          title="Resources"
          content={[
            "FreeCodeCamp",
            "AWS Course",
            "Cloud Practitioner"
          ]}
          offset="mb-40"
        />

        {/* STEP 06 */}
        <Step
          number="06"
          title="Targets"
          content={[
            "AWS Practitioner",
            "Cloud Security Professional",
            "Certified Ethical Hacker"
          ]}
          offset="mb-52"
        />

        {/* TROPHY */}
        <div className="absolute right-0 -top-28">
          <Image
            src="/images/trophy.png"
            alt="trophy"
            width={140}
            height={140}
          />
        </div>

      </div>

    </div>
  );
}


function Step({ number, title, content, offset = "" }: any) {

  return (
    <div className={`w-[220px] bg-white border rounded-lg shadow-md ${offset}`}>

      <div className="bg-blue-600 text-white px-3 py-2 font-semibold">
        {number}
      </div>

      <div className="p-4">

        <h3 className="font-semibold text-gray-800 mb-2">
          {title}
        </h3>

        <ul className="text-sm text-gray-700 space-y-1">
          {content.map((item: string, index: number) => (
            <li key={index}>• {item}</li>
          ))}
        </ul>

      </div>

    </div>
  );
}