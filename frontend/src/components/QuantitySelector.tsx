import { useState } from "react";

interface QuantitySelectorProps {
  value: number;
  maxValue: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export default function QuantitySelector({
  value,
  maxValue,
  onChange,
  disabled = false,
}: QuantitySelectorProps) {
  const [error, setError] = useState<string | null>(null);

  const handleDecrement = () => {
    if (disabled) return;
    const newValue = Math.max(1, value - 1);
    onChange(newValue);
    setError(null);
  };

  const handleIncrement = () => {
    if (disabled) return;
    if (value >= maxValue) {
      setError(`Максимум ${maxValue} шт.`);
      return;
    }
    const newValue = Math.min(maxValue, value + 1);
    onChange(newValue);
    setError(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    if (inputValue === "") {
      onChange(1);
      setError(null);
      return;
    }

    const numValue = Number(inputValue);
    if (numValue < 1) {
      onChange(1);
      setError("Минимум 1 шт.");
    } else if (numValue > maxValue) {
      onChange(maxValue);
      setError(`Максимум ${maxValue} шт.`);
    } else {
      onChange(numValue);
      setError(null);
    }
  };

  const handleBlur = () => {
    if (value < 1) {
      onChange(1);
    } else if (value > maxValue) {
      onChange(maxValue);
    }
    setError(null);
  };

  return (
    <div className="flex flex-col items-start gap-1">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleDecrement}
          disabled={disabled || value <= 1}
          className="flex h-10 w-10 items-center justify-center rounded-l-md border border-amber-500 bg-white text-amber-700 transition hover:bg-amber-50 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Уменьшить количество"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 12H4"
            />
          </svg>
        </button>

        <input
          type="number"
          min="1"
          max={maxValue}
          value={value}
          onChange={handleInputChange}
          onBlur={handleBlur}
          disabled={disabled}
          className="h-10 w-16 border-y border-amber-500 px-2 text-center text-sm font-semibold text-slate-900 focus:outline-none disabled:bg-slate-100"
        />

        <button
          type="button"
          onClick={handleIncrement}
          disabled={disabled || value >= maxValue}
          className="flex h-10 w-10 items-center justify-center rounded-r-md border border-amber-500 bg-white text-amber-700 transition hover:bg-amber-50 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Увеличить количество"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </button>
      </div>

      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
    </div>
  );
}
