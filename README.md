### International Grading Agency

a frappe application that outlines the complete development plan for Phase 1 of the International Grading Agency (IGA) grading and certification system. The project will deliver a production-ready, audit-compliant platform built on ERPNext as the operational backbone, with a secure API integration layer connecting to a public-facing website.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app iga
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/iga
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
