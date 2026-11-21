module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'react-app',
    'plugin:react/recommended',
    'plugin:security/recommended-legacy',
  ],
  plugins: ['react', 'security'],
  rules: {
    'security/detect-object-injection': 'warn',
    'security/detect-non-literal-require': 'error',
    'security/detect-unsafe-regex': 'error',
    'react/no-danger': 'error',
    'react/jsx-no-target-blank': 'error',
    'react/prop-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};