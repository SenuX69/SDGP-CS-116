"use client";

import { useState } from "react";

export default function CareerPath() {

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

    alert("Assessment Submitted!");
  };

  const inputStyle =
    "w-full border border-gray-300 rounded-lg p-3 mt-1 bg-white text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500";

  const errorInput =
    "w-full border border-red-400 rounded-lg p-3 mt-1 bg-white text-gray-800 placeholder-gray-400 focus:outline-none focus:border-red-400 focus:ring-1 focus:ring-red-400";

  return (
    <div className="w-full min-h-screen bg-white px-16 py-10">

      <h1 className="text-3xl font-semibold text-gray-800 mb-12">
        Skill Assessment
      </h1>

      <div className="grid grid-cols-2 gap-20">

        {/* LEFT SIDE */}
        <div className="space-y-6">

          {/* CURRENT ROLE */}
          <div>
            <label className="text-sm text-gray-800 font-medium">
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

          {/* QUALIFICATION */}
          <div>
            <label className="text-sm text-gray-800 font-medium">
              Highest Qualification Obtained (Ex: O/L, BSc)*
            </label>

            <input
              name="qualification"
              placeholder="Enter Qualification"
              value={form.qualification}
              onChange={handleChange}
              className={submitted && !form.qualification ? errorInput : inputStyle}
            />
          </div>

          {/* FIELD */}
          <div>
            <label className="text-sm text-gray-800 font-medium">
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

          {/* REASON */}
          <div>
            <label className="text-sm text-gray-800 font-medium">
              Reason for switching fields (if so)
            </label>

            <input
              name="reason"
              placeholder="Enter Reason"
              value={form.reason}
              onChange={handleChange}
              className={inputStyle}
            />
          </div>

          {/* FIELD INTERESTED */}
          <div>
            <label className="text-sm text-gray-800 font-medium">
              Enter Field Interested In
            </label>

            <input
              name="interest"
              placeholder="Enter Field"
              value={form.interest}
              onChange={handleChange}
              className={submitted && !form.interest ? errorInput : inputStyle}
            />

            {submitted && !form.interest && (
              <p className="text-red-500 text-sm mt-1">
                Please Complete the field with an actual Field of Work
              </p>
            )}
          </div>

          {/* LANGUAGE */}
          <div>

            <p className="text-sm text-gray-800 font-medium mb-3">
              Preferred Language of Choice
            </p>

            <div className="space-y-2">

              <label className="flex items-center gap-2 text-gray-700">
                <input
                  type="radio"
                  name="language"
                  value="English"
                  onChange={handleChange}
                />
                English
              </label>

              <label className="flex items-center gap-2 text-gray-700">
                <input
                  type="radio"
                  name="language"
                  value="Sinhala"
                  onChange={handleChange}
                />
                Sinhala
              </label>

              <label className="flex items-center gap-2 text-gray-700">
                <input
                  type="radio"
                  name="language"
                  value="Tamil"
                  onChange={handleChange}
                />
                Tamil
              </label>

            </div>

          </div>

        </div>


        {/* RIGHT SIDE */}
        <div className="space-y-10">

          {/* JOB STATUS */}
          <div>

            <label className="text-sm text-gray-800 font-medium">
              Job Status
            </label>

            <select
              name="jobStatus"
              value={form.jobStatus}
              onChange={handleChange}
              className={submitted && !form.jobStatus ? errorInput : inputStyle}
            >
              <option value="">Select Answer</option>
              <option>Employed</option>
              <option>Unemployed</option>
              <option>Committed to Studies</option>
            </select>

          </div>

          {/* PAY FOR COURSES */}
          <div>

            <label className="text-sm text-gray-800 font-medium">
              Are you willing to pay for courses?
            </label>

            <select
              name="payCourses"
              value={form.payCourses}
              onChange={handleChange}
              className={submitted && !form.payCourses ? errorInput : inputStyle}
            >
              <option value="">Select Answer</option>
              <option>Yes</option>
              <option>No</option>
              <option>Free or Low cost Courses would be appropriate</option>
            </select>

          </div>


          {/* DIGITAL SKILLS */}
          <div>

            <label className="text-sm text-gray-800 font-medium">
              How confident are you with Digital Skills
            </label>

            <select
              name="digitalSkill"
              value={form.digitalSkill}
              onChange={handleChange}
              className={submitted && !form.digitalSkill ? errorInput : inputStyle}
            >
              <option value="">Select Level</option>
              <option>No Experience prior</option>
              <option>Basic Understanding</option>
              <option>Comfortable with certain tools (ex: Photoshop)</option>
              <option>Intermediate Level Knowledge</option>
              <option>Expert</option>
            </select>

          </div>


          {/* TIME COMMITMENT */}
          <div>

            <label className="text-sm text-gray-800 font-medium">
              Time Commitment for learning (Per month)
            </label>

            <select
              name="timeCommitment"
              value={form.timeCommitment}
              onChange={handleChange}
              className={submitted && !form.timeCommitment ? errorInput : inputStyle}
            >
              <option value="">Select Time</option>
              <option>Less than 10 hours</option>
              <option>10 - 25 hours</option>
              <option>25 - 40 hours</option>
              <option>More than 40 hours</option>
            </select>

          </div>

        </div>

      </div>


      {/* SUBMIT BUTTON */}
      <button
        onClick={handleSubmit}
        className="mt-12 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        Submit Assessment
      </button>

    </div>
  );
}