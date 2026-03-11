import Image from "next/image";

export default function CareerPathResult() {
  return (
    <div className="min-h-screen bg-white px-16 py-10">

      <h1 className="text-2xl font-semibold text-gray-800 mb-10">
        Career Path Mapping
      </h1>

      <div className="flex items-end gap-4 overflow-x-auto">

        {/* STEP 1 */}
        <div className="w-60 border rounded shadow bg-white">
          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            01
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Existing Career</h3>

            <p className="font-medium">Education</p>
            <p>BSc in Nursing</p>

            <p className="font-medium mt-3">Field of Study</p>

            <ul className="list-disc ml-4">
              <li>Health Care</li>
              <li>Technology Studies</li>
              <li>Engineering Studies</li>
            </ul>

          </div>
        </div>


        {/* STEP 2 */}
        <div className="w-60 border rounded shadow bg-white">
          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            02
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Field of Interest</h3>

            <ul className="list-disc ml-4">
              <li>Computer Occupations</li>
            </ul>

          </div>
        </div>


        {/* STEP 3 */}
        <div className="w-60 border rounded shadow bg-white">
          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            03
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Potential Careers</h3>

            <ul className="list-disc ml-4">
              <li>Computer Systems Analysts</li>
              <li>Information Security Analysts</li>
              <li>Computer Support Specialists</li>
              <li>Network Support Specialists</li>
            </ul>

          </div>
        </div>


        {/* STEP 4 */}
        <div className="w-60 border rounded shadow bg-white">
          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            04
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Recommended Actions</h3>

            <ul className="list-disc ml-4">
              <li>60 Hours Computer Systems Training</li>
              <li>Employer Certifications</li>
              <li>6 Month Course</li>
            </ul>

          </div>
        </div>


        {/* STEP 5 */}
        <div className="w-60 border rounded shadow bg-white">
          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            05
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Resources</h3>

            <ul className="list-disc ml-4">
              <li>FreeCodeCamp</li>
              <li>Cloud Practitioner Course</li>
              <li>AWS Cloud Exams</li>
            </ul>

          </div>
        </div>


        {/* STEP 6 */}
        <div className="w-60 border rounded shadow bg-white">

          <div className="bg-blue-700 text-white px-3 py-1 font-semibold">
            06
          </div>

          <div className="p-4 text-sm text-gray-700">

            <h3 className="font-semibold mb-2">Targets</h3>

            <ul className="list-disc ml-4">
              <li>AWS Cloud Practitioner</li>
              <li>Cloud Security Professional</li>
              <li>Data Privacy Engineer</li>
              <li>Certified Ethical Hacker</li>
            </ul>

          </div>

        </div>

      </div>

    </div>
  );
}