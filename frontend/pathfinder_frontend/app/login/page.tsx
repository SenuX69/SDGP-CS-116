"use client";

import Link from "next/link";
import { useState } from "react";
import Image from "next/image";

export default function LoginPage() {

  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");

  const handleLogin = async (e:any) => {
    e.preventDefault();

    try {
      const res = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password
        }),
      });

      const data = await res.json();

      if(res.ok){
        alert("Login successful");

        // ✅ STORE USER NAME
        localStorage.setItem("userName", data.name || "User");

        // ✅ REDIRECT
        window.location.href = "/dashboard";

      } else {
        alert(data.detail || "Invalid credentials");
      }

    } catch (err) {
      console.error(err);
      alert("Error connecting to server");
    }
  };

  return (

    <div className="min-h-screen bg-white text-black">

      {/* NAVBAR */}
      <nav className="flex justify-between items-center px-8 py-4 border-b bg-white">

        <div className="flex items-center gap-3">
          <Image src="/images/logo.png" alt="logo" width={40} height={40}/>
          <span className="font-semibold text-lg">PathFinder</span>
        </div>

        <div className="flex items-center gap-6">
          <Link href="/" className="text-gray-700">Home</Link>
          <Link href="/register" className="bg-black text-white px-5 py-2 rounded-full">
            Sign Up
          </Link>
        </div>

      </nav>

      {/* LOGIN SECTION */}
      <div className="grid grid-cols-2 items-center px-20 py-16">

        {/* LEFT FORM */}
        <div>

          <h1 className="text-4xl font-bold mb-8">Login</h1>

          <form onSubmit={handleLogin} className="space-y-6 w-96">

            <div>
              <label className="block mb-2 text-gray-800">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                className="w-full bg-gray-200 rounded-lg p-3"
              />
            </div>

            <div>
              <label className="block mb-2 text-gray-800">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
                className="w-full bg-gray-200 rounded-lg p-3"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
            >
              Login
            </button>

          </form>

          <p className="mt-4 text-gray-600">
            Don’t have an account?{" "}
            <Link href="/register" className="text-blue-600">
              Sign up
            </Link>
          </p>

        </div>

        {/* RIGHT IMAGE */}
        <div className="flex justify-center">
          <Image
            src="/images/login-illustration.png"
            alt="login"
            width={450}
            height={450}
          />
        </div>

      </div>

    </div>
  );
}