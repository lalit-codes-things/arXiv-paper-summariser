import { Link } from 'wouter';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#F3F3F3] flex items-center justify-center p-6">
      <div className="text-center">
        <div className="text-8xl font-bold text-[#B9FF66] mb-4">404</div>
        <h1 className="text-2xl font-bold text-[#191A23] mb-2">Page not found</h1>
        <p className="text-[#898989] mb-8">This page doesn't exist.</p>
        <Link href="/">
          <button className="p-btn-dark px-6 py-2.5">← Back home</button>
        </Link>
      </div>
    </div>
  );
}
