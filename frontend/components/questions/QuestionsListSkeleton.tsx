"use client";

export default function QuestionsListSkeleton() {
    return (
        <div className="flex flex-col gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
                <div
                    key={i}
                    className="flex items-start justify-between p-3 rounded-lg animate-pulse"
                >
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                        {/* Question Text & Answer Skeleton */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2 mb-2">
                                {/* Question text skeleton */}
                                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                                {/* Timestamp skeleton */}
                                <div className="h-3 bg-gray-200 rounded w-24"></div>
                            </div>
                            {/* Answer preview skeleton */}
                            <div className="h-3 bg-gray-200 rounded w-full mt-1"></div>
                        </div>
                    </div>

                    {/* Status Badge Skeleton */}
                    <div className="flex items-center gap-2 text-xs bg-gray-50 px-3 py-1 rounded-full ml-2 flex-shrink-0">
                        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                        <div className="h-3 bg-gray-200 rounded w-16"></div>
                    </div>
                </div>
            ))}
        </div>
    );
}