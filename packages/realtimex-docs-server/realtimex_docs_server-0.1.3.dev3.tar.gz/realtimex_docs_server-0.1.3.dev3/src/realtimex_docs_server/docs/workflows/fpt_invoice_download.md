# Workflow: FPT Portal Invoice Download

## Overview
Download the requested number of most recent paid invoices from the FPT portal using normalized coordinates and the documented timing requirements. Always follow the documented steps in order, call the wait tool for each pause, and rely on the browser-opening tool instead of clicking desktop icons.

## Prerequisites
- Valid FPT portal credentials supplied by the user (username and password).
- Stable internet connection.
- Firefox browser installed and accessible at the documented dock position.
- Download directory configured to save invoices without additional prompts.

## Coordinate Reference (Normalized, reference screen 1920×1080)
Use this table with the `calculate_screen_coordinates(normalized_x, normalized_y)` tool before every interaction.

| Element | Normalized (x, y) | Description |
| --- | --- | --- |
| `browser_address_bar` | (0.260, 0.083) | Address bar for URL entry |
| `username_field` | (0.135, 0.486) | Username input field |
| `username_submit_button` | (0.167, 0.565) | Button that advances from username entry to password entry |
| `password_field` | (0.141, 0.509) | Password input field |
| `login_button_final` | (0.167, 0.620) | Final login button |
| `contracts_menu` | (0.037, 0.361) | “Hợp Đồng” menu item |
| `view_invoices_link` | (0.844, 0.407) | “xem hóa đơn” link |
| `paid_invoices_tab` | (0.219, 0.315) | “Đã thanh toán” tab |
| `first_invoice_download_button` | (0.927, 0.412) | Download button for newest invoice |

**Invoice Row Offset**: Each additional invoice download button is located `0.065` lower on the normalized y-axis. For invoice index `n`, compute `normalized_y = 0.412 + (n * 0.065)`.

## Step-by-Step Procedure
Use the `wait(seconds)` tool to satisfy every pause duration listed below. For every UI action, strictly follow this order:
1. `calculate_screen_coordinates` with the element’s normalized values.
2. `move_mouse` to the returned absolute coordinates.
3. `click_mouse` (or perform the required input).
4. `wait` for the documented duration.

1. **Open Browser and Navigate**
   - Call the browser-opening tool with the URL `https://onmember.fpt.vn/login`.
   - Wait 3 seconds for the login page to render.
2. **Select Credentials**
   - Call `get_credentials()` and select the credential entry labeled for the FPT portal (e.g., `fpt_portal`). If multiple candidates match, clarify with the user; otherwise proceed immediately.
3. **Enter Username**
   - Navigate to `username_field`, click, and call `type_credential_field(credential_id, "username")`.
   - Click `username_submit_button`, then `wait(2)` to ensure the password field is fully rendered.
4. **Enter Password**
   - Navigate to `password_field`, click, and call `type_credential_field(credential_id, "password")`.
   - Click `login_button_final`, then `wait(3)` for the dashboard to appear.
5. **Open Contracts Page**
   - Navigate to `contracts_menu`, click, then `wait(1)`.
6. **Open Invoices**
   - Navigate to `view_invoices_link`, click, then `wait(2)`.
7. **Filter Paid Invoices**
   - Navigate to `paid_invoices_tab`, click, then `wait(2)`.
8. **Download Invoices**
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `normalized_y = 0.412 + (n * 0.065)` and call `calculate_screen_coordinates(0.927, normalized_y)`.
     - Move and click to start the download, then `wait(1)` before moving to the next invoice.
9. **Confirm Completion**
   - Verify every requested download initiated (e.g., download shelf or folder confirmation). Capture a screenshot only if evidence is required or an anomaly is observed.

## Recovery Guidance
- If a page does not load within the expected wait time, call `wait(3)` and retry the previous interaction once.
- If `calculate_screen_coordinates` fails or the element does not appear within two attempts, **STOP AND ESCALATE** for updated documentation.
- If `type_credential_field` returns an error, confirm the credential reference and field name with the user before retrying once.
- For authentication failures, report the error without reattempting unless explicitly instructed.

## Completion Criteria
- All requested paid invoices have download processes started successfully.
- Final report includes the workflow name, key actions, confirmation that every download began, and notes any anomalies. Never include credential values.
