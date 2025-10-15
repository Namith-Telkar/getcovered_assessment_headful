import { useState } from "react";
import { analyzeUrl } from "../services/api";

function SingleUrlAnalyzer({ onAnalysisComplete, onError, setIsLoading }) {
  const [url, setUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const examples = [
    { name: "GitHub", url: "https://github.com/login" },
    { name: "Instagram", url: "https://instagram.com/accounts/login" },
    { name: "Stack Overflow", url: "https://stackoverflow.com/users/login" },
    { name: "Medium", url: "https://medium.com/m/signin" },
    { name: "WordPress", url: "https://wordpress.com/log-in" },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!url.trim()) {
      onError("Please enter a URL");
      return;
    }

    setIsAnalyzing(true);
    setIsLoading(true);

    try {
      const result = await analyzeUrl(url.trim());
      onAnalysisComplete(result);
    } catch (error) {
      onError(error.message || "Failed to analyze URL");
    } finally {
      setIsAnalyzing(false);
      setIsLoading(false);
    }
  };

  const handleExampleClick = (exampleUrl) => {
    setUrl(exampleUrl);
  };

  return (
    <section className="card animate-slide-up">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex flex-col md:flex-row gap-3">
          <input
            id="url-input"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter website URL (e.g., github.com/login)"
            className="input-field flex-1"
            disabled={isAnalyzing}
          />
          <button
            type="submit"
            className="btn-primary flex items-center justify-center gap-2 min-w-[140px]"
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                <span>Analyzing</span>
              </>
            ) : (
              <span>Analyze</span>
            )}
          </button>
        </div>

        {/* Quick Examples */}
        <div className="pt-4 border-t border-[#e0e0e0]">
          <p className="text-sm font-light text-[#5a5a5a] mb-3 uppercase tracking-wider">
            Try an example
          </p>
          <div className="flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                key={example.url}
                type="button"
                onClick={() => handleExampleClick(example.url)}
                className="px-4 py-2 bg-[#fafafa] hover:bg-[#5b7fd4] hover:text-white border border-[#e0e0e0] hover:border-[#5b7fd4] rounded-full transition-all duration-200 font-light text-sm text-[#2d2d2d]"
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>
      </form>
    </section>
  );
}

export default SingleUrlAnalyzer;
