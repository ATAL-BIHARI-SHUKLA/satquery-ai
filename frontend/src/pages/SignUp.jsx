import { useState } from "react";
import { api } from "../services/api";
export default function SignUp({ navigateTo }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fullName || !email || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setSuccess("");
    
    try {
      await api.signup({
        full_name: fullName,
        email,
        password,
        confirm_password: confirmPassword
      });
      setSuccess("Account created successfully! Redirecting to login...");
      setTimeout(() => {
        navigateTo("login");
      }, 2000);
    } catch (err) {
      setError(err.message || "Failed to sign up.");
    }
  };

  return (
    <div className="flex min-h-screen bg-bg-base text-text-main items-center justify-center p-4">
      <div className="w-full max-w-md bg-bg-base border border-border-subtle rounded-2xl p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/30">
              <div className="h-5 w-5 rounded-full border-[1.5px] border-primary" />
              <span className="absolute h-2 w-2 rounded-full bg-primary" />
            </div>
          </div>
          <h2 className="text-2xl font-semibold tracking-wide">
            Create an Account
          </h2>
          <p className="text-text-muted text-sm mt-2">Join SATQUERY today</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm text-center">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl text-sm text-center">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-text-main mb-1.5">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-surface border border-border-subtle rounded-xl px-4 py-3 text-text-main placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-primary transition"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-main mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface border border-border-subtle rounded-xl px-4 py-3 text-text-main placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-primary transition"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-main mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface border border-border-subtle rounded-xl px-4 py-3 text-text-main placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-primary transition"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-main"
              >
                {showPassword ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                )}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-main mb-1.5">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-surface border border-border-subtle rounded-xl px-4 py-3 text-text-main placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-primary transition"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-main"
              >
                {showConfirmPassword ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-primary hover:bg-primary text-text-main font-medium py-3 rounded-xl transition duration-200"
          >
            Create Account
          </button>
        </form>

        <div className="mt-6 text-center space-y-3">
          <p className="text-sm text-text-muted">
            Already have an account?{" "}
            <button
              onClick={() => navigateTo("login")}
              className="text-primary hover:text-primary font-medium transition"
            >
              Sign in
            </button>
          </p>
          <button
            onClick={() => navigateTo("home")}
            className="text-sm text-text-muted hover:text-text-main transition"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
