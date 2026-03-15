"use client";

import Link from "next/link";
import { useState } from "react";
import Image from "next/image";

export default function LoginPage() {

const [email,setEmail] = useState("");
const [password,setPassword] = useState("");

const handleLogin = (e:any) => {
e.preventDefault();
console.log(email,password);
};

return (

<div className="min-h-screen bg-white text-black">

{/* NAVBAR */}

<nav className="flex justify-between items-center px-8 py-4 border-b bg-white">

<div className="flex items-center gap-3">

<Image
  src="/images/logo.png"
  alt="PathFinder Logo"
  width={40}
  height={40}
/>

<span className="font-semibold text-lg text-black">
PathFinder
</span>

</div>

<div className="flex items-center gap-6">

<Link href="/" className="text-gray-700">
Home
</Link>

<Link
href="/register"
className="bg-black text-white px-5 py-2 rounded-full"
>
Sign Up
</Link>

</div>

</nav>


{/* LOGIN SECTION */}

<div className="grid grid-cols-2 items-center px-20 py-16">

{/* LEFT SIDE FORM */}

<div>

<h1 className="text-4xl font-bold mb-8 text-black">
Log In
</h1>

<form onSubmit={handleLogin} className="space-y-6 w-96">

<div>

<label className="block mb-2 text-gray-800">
Email
</label>

<input
type="email"
value={email}
onChange={(e)=>setEmail(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3 text-black"
/>

</div>


<div>

<label className="block mb-2 text-gray-800">
Password
</label>

<input
type="password"
value={password}
onChange={(e)=>setPassword(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3 text-black"
/>

</div>


<p className="text-sm text-gray-700 text-right">
Forgot Password?
</p>


<button
type="submit"
className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
>
Login
</button>


<p className="text-sm text-gray-800">

Don't have an account?

<Link href="/register" className="text-blue-600 ml-1 font-medium">
Sign Up
</Link>

</p>

</form>

</div>


{/* RIGHT SIDE IMAGE */}

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