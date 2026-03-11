import Image from "next/image";

export default function Courses() {

  return (
    <div className="min-h-screen bg-gray-50 px-16 py-10">

      <div className="flex justify-between items-center mb-8">

        <h1 className="text-3xl font-semibold text-gray-800">
          Suggested Courses
        </h1>

        <Image
          src="/images/filter.png"
          alt="filter"
          width={30}
          height={30}
        />

      </div>

      <div className="flex gap-10">

        <div className="flex-1">
          Courses Here
        </div>

        <div className="w-56 bg-blue-100 p-5 rounded">
          Filter Panel
        </div>

      </div>

    </div>
  );
}