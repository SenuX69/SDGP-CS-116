"use client";

import Link from "next/link";
import { useState } from "react";
import Image from "next/image";

export default function RegisterPage() {

const [firstName,setFirstName] = useState("");
const [lastName,setLastName] = useState("");
const [password,setPassword] = useState("");
const [confirmPassword,setConfirmPassword] = useState("");

const handleRegister = (e:any) => {
e.preventDefault();

console.log(firstName,lastName,password,confirmPassword);
};

return (

<div className="min-h-screen bg-white text-black">

{/* NAVBAR */}

<nav className="flex justify-between items-center px-8 py-4 border-b bg-white">

<div className="flex items-center gap-3">

<Image
src="/images/logo.png"
alt="logo"
width={40}
height={40}
/>

<span className="font-semibold text-lg">
PathFinder
</span>

</div>

<div className="flex items-center gap-6">

<Link href="/" className="text-gray-700">
Home
</Link>

<Link
href="/login"
className="bg-black text-white px-5 py-2 rounded-full"
>
Login
</Link>

</div>

</nav>


{/* SIGNUP SECTION */}

<div className="grid grid-cols-2 items-center px-20 py-16">


{/* LEFT FORM */}

<div>

<h1 className="text-4xl font-bold mb-8">
Sign-Up
</h1>

<form onSubmit={handleRegister} className="space-y-6 w-96">

<div>

<label className="block mb-2 text-gray-800">
First Name
</label>

<input
type="text"
value={firstName}
onChange={(e)=>setFirstName(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3"
/>

</div>


<div>

<label className="block mb-2 text-gray-800">
Last Name
</label>

<input
type="text"
value={lastName}
onChange={(e)=>setLastName(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3"
/>

</div>


<div>

<label className="block mb-2 text-gray-800">
New Password
</label>

<input
type="password"
value={password}
onChange={(e)=>setPassword(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3"
/>

</div>


<div>

<label className="block mb-2 text-gray-800">
Confirm Password
</label>

<input
type="password"
value={confirmPassword}
onChange={(e)=>setConfirmPassword(e.target.value)}
className="w-full bg-gray-200 rounded-lg p-3"
/>

</div>


<button
type="submit"
className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
>
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