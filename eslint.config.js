// ESLint 9 flat config.
//
// Replaces the legacy .eslintrc.json, which ESLint 9 no longer reads
// by default (ESLint 9 requires eslint.config.js unless explicitly
// told to fall back to the old eslintrc format). This preserves the
// same rule intent as the old config — eslint:recommended +
// plugin:react/recommended, no-console as a warning, prop-types and
// react-in-jsx-scope disabled (React 18 automatic JSX runtime) —
// using only already-installed packages (@eslint/js,
// eslint-plugin-react, globals).
import js from '@eslint/js'
import react from 'eslint-plugin-react'
import globals from 'globals'

export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'qa/**',
      'reports/**',
      'src/data/*.json',
    ],
  },

  // Browser-side React source.
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
      },
    },
    plugins: {
      react,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.flat.recommended.rules,
      ...react.configs.flat['jsx-runtime'].rules,
      'no-console': 'warn',
      'react/prop-types': 'off',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },

  // Node-side build/tooling scripts (not covered by the CI lint
  // command, which is scoped to src/, but kept correct for anyone
  // running `eslint .` directly).
  {
    files: ['scripts/**/*.{js,mjs}', 'vite.config.js', 'tailwind.config.js', 'postcss.config.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.node,
      },
    },
    rules: {
      ...js.configs.recommended.rules,
    },
  },
]
