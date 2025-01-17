export class Functions {
    static getStatusColor(status: string) {
        switch (status) {
            case "pending":
                return "bg-amber-100 text-amber-800 ring-amber-600/20";
            case "in_progress":
                return "bg-blue-100 text-blue-800 ring-blue-600/20";
            case "completed":
                return "bg-emerald-100 text-emerald-800 ring-emerald-600/20";
            default:
                return "bg-gray-100 text-gray-800 ring-gray-600/20";
        }
    }
}