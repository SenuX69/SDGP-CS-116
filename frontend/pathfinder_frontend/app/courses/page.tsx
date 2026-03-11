import Image from "next/image";

export default function Courses() {
  return (
    <div className="min-h-screen bg-gray-50 px-16 py-10">

      {/* TITLE + FILTER ICON */}
      <div className="flex justify-between items-center mb-10">

        <h1 className="text-3xl font-semibold text-gray-800">
          Suggested Courses
        </h1>

        <Image
          src="/images/filter.png"
          alt="filter"
          width={24}
          height={24}
        />

      </div>


      <div className="flex gap-10">

        {/* COURSES GRID */}
        <div className="flex-1 grid grid-cols-3 gap-6">


          {/* CARD 1 */}
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition">

            <h2 className="font-semibold text-gray-800 text-lg">
              UI/UX Design for Beginners
            </h2>

            <div className="flex gap-3 mt-3 text-sm text-gray-500">
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                8H
              </span>
              <span>Cost: Free</span>
            </div>

            <div className="flex items-center gap-3 mt-6">
              <Image
                src="/images/google.png"
                alt="Google"
                width={28}
                height={28}
              />
              <p className="text-gray-700 text-sm">Google Inc.</p>
            </div>

          </div>


          {/* CARD 2 */}
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition">

            <h2 className="font-semibold text-gray-800 text-lg">
              Statistics with Python
            </h2>

            <div className="flex gap-3 mt-3 text-sm text-gray-500">
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                17H
              </span>
              <span>Price: $19.99</span>
            </div>

            <div className="flex items-center gap-3 mt-6">
              <Image
                src="/images/udemy.png"
                alt="Udemy"
                width={28}
                height={28}
              />
              <p className="text-gray-700 text-sm">Udemy</p>
            </div>

          </div>


          {/* CARD 3 */}
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition">

            <h2 className="font-semibold text-gray-800 text-lg">
              ML for Beginners
            </h2>

            <div className="flex gap-3 mt-3 text-sm text-gray-500">
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                5H
              </span>
              <span>Price: $17.99</span>
            </div>

            <div className="flex items-center gap-3 mt-6">
              <Image
                src="/images/coursera.png"
                alt="Coursera"
                width={28}
                height={28}
              />
              <p className="text-gray-700 text-sm">Coursera</p>
            </div>

          </div>


          {/* CARD 4 */}
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition">

            <h2 className="font-semibold text-gray-800 text-lg">
              Tailwind CSS Full Course
            </h2>

            <div className="flex gap-3 mt-3 text-sm text-gray-500">
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                8H
              </span>
              <span>Cost: Free</span>
            </div>

            <div className="flex items-center gap-3 mt-6">
              <Image
                src="/images/google.png"
                alt="Google"
                width={28}
                height={28}
              />
              <p className="text-gray-700 text-sm">Google Inc.</p>
            </div>

          </div>


          {/* CARD 5 */}
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition">

            <h2 className="font-semibold text-gray-800 text-lg">
              HCI for Beginners
            </h2>

            <div className="flex gap-3 mt-3 text-sm text-gray-500">
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded">
                8H
              </span>
              <span>Cost: Free</span>
            </div>

            <div className="flex items-center gap-3 mt-6">
              <Image
                src="/images/google.png"
                alt="Google"
                width={28}
                height={28}
              />
              <p className="text-gray-700 text-sm">Google Inc.</p>
            </div>

          </div>


        </div>


        {/* FILTER PANEL */}
        <div className="w-56 bg-blue-100 p-5 rounded-lg">

          <h3 className="font-semibold mb-4">
            Filter
          </h3>

          <div className="space-y-3 text-sm">

            <label className="flex gap-2">
              <input type="checkbox" />
              Most Relevant
            </label>

            <label className="flex gap-2">
              <input type="checkbox" />
              Alphabetical Order
            </label>

            <label className="flex gap-2">
              <input type="checkbox" />
              Price Low to High
            </label>

          </div>

        </div>

      </div>

    </div>
  );
}