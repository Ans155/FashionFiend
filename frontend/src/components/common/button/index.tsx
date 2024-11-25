import React, { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'small' | 'medium' | 'large';
  isSubmitting?: boolean;
  customClasses?: string,
  onClick?: () => void;
}
const BtnLoader = () => {
    return (
        <svg
            className="animate-spin h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
        >
            <circle
                className="opacity-100"
                cx="12"
                cy="12"
                r="10"
                stroke="#ccc"
                strokeWidth="4"
            ></circle>
            <path
                className="opacity-75"
                fill="#007AFF"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
        </svg>
    )
}
const Button: React.FC<ButtonProps> = ({ variant = 'primary', size = 'medium', isSubmitting = false,
  customClasses,
  children,
  onClick, ...props }) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium cursor-pointer rounded-full py-1 relative';

  const variantStyles: any = {
    primary: `text-white ${!isSubmitting ? "bg-blue-600 hover:bg-blue-700" : "bg-primary-600"}`,
    secondary: 'text-secondary-300 bg-white border border-secondary-300 hover:bg-secondary-300 hover:text-white',
    success: 'text-white bg-green-500 hover:bg-green-600',
    danger: 'text-white bg-red-500 hover:bg-red-600',
  };

  const sizeStyles = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-4 py-2 text-base',
    large: 'px-5 py-3 text-lg',
  };

  return (
    <button
      className={`
        ${baseStyles}
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${customClasses}`}
      disabled={isSubmitting}
      onClick={onClick}
    >
      <>
        <div className={`absolute top-2/4 left-2/4 transform -translate-x-1/2 -translate-y-1/2 ${isSubmitting ? "opacity-1" : "opacity-0"}`}><BtnLoader/></div>
        <div className={`${isSubmitting ? "opacity-0" : "opacity-1"}`}>{children}</div>
      </>
    </button>
  );
};

export default Button;