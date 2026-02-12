import { Link } from "react-router-dom";
import { Zap, ScanSearch } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative mt-auto border-t border-border/60 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid gap-8 sm:grid-cols-3">
          {/* Brand column */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-badger text-white">
                <span className="font-display text-xs font-black">M</span>
              </div>
              <span className="font-display text-sm font-bold tracking-tight">
                MAD<span className="text-badger">-</span>HUMANIZER
              </span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Transform AI-generated text into natural, human-sounding content using advanced language models.
            </p>
          </div>

          {/* Navigation column */}
          <div className="space-y-3">
            <h4 className="font-display text-xs font-bold uppercase tracking-[0.15em] text-foreground">
              Tools
            </h4>
            <div className="flex flex-col gap-2">
              <Link
                to="/"
                className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-badger"
              >
                <Zap className="h-3.5 w-3.5" />
                Humanizer
              </Link>
              <Link
                to="/detector"
                className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-badger"
              >
                <ScanSearch className="h-3.5 w-3.5" />
                AI Detector
              </Link>
            </div>
          </div>

          {/* Info column */}
          <div className="space-y-3">
            <h4 className="font-display text-xs font-bold uppercase tracking-[0.15em] text-foreground">
              About
            </h4>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Built with Llama 3.2 + LoRA fine-tuning. Multi-detector AI analysis powered by industry-leading APIs.
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 flex flex-col items-center justify-between gap-2 border-t border-border/60 pt-6 sm:flex-row">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} MAD-HUMANIZER. All rights reserved.
          </p>
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-1.5 rounded-full bg-badger" />
            <span className="text-xs font-medium text-muted-foreground">
              Madison, WI
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
