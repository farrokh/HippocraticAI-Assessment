"use client"

export default function PromptsListsLoading() {
    // show skeleton loading for the list of templates
    return (
        <div className="animate-pulse">
            <div className="h-10 bg-gray-200 rounded w-full" />
            <div className="h-10 bg-gray-200 rounded w-full" />
        </div>
    )
}