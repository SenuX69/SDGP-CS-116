import Image from "next/image";

const courses = [
  {
    title: "UI/UX Design for Beginners",
    duration: "10H",
    price: "Free",
    provider: "Google Inc.",
    logo: "/images/google.png",
  },
  {
    title: "Statistics with Python",
    duration: "17H",
    price: "$19.99",
    provider: "Udemy",
    logo: "/images/udemy.png",
  },
  {
    title: "ML for Beginners",
    duration: "5H",
    price: "$17.99",
    provider: "Coursera",
    logo: "/images/coursera.png",
  },
  {
    title: "Tailwind CSS Full Course",
    duration: "8H",
    price: "Free",
    provider: "Google Inc.",
    logo: "/images/google.png",
  },
  {
    title: "HCI for Beginners",
    duration: "8H",
    price: "Free",
    provider: "Google Inc.",
    logo: "/images/google.png",
  },
];

export default function Courses() {
  return (
    <div className="min-h-screen bg-gray-50 px-16 py-10">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-semibold text-gray-800">
          Suggested Courses
        </h1>

        <Image src="/images/filter.png" alt="filter" width={24} height={24} />
      </div>

      <div className="flex gap-10">

        {/* COURSES GRID */}
        <div className="flex-1 grid grid-cols-3 gap-6">

          {courses.map((course, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition"
            >
              <h2 className="font-semibold text-gray-800 text-lg">
                {course.title}
              </h2>

              <div className="flex gap-3 mt-3 text-sm text-gray-500">
                <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                  {course.duration}
                </span>
                <span>
                  {course.price === "Free"
                    ? "Cost: Free"
                    : `Price: ${course.price}`}
                </span>
              </div>

              <div className="flex items-center gap-3 mt-6">
                <Image
                  src={course.logo}
                  alt={course.provider}
                  width={28}
                  height={28}
                />
                <p className="text-gray-700 text-sm">{course.provider}</p>
              </div>
            </div>
          ))}

        </div>

        {/* FILTER PANEL (same as yours) */}
        <div className="w-56 bg-blue-50 border border-blue-100 p-6 rounded-xl">
          <h3 className="font-semibold text-gray-700 mb-4">Filter</h3>

          <div className="space-y-3 text-sm">
            <label className="flex gap-2 text-gray-600">
              <input type="checkbox" />
              Most Relevant
            </label>

            <label className="flex gap-2 text-gray-600">
              <input type="checkbox" />
              Alphabetical Order
            </label>

            <label className="flex gap-2 text-gray-600">
              <input type="checkbox" />
              Price Low to High
            </label>
          </div>
        </div>

      </div>
    </div>
  );
}