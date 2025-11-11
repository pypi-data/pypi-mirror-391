# Workflow: EVN Portal Invoice Download

## Overview
Download the requested number of most recent invoices from the EVN portal using normalized coordinates, secure credential typing, and documented timing requirements. Follow the steps exactly, call the wait tool for every pause, and rely on browser-opening and secure-credential tools for navigation and login.

## Prerequisites
- Valid EVN portal credentials provided by the user.
- Stable internet connection.
- Browser-opening tool available to load the EVN portal URL directly.
- Download directory configured to save invoices without additional prompts.

## Coordinate Reference (Normalized, reference screen 1920×1080)
Use this table with `calculate_screen_coordinates(normalized_x, normalized_y)` before each interaction.

| Element | Normalized (x, y) | Description |
| --- | --- | --- |
| `login_button_home` | (0.807, 0.167) | “Đăng nhập” button on home page |
| `username_field` | (0.458, 0.356) | Username (Số điện thoại) input |
| `password_field` | (0.458, 0.440) | Password (Mật khẩu) input |
| `login_button_form` | (0.495, 0.556) | “Đăng nhập” button on login form |
| `view_all_invoices_button` | (0.750, 0.514) | “Xem tất cả hoá đơn” button |
| `download_button_row1` | (0.784, 0.630) | Download button for first invoice row |
| `download_popup_pdf_option` | (0.562, 0.537) | PDF version option in popup |
| `download_popup_close` | (0.581, 0.412) | Close icon for the download popup |

**Invoice Row Offset**: Each subsequent invoice row’s download button is `+0.046` higher on the normalized y-axis. For invoice index `n`, compute `normalized_y = 0.630 + (n * 0.046)`.

## Step-by-Step Procedure
Use the `wait(seconds)` tool to satisfy every pause. For each element, **follow this exact order**:
1. `calculate_screen_coordinates(normalized_x, normalized_y)`
2. `move_mouse` to the resulting coordinates
3. `click_mouse` (or perform the required input)
4. `wait` for the documented duration

1. **Open Browser and Navigate**
   - Call the browser-opening tool with `https://www.evnhcmc.vn` and `wait(2)` for the home page to load.
2. **Select Credentials**
   - Call `get_credentials()` and choose the credential entry labeled for the EVN portal (e.g., `evn_portal`). Only ask the user if multiple choices could apply.
3. **Start Login**
   - `calculate_screen_coordinates` for `login_button_home` → `move_mouse` → `click_mouse` → `wait(1)`.
4. **Enter Username**
   - Focus field: `calculate_screen_coordinates` for `username_field` → `move_mouse` → `click_mouse`.
   - Type: `type_credential_field(credential_id, "username")` → `wait(1)`.
5. **Enter Password**
   - Focus field: `calculate_screen_coordinates` for `password_field` → `move_mouse` → `click_mouse`.
   - Type: `type_credential_field(credential_id, "password")` → `wait(1)`.
6. **Submit Login**
   - `calculate_screen_coordinates` for `login_button_form` → `move_mouse` → `click_mouse` → `wait(3)` for the account page to load.
7. **Navigate to Invoice List**
   - Scroll once with `scroll(-200)` to reveal the invoices section.
   - `calculate_screen_coordinates` for `view_all_invoices_button` → `move_mouse` → `click_mouse` → `wait(5)` for the invoice list to render.
8. **Download Invoices**
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `normalized_y = 0.630 + (n * 0.046)`.
     - `calculate_screen_coordinates(0.784, normalized_y)` → `move_mouse` → `click_mouse` → `wait(1)` for the popup.
     - Popup actions:
       - `calculate_screen_coordinates` for `download_popup_pdf_option` → `move_mouse` → `click_mouse`.
       - `calculate_screen_coordinates` for `download_popup_close` → `move_mouse` → `click_mouse`.
     - `wait(1)` before moving to the next row.
9. **Confirm Completion**
   - Verify all requested downloads have started (download shelf or confirmation indicator). Capture a screenshot only if required for evidence or debugging.

## Recovery Guidance
- If a page or popup fails to load within the expected wait time, `wait(3)` and retry the action once.
- If `calculate_screen_coordinates` or the download popup actions fail twice, **STOP AND ESCALATE** for updated instructions.
- If `type_credential_field` reports an error, reconfirm the credential reference and field name with the user before retrying once.
- For authentication errors, report the problem and await further instructions.

## Completion Criteria
- All requested invoices have initiated downloads.
- Final report lists the workflow name, actions performed (login, navigation, download count), and confirms completion without exposing credential data.
