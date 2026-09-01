'use strict';

const prettierRecommended = require('eslint-plugin-prettier/recommended');

module.exports = [
  {
    ignores: [
      'node_modules/**',
      'frontend/dist/**',
      'frontend/build/**',
      'backend/**',
      '**/*.db',
    ],
  },
  {
    files: ['frontend/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      eqeqeq: ['error', 'always'],
    },
  },
  prettierRecommended,
];
