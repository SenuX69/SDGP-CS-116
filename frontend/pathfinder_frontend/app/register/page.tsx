"use client";

import Link from "next/link";
import { useState } from "react";
import Image from "next/image";

export default function RegisterPage() {

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleRegister = async (e: any) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: firstName + " " + lastName,
          email: email,
          password: password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Registered successfully");
        window.location.href = "/login";
      } else {
        alert(data.detail);
      }

    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  return (
    <div className="min-h-screen bg-white text-black">

      {/* NAVBAR */}
      <nav className="flex justify-between items-center px-8 py-4 border-b bg-white">
        <div className="flex items-center gap-3">
          <Image src="/images/logo.png" alt="logo" width={40} height={40} />
          <span className="font-semibold text-lg">PathFinder</span>
        </div>

        <div className="flex items-center gap-6">
          <Link href="/" className="text-gray-700">Home</Link>
          <Link href="/login" className="bg-black text-white px-5 py-2 rounded-full">
            Login
          </Link>
        </div>
      </nav>

      {/* SIGNUP SECTION */}
      <div className="grid grid-cols-2 items-center px-20 py-16">

        {/* LEFT FORM */}
        <div>
          <h1 className="text-4xl font-bold mb-8">Sign-Up</h1>

          <form onSubmit={handleRegister} className="space-y-6 w-96">

            <div>
              <label className="block mb-2">First Name</label>
              <input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full bg-gray-200 p-3 rounded"
              />
            </div>

            <div>
              <label className="block mb-2">Last Name</label>
              <input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full bg-gray-200 p-3 rounded"
              />
            </div>

            <div>
              <label className="block mb-2">Email</label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-gray-200 p-3 rounded"
              />
            </div>

            <div>
              <label className="block mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-200 p-3 rounded"
              />
            </div>

            <div>
              <label className="block mb-2">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-gray-200 p-3 rounded"
              />
            </div>

            <button className="w-full bg-blue-600 text-white py-3 rounded">
              Sign Up
            </button>

          </form>
        </div>

        {/* RIGHT IMAGE */}
        <div className="flex justify-center">
          <Image
            src="/images/register-illustration.png"
            alt="register"
            width={450}
            height={450}
          />
        </div>

      </div>
    </div>
  );
}