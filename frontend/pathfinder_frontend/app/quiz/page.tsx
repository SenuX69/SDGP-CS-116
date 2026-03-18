"use client";

import { useState } from "react";

export default function QuizPage() {

  const [step, setStep] = useState(1);

  const [form, setForm] = useState({
    role: "",
    goal: "",
    name: "",
    email: "",
    gender: "",
    education: ""
  });

  const [answers, setAnswers] = useState({});

  const questions = [
    "Well-organized","Friendly","Persuasive","Creative","Inquisitive",
    "Analytical","Sensitive","Outgoing","Decisive","Enthusiastic",
    "Interested in doing basic calculations","Thorough","Athletic",
    "A Nature Lover","Imaginative","Intuitive","Observant","Understanding",
    "Straightforward","Insightful about people","Self-Confident","Sociable",
    "Practical","Mechanically Inclined","Energetic",
    "Accurate with details and numbers","Innovative","Methodical",
    "Scientific","Logical","Idealistic","Efficient","An individualist",
    "Helpful","Precise","Interested about the physical/real world"
  ];

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAnswer = (q, val) => {
    setAnswers({ ...answers, [q]: val });
  };

  // ✅ CONNECTED TO BACKEND
  const handleSubmit = async () => {

    const payload = {
      ...form,
      answers
    };

    try {
      const res = await fetch("http://localhost:8000/api/quiz", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      alert(`Recommended Career: ${data.career}`);

    } catch (err) {
      console.error(err);
      alert("Error submitting quiz");
    }
  };

  return (
    <div className="min-h-screen bg-white text-black px-10 py-8">

      {/* STEP 1 */}
      {step === 1 && (
        <div className="max-w-4xl mx-auto">

          <h2 className="text-gray-700 text-lg mb-6 font-medium">
            Please fill in below required details
          </h2>

          <p className="font-semibold mb-2 text-gray-900">Are You?</p>
          <div className="flex flex-wrap gap-6 mb-6">
            {["School Student","School Leaver","University Student","Professional"].map((r)=>(
              <label key={r} className="flex items-center gap-2 text-gray-800">
                <input type="radio" name="role" value={r} onChange={handleChange} className="accent-red-500"/>
                {r}
              </label>
            ))}
          </div>

          <p className="font-semibold mb-2 text-gray-900">What are you looking for?</p>
          <div className="flex flex-wrap gap-6 mb-6">
            {["Subject Selection","Training Course","Higher Education","Career Change","Job","Career Development"].map((g)=>(
              <label key={g} className="flex items-center gap-2 text-gray-800">
                <input type="radio" name="goal" value={g} onChange={handleChange} className="accent-red-500"/>
                {g}
              </label>
            ))}
          </div>

          <input
            name="name"
            placeholder="Name"
            onChange={handleChange}
            className="w-full bg-gray-100 border border-gray-300 p-3 rounded mb-4 focus:border-red-500 outline-none"
          />

          <input
            name="email"
            placeholder="Email Address"
            onChange={handleChange}
            className="w-full bg-gray-100 border border-gray-300 p-3 rounded mb-4 focus:border-red-500 outline-none"
          />

          <p className="mb-2 text-gray-900 font-semibold">Gender</p>
          <div className="flex gap-6 mb-4">
            <label className="text-gray-800">
              <input type="radio" name="gender" value="Male" onChange={handleChange} className="accent-red-500"/> Male
            </label>
            <label className="text-gray-800">
              <input type="radio" name="gender" value="Female" onChange={handleChange} className="accent-red-500"/> Female
            </label>
          </div>

          <select
            name="education"
            onChange={handleChange}
            className="w-full bg-gray-100 border border-gray-300 p-3 rounded mb-6 focus:border-red-500 outline-none"
          >
            <option>Select Education</option>
            <option>O/L</option>
            <option>A/L</option>
            <option>Diploma</option>
            <option>Bachelors</option>
            <option>Masters</option>
          </select>

          <button
            onClick={()=>setStep(2)}
            className="bg-red-500 text-white px-8 py-3 rounded-lg hover:bg-red-600 transition"
          >
            Next
          </button>

        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <div className="max-w-6xl mx-auto">

          <h1 className="text-2xl font-bold mb-6 text-gray-900">
            Personality Test
          </h1>

          <div className="grid grid-cols-6 text-center mb-4 font-semibold text-gray-700">
            <div></div>
            <div>Strongly Agree</div>
            <div>Agree</div>
            <div>Neutral</div>
            <div>Disagree</div>
            <div>Strongly Disagree</div>
          </div>

          {questions.map((q, i) => (
            <div key={i} className="grid grid-cols-6 items-center py-3 border-b border-gray-200">

              <div className="text-gray-800 text-sm">{q}</div>

              {["5","4","3","2","1"].map((val)=>(
                <input
                  key={val}
                  type="radio"
                  name={q}
                  onChange={()=>handleAnswer(q,val)}
                  className="accent-red-500 mx-auto"
                />
              ))}

            </div>
          ))}

          <button
            onClick={handleSubmit}
            className="mt-8 bg-red-500 text-white px-10 py-3 rounded-lg hover:bg-red-600 transition"
          >
            Submit
          </button>

        </div>
      )}

    </div>
  );
}