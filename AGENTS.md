# ChurchManager Development Boundary

- `C:\Users\Pastor\Documents\ChurchManager-Legacy` is the separate Frozen ChurchManager application.
- Never edit, delete, migrate, synchronize, import from, or copy development files into the Frozen application tree from this project.
- Never use the Frozen application's runtime, JSForm copy, forms, configuration, or production database for development work.
- Development ChurchManager uses this project, `C:\Users\Pastor\Documents\JSForm`, its own `.runtime-venv`, and the guarded development/test database configuration.
- Read-only inspection of the Frozen application is allowed only when the user explicitly requests verification.
- Any Frozen application change must be performed from its separate project, not from this project.
- In this project, "legacy" means obsolete JSForm-era behavior inside development. It never means the separate Frozen application and never authorizes changes there.
