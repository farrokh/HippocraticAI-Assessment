import Link from "next/link";

interface NoComparisonProps {
  message?: string;
  showBackButton?: boolean;
}

export default function NoComparison({ 
  message = "No More Comparisons Available",
  showBackButton = true 
}: NoComparisonProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <svg 
              className="w-8 h-8 text-gray-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.824-2.709M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {message}
          </h1>
          <p className="text-gray-600">
            There are no more duels available for comparison at this time.
          </p>
        </div>
        
        {showBackButton && (
          <div className="space-y-3">
            <Link 
              href="/" 
              className="inline-block w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Go Back to Home
            </Link>
            <Link 
              href="/templates" 
              className="inline-block w-full bg-gray-100 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              Browse Templates
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
