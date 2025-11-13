# Workflow: EVN Portal Invoice Download

## Overview
Download the requested number of most recent invoices from the EVN portal using normalized coordinates, secure credential typing, and documented timing requirements. Follow the steps exactly, call the wait tool for every pause, and rely on browser-opening and secure-credential tools for navigation and login.

## Prerequisites
- Valid EVN portal credentials provided by the user.
- Stable internet connection.
- Browser-opening tool available to load the EVN portal URL directly.
- Download directory configured to save invoices without additional prompts.

## Coordinate Reference (Reference screen 1920×1080)
Use these absolute coordinates when calling `move_mouse`. Pointer tools automatically scale them for the current display.

| Element | Coordinates (x, y) | Description |
| --- | --- | --- |
| `login_button_home` | (1550, 180) | “Đăng nhập” button on home page |
| `username_field` | (880, 385) | Username (Số điện thoại) input |
| `password_field` | (880, 475) | Password (Mật khẩu) input |
| `login_button_form` | (950, 600) | “Đăng nhập” button on login form |
| `view_all_invoices_button` | (1440, 555) | “Xem tất cả hoá đơn” button |
| `download_button_row1` | (1505, 680) | Download button for first invoice row |
| `download_popup_pdf_option` | (1080, 580) | PDF version option in popup |
| `download_popup_close` | (1115, 445) | Close icon for the download popup |

**Invoice Row Offset**: Each subsequent invoice row’s download button is `+50` on the y-axis. For invoice index `n`, compute `y = 680 + (n * 50)`.

## Execution Rules
- **VALIDATE → MOVE → CLICK → TYPE**. This order is mandatory for every interaction.
- **Image validation is required** whenever an image is listed. Call `wait_for_element(image, timeout)` (retry once). STOP if validation fails twice.
- **NO CLICK SKIPPING**: `move_mouse` MUST ALWAYS be followed by `click_mouse` before typing.
- **SEQUENTIAL tools only**: finish one sequence before starting the next; never overlap calls.
- **NO SCREENSHOTS** during workflow execution. Report failures via text only.
- **ASK FOR MISSING ASSETS**: if an image or region is unclear, pause and request updated references before proceeding.

## Reference Images (Use with `wait_for_element`)
| Image Name | Purpose | Timeout |
| --- | --- | --- |
| `evn/login_button_home.png` | Home page loaded; “Đăng nhập” button visible | 10s |
| `evn/username_field.png` | Username field visible inside login modal | 10s |
| `evn/password_field.png` | Password field visible | 10s |
| `evn/login_button_form.png` | Form submit button ready | 10s |
| `evn/view_all_invoices_button.png` | “Xem tất cả hoá đơn” button rendered | 12s |
| `evn/download_button.png` | Invoice table row with download button visible | 12s |
| `evn/pdf_option.png` | PDF option inside download popup | 10s |
| `evn/close_popup.png` | Popup close icon | 10s |

> Regions for these images follow the reference coordinates above. If visuals differ on your screen, pause and request updated assets.

## Step-by-Step Procedure

## Step-by-Step Procedure
Each action MUST follow this sequence:
1. `wait_for_element(image, timeout)` if the step references an image (retry once; STOP if still failing).
2. `move_mouse(reference_x, reference_y)` using the coordinates above.
3. `click_mouse` (or perform the documented interaction).
4. `type_credential_field` or other input tools only after the click.
5. `wait(seconds)` only when explicitly instructed (e.g., to avoid overwhelming popups).

1. **Open Browser and Navigate**
   - Call the browser-opening tool with `https://www.evnhcmc.vn`.
   - **Validate** home login button: `wait_for_element("evn/login_button_home.png", timeout=10)`.
2. **Select Credentials**
   - Call `get_credentials()` and choose the credential entry labeled for the EVN portal (e.g., `evn_portal`). Only ask the user if multiple choices could apply.
3. **Start Login**
   - `wait_for_element("evn/login_button_home.png", timeout=10)` → `move_mouse(1550, 180)` → `click_mouse`.
4. **Enter Username**
   - `wait_for_element("evn/username_field.png", timeout=10)` → `move_mouse(880, 385)` → `click_mouse`.
   - Type username: `type_credential_field(credential_id, "username")`.
5. **Enter Password**
   - `wait_for_element("evn/password_field.png", timeout=10)` → `move_mouse(880, 475)` → `click_mouse`.
   - Type password: `type_credential_field(credential_id, "password")`.
6. **Submit Login**
   - `wait_for_element("evn/login_button_form.png", timeout=10)` → `move_mouse(950, 600)` → `click_mouse`.
   - Allow the dashboard to load by retrying `wait_for_element("evn/view_all_invoices_button.png", timeout=12)`.
7. **Navigate to Invoice List**
   - Scroll once with `scroll(-200)` to reveal the invoices section.
   - `wait_for_element("evn/view_all_invoices_button.png", timeout=12)` → `move_mouse(1440, 555)` → `click_mouse`.
8. **Download Invoices**
   - `wait_for_element("evn/download_button.png", timeout=12)` to confirm the table is visible.
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `y = 680 + (n * 50)`.
     - `move_mouse(1505, y)` → `click_mouse`.
     - Popup sequence (validate before every click):
       - `wait_for_element("evn/pdf_option.png", timeout=10)` → `move_mouse(1080, 580)` → `click_mouse`.
       - `wait_for_element("evn/close_popup.png", timeout=10)` → `move_mouse(1115, 445)` → `click_mouse`.
     - `wait(1)` before moving to the next row.
9. **Confirm Completion**
   - Verify all requested downloads have started (download shelf or confirmation indicator). Do not capture screenshots unless explicitly instructed outside this workflow.

## Recovery Guidance
- If `wait_for_element` fails, retry once. If it fails again, **STOP AND ESCALATE** with the failing image name.
- If moving/clicking an element fails twice or the popup controls do not appear, **STOP AND ESCALATE** for updated instructions.
- If `type_credential_field` reports an error, reconfirm the credential reference and field name with the user before retrying once.
- For authentication errors, report the problem and await further instructions.

## Completion Criteria
- All requested invoices have initiated downloads.
- Final report lists the workflow name, actions performed (login, navigation, download count), and confirms completion without exposing credential data.
