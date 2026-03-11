"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CareerPath() {

  const router = useRouter();

  const [form, setForm] = useState({
    role: "",
    qualification: "",
    field: "",
    reason: "",
    interest: "",
    jobStatus: "",
    payCourses: "",
    digitalSkill: "",
    timeCommitment: "",
    language: ""
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {

    setSubmitted(true);

    if (
      !form.role ||
      !form.qualification ||
      !form.interest ||
      !form.jobStatus ||
      !form.payCourses ||
      !form.digitalSkill ||
      !form.timeCommitment ||
      !form.language
    ) {
      return;
    }

    sessionStorage.setItem("careerData", JSON.stringify(form));

    router.push("/career-path/result");
  };

  const inputStyle =
    "w-full border border-gray-300 rounded-lg p-3 mt-1 bg-white text-gray-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500";

  const errorInput =
    "w-full border border-red-400 rounded-lg p-3 mt-1 bg-white text-gray-800 focus:border-red-400 focus:ring-1 focus:ring-red-400";

  return (
    <div className="w-full min-h-screen bg-white px-16 py-10">

      <h1 className="text-3xl font-semibold text-gray-800 mb-12">
        Skill Assessment
      </h1>

      <div className="grid grid-cols-2 gap-20">

        {/* LEFT SIDE */}
        <div className="space-y-6">

          <div>
            <label className="text-sm font-medium text-gray-800">
              Current Role*
            </label>

            <input
              name="role"
              placeholder="Enter role"
              value={form.role}
              onChange={handleChange}
              className={submitted && !form.role ? errorInput : inputStyle}
            />
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Highest Qualification Obtained*
            </label>

            <input
              name="qualification"
              placeholder="Enter Qualification"
              value={form.qualification}
              onChange={handleChange}
              className={submitted && !form.qualification ? errorInput : inputStyle}
            />
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Type of Field (If Working)
            </label>

            <input
              name="field"
              placeholder="Enter Field"
              value={form.field}
              onChange={handleChange}
              className={inputStyle}
            />
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Reason for switching fields
            </label>

            <input
              name="reason"
              placeholder="Enter Reason"
              value={form.reason}
              onChange={handleChange}
              className={inputStyle}
            />
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Field Interested In*
            </label>

            <input
              name="interest"
              placeholder="Enter Field"
              value={form.interest}
              onChange={handleChange}
              className={submitted && !form.interest ? errorInput : inputStyle}
            />
          </div>


                  <div>

                      <p className="text-sm font-medium text-gray-800 mb-3">
                          Preferred Language*
                      </p>

                      <div className="space-y-3">

                          <label className="flex items-center gap-3 text-gray-800 cursor-pointer">

                              <input
                                  type="radio"
                                  name="language"
                                  value="English"
                                  onChange={handleChange}
                                  className="accent-blue-600 w-4 h-4"
                              />

                              English

                          </label>


                          <label className="flex items-center gap-3 text-gray-800 cursor-pointer">

                              <input
                                  type="radio"
                                  name="language"
                                  value="Sinhala"
                                  onChange={handleChange}
                                  className="accent-blue-600 w-4 h-4"
                              />

                              Sinhala

                          </label>


                          <label className="flex items-center gap-3 text-gray-800 cursor-pointer">

                              <input
                                  type="radio"
                                  name="language"
                                  value="Tamil"
                                  onChange={handleChange}
                                  className="accent-blue-600 w-4 h-4"
                              />

                              Tamil

                          </label>

                      </div>

</div>

        </div>


        {/* RIGHT SIDE */}
        <div className="space-y-8">

          <div>
            <label className="text-sm font-medium text-gray-800">
              Job Status*
            </label>

            <select
              name="jobStatus"
              value={form.jobStatus}
              onChange={handleChange}
              className={submitted && !form.jobStatus ? errorInput : inputStyle}
            >
              <option value="">Select</option>
              <option>Employed</option>
              <option>Unemployed</option>
              <option>Committed to Studies</option>
            </select>
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Willing to pay for courses?*
            </label>

            <select
              name="payCourses"
              value={form.payCourses}
              onChange={handleChange}
              className={submitted && !form.payCourses ? errorInput : inputStyle}
            >
              <option value="">Select</option>
              <option>Yes</option>
              <option>No</option>
              <option>Free / Low Cost</option>
            </select>
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Digital Skill Level*
            </label>

            <select
              name="digitalSkill"
              value={form.digitalSkill}
              onChange={handleChange}
              className={submitted && !form.digitalSkill ? errorInput : inputStyle}
            >
              <option value="">Select</option>
              <option>No Experience</option>
              <option>Basic Understanding</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </div>


          <div>
            <label className="text-sm font-medium text-gray-800">
              Time Commitment*
            </label>

            <select
              name="timeCommitment"
              value={form.timeCommitment}
              onChange={handleChange}
              className={submitted && !form.timeCommitment ? errorInput : inputStyle}
            >
              <option value="">Select</option>
              <option>Less than 10 hours</option>
              <option>10-25 hours</option>
              <option>25-40 hours</option>
              <option>More than 40 hours</option>
            </select>
          </div>

        </div>

      </div>

      <button
        onClick={handleSubmit}
        className="mt-12 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        Submit Assessment
      </button>

    </div>
  );
}