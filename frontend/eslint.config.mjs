import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import reactHooks from "eslint-plugin-react-hooks";

const config = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: { ecmaVersion: "latest", sourceType: "module", ecmaFeatures: { jsx: true } },
    },
    plugins: { "@typescript-eslint": tsPlugin, "react-hooks": reactHooks },
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
];

export default config;
