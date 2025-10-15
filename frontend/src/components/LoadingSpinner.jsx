function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#5b7fd4]/30 border-t-[#5b7fd4] mb-6"></div>
      <p className="text-[#5a5a5a] text-lg font-light">{message}</p>
    </div>
  );
}

export default LoadingSpinner;
