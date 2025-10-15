import { useState } from "react";
import Header from "./components/Header";
import SingleUrlAnalyzer from "./components/SingleUrlAnalyzer";
import ResultCard from "./components/ResultCard";

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalysisComplete = (newResults) => {
    if (Array.isArray(newResults)) {
      setResults(newResults);
    } else {
      setResults([newResults]);
    }
    setError(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setResults([]);
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Header />

        <main className="space-y-8">
          {/* Single URL Analyzer with Examples */}
          <SingleUrlAnalyzer
            onAnalysisComplete={handleAnalysisComplete}
            onError={handleError}
            setIsLoading={setIsLoading}
          />

          {/* Error Display */}
          {error && (
            <div className="border border-[#e89090] bg-[#e89090]/5 rounded-2xl p-6 animate-fade-in">
              <p className="text-[#2d2d2d] text-base font-light">{error}</p>
            </div>
          )}

          {/* Results Section */}
          {results.length > 0 && (
            <div className="space-y-6 animate-fade-in">
              <div className="space-y-6">
                {results.map((result, index) => (
                  <ResultCard key={index} result={result} />
                ))}
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && results.length === 0 && !error && (
            <div className="text-center py-16 animate-fade-in">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-2 border-[#5b7fd4]/20 border-t-[#5b7fd4] mb-4"></div>
              <p className="text-[#5a5a5a] text-base font-light">
                Analyzing...
              </p>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-24 text-center py-6 border-t border-[#e0e0e0]">
          <p className="text-[#5a5a5a] text-sm font-light">
            Powered by Llama 3.2 (Ollama)
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
