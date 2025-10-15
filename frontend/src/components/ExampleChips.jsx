import { useState } from "react";
import { analyzeUrl } from "../services/api";

function ExampleChips({ onExampleClick }) {
  const examples = [
    { name: "GitHub", url: "github.com" },
    { name: "LinkedIn", url: "linkedin.com" },
    { name: "Twitter", url: "twitter.com" },
    { name: "Reddit", url: "reddit.com" },
    { name: "Facebook", url: "facebook.com" },
  ];

  return (
    <section className="card animate-slide-up">
      <h3 className="text-lg font-medium text-[#4a4a4a] mb-5 flex items-center gap-2">
        <span className="text-[#a7c7e7]">🌟</span>
        Quick Examples
      </h3>
      <div className="flex flex-wrap gap-3">
        {examples.map((example) => (
          <button
            key={example.url}
            onClick={() => {
              document.getElementById("url-input").value = example.url;
              document
                .getElementById("url-input")
                .dispatchEvent(new Event("input", { bubbles: true }));
            }}
            className="px-6 py-2.5 bg-white hover:bg-[#b4a7d6] hover:text-white border border-[#e8e8e8] hover:border-[#b4a7d6] rounded-full transition-all duration-300 font-medium text-sm hover:-translate-y-1 hover:shadow-md text-[#4a4a4a]"
          >
            {example.name}
          </button>
        ))}
      </div>
    </section>
  );
}

export default ExampleChips;
