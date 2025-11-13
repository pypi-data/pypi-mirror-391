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

## Step-by-Step Procedure
Use the `wait(seconds)` tool to satisfy every pause. For each element, **follow this exact order**:
1. `move_mouse(reference_x, reference_y)` using the coordinates above (auto-scaled by the mouse tool).
2. `click_mouse` (or perform the required input such as drag or scroll).
3. `wait` for the documented duration.

1. **Open Browser and Navigate**
   - Call the browser-opening tool with `https://www.evnhcmc.vn` and `wait(2)` for the home page to load.
2. **Select Credentials**
   - Call `get_credentials()` and choose the credential entry labeled for the EVN portal (e.g., `evn_portal`). Only ask the user if multiple choices could apply.
3. **Start Login**
   - `move_mouse(1550, 180)` → `click_mouse` → `wait(1)`.
4. **Enter Username**
   - Focus field: `move_mouse(880, 385)` → `click_mouse`.
   - Type: `type_credential_field(credential_id, "username")` → `wait(1)`.
5. **Enter Password**
   - Focus field: `move_mouse(880, 475)` → `click_mouse`.
   - Type: `type_credential_field(credential_id, "password")` → `wait(1)`.
6. **Submit Login**
   - `move_mouse(950, 600)` → `click_mouse` → `wait(3)` for the account page to load.
7. **Navigate to Invoice List**
   - Scroll once with `scroll(-200)` to reveal the invoices section.
   - `move_mouse(1440, 555)` → `click_mouse` → `wait(5)` for the invoice list to render.
8. **Download Invoices**
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `y = 680 + (n * 50)`.
     - `move_mouse(1505, y)` → `click_mouse` → `wait(1)` for the popup.
     - Popup actions:
       - `move_mouse(1080, 580)` → `click_mouse` (select PDF).
       - `move_mouse(1115, 445)` → `click_mouse` (close popup).
     - `wait(1)` before moving to the next row.
9. **Confirm Completion**
   - Verify all requested downloads have started (download shelf or confirmation indicator). Capture a screenshot only if required for evidence or debugging.

## Recovery Guidance
- If a page or popup fails to load within the expected wait time, `wait(3)` and retry the action once.
- If moving/clicking an element fails twice or the popup controls do not appear, **STOP AND ESCALATE** for updated instructions.
- If `type_credential_field` reports an error, reconfirm the credential reference and field name with the user before retrying once.
- For authentication errors, report the problem and await further instructions.

## Completion Criteria
- All requested invoices have initiated downloads.
- Final report lists the workflow name, actions performed (login, navigation, download count), and confirms completion without exposing credential data.
