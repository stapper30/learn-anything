export default function SideNav({ concepts }) {
    return (
        <div className="w-1/4">
            <div className="bg-gray-200 p-4 rounded-lg sticky top-4 max-h-[calc(100vh-2rem)] overflow-hidden flex flex-col">
                <h2 className="text-xl font-semibold mb-4">Navigation</h2>
                <ul className="space-y-2 flex-1 overflow-y-auto">
                    {concepts.concepts.map((concept) => (
                        <li key={concept.id}>
                            <a href={`#${concept.id}`} className="text-blue-600 hover:underline">
                                {concept.title}
                            </a>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}