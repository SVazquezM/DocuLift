
# DocuLift
#### Video Demo: <https://www.youtube.com/watch?v=Ibxx_JDMNc8>
#### Description:

DocuLift is a full-stack web application built with Flask, SQLite, HTML/CSS, and JavaScript designed to simplify and automate the technical documentation of elevator renovation or modification projects.
Its goal is to reduce the time technicians spend on paperwork and ensure that all documentation complies with the official formats required by the administration, quickly, efficiently, and without errors.
With DocuLift, each technician can create, manage, and generate comprehensive PDF reports on the work performed, while also maintaining a project history accessible from an intuitive dashboard.

## Files

- `app.py`: This Flask file defines every route (login, register, add project, update, delete, PDF generation), calls the database, and applies the validation rules. Whenever you click “Save,” “Edit,” “Delete,” or “Print,” the request flows through here.

- `app.py`: The main Flask application. It wires up every route in DocuLift and orchestrates all server-side tasks.
  - Authentication (`/register`, `/login`, `/logout`)
  - Field validation (`/validate-field`, `/validate-field-public`)
  - Project lifecycle (`/add-project`, `/update-project`, `/delete-project`, `/get-project`)
  - PDF generation (`/generate-pdf/<id>`)

 `helpers.py`: A toolbox of shared utilities.
  - `login_required` wraps any view that should be visible only to authenticated users; if the session lacks `user_id` the user is redirected back to the login screen.
  - `get_technical_specs()` and `get_certificates()` return dictionaries of predefined options used to populate the custom dropdowns; this keeps the catalogs centralized so the frontend can render them dynamically.

- `templates/login2.html`: The standalone login and registration page. It offers instant feedback—if something’s wrong with the email or password, the user sees it before submitting.


- `templates/layout9.html`: The main dashboard. It lists projects, opens the multi-tab modal used to create or edit projects, ties together all the custom components, and contains the JavaScript that validates fields, sends data to `app.py`, and updates the interface without reloads.


- `templates/pdf/documento.html`: The PDF template that fills with project data. Every checkbox and text span corresponds to a field saved in the database, ensuring the printable report matches official requirements. To generate this tamplate we used:
    - **WeasyPrint** – A PDF rendering engine that understands HTML and CSS. It was chosen because the final document needs to match an official layout; writing that from scratch in a PDF library would be slower and harder to maintain. With WeasyPrint you can reuse the same templating approach (Jinja + CSS) used elsewhere in the app.


- `static/styles.css`: Base styling for the site (colors, spacing, buttons) layered on top of Bootstrap so the dashboard and modal have a consistent look.

- `static/multi-select.js`: A reusable multi-select dropdown component use layout9 multi-tab modal.

- `static/single-select.js`: A single-choice dropdown  component use layout9 multi-tab modal.

- `static/single-select_input_text.js`: Extends the dropdown to allow typing custom values (perfect for technical specs where the technician might need a free-form entry).

- `static/multi-select.css`, `static/single-select.css`, `static/single-select_input_text.css`: Styling files that give each component its layout, colors, and animations so they blend seamlessly into the modal.

- `static/pdf/styles.css`: Specific rules for the PDF layout (fonts, page structure, column widths) so the generated document prints cleanly on A4.

- `project.db`: The SQLite database. It stores user accounts, every project record.



