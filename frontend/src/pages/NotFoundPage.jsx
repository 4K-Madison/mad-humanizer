import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="font-display text-[120px] font-black leading-none text-badger/15">
        404
      </div>
      <h1 className="mt-2 font-display text-2xl font-extrabold tracking-tight text-foreground">
        Page not found
      </h1>
      <p className="mt-2 text-base text-muted-foreground">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Button asChild className="mt-8 gap-2">
        <Link to="/">
          <ArrowLeft className="h-4 w-4" />
          Back to Humanizer
        </Link>
      </Button>
    </div>
  );
}
