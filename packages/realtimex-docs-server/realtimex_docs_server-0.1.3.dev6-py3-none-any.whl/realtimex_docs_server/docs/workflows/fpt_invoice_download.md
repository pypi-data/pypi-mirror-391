# Workflow: FPT Portal Invoice Download

## Overview
Download the requested number of most recent paid invoices from the FPT portal using normalized coordinates and the documented timing requirements. Always follow the documented steps in order, call the wait tool for each pause, and rely on the browser-opening tool instead of clicking desktop icons.

## Prerequisites
- Valid FPT portal credentials supplied by the user (username and password).
- Stable internet connection.
- Browser-opening tool available to load the FPT portal URL directly (no assumption about which browser is installed).
- Download directory configured to save invoices without additional prompts.

## Coordinate Reference (Reference screen 1920×1080)
Use these absolute coordinates when calling `move_mouse`. The pointer tools automatically scale them for the current screen.

| Element | Coordinates (x, y) | Description |
| --- | --- | --- |
| `browser_address_bar` | (500, 90) | Address bar for URL entry |
| `username_field` | (260, 525) | Username input field |
| `username_submit_button` | (320, 610) | Button that advances from username entry to password entry |
| `password_field` | (270, 550) | Password input field |
| `login_button_final` | (320, 670) | Final login button |
| `contracts_menu` | (70, 390) | “Hợp Đồng” menu item |
| `view_invoices_link` | (1620, 440) | “xem hóa đơn” link |
| `paid_invoices_tab` | (420, 340) | “Đã thanh toán” tab |
| `first_invoice_download_button` | (1780, 445) | Download button for newest invoice |

**Invoice Row Offset**: Each additional invoice download button is `+70` on the y-axis. For invoice index `n`, compute `y = 445 + (n * 70)`.

## Reference Images (Element Validation)
**Use these with `wait_for_element(image_name, timeout)` to validate page readiness before proceeding.**

| Image Name | Purpose | Timeout |
| --- | --- | --- |
| `fpt/username_field.png` | Login page loaded, username field visible | 10s |
| `fpt/username_submit_button.png` | Username submit button visible | 10s |
| `fpt/password_field.png` | Password form appeared after username submission | 10s |
| `fpt/login_button.png` | Final login button visible | 10s |
| `fpt/contracts_menu.png` | Dashboard loaded, contracts menu visible | 15s |
| `fpt/invoices_link.png` | Contracts page loaded, invoices link visible | 10s |
| `fpt/paid_tab.png` | Paid invoices tab visible and active | 10s |
| `fpt/download_button.png` | First invoice row with download button visible | 10s |

## Step-by-Step Procedure
**For each UI action, strictly follow this order:**
1. **Validate element**: `wait_for_element(image_name, timeout)` using reference images above.
2. **Position mouse**: `move_mouse(reference_x, reference_y)` using coordinates above (auto-scaled).
3. **Interact**: `click_mouse` or `type_credential_field` as instructed.

**DO NOT proceed to next step until validation succeeds.**

1. **Open Browser and Navigate**
   - Call `open_browser("https://onmember.fpt.vn/login")`.
   - **Validate**: `wait_for_element("fpt/username_field.png", timeout=10)`.

2. **Select Credentials**
   - Call `get_credentials()` and select the credential entry labeled for the FPT portal (e.g., `fpt_portal`). If multiple candidates match, clarify with the user; otherwise proceed immediately.

3. **Enter Username**
   - Focus field: `move_mouse(260, 525)` → `click_mouse`.
   - Type username: `type_credential_field(credential_id, "username")`.
   - **Validate** button ready: `wait_for_element("fpt/username_submit_button.png", timeout=10)`.
   - Submit username: `move_mouse(320, 610)` → `click_mouse`.
   - **Validate** password form appeared: `wait_for_element("fpt/password_field.png", timeout=10)` to ensure the password field loads.

4. **Enter Password**
   - Focus field: `move_mouse(270, 550)` → `click_mouse`.
   - Type password: `type_credential_field(credential_id, "password")`.
   - **Validate** login button ready: `wait_for_element("fpt/login_button.png", timeout=10)`.
   - Submit login: `move_mouse(320, 670)` → `click_mouse`.
   - **Validate** dashboard loaded: `wait_for_element("fpt/contracts_menu.png", timeout=15)` to ensure the dashboard appears.

5. **Open Contracts Page**
   - Click menu: `move_mouse(70, 390)` → `click_mouse`.
   - Wait: `wait(2)` for page transition.
   - **Validate** invoices link visible: `wait_for_element("fpt/invoices_link.png", timeout=10)` to ensure the contracts page loaded.

6. **Open Invoices**
   - Click invoices link: `move_mouse(1620, 440)` → `click_mouse`.
   - Wait: `wait(2)` for invoices list to load.

7. **Filter Paid Invoices**
   - Click paid tab: `move_mouse(420, 340)` → `click_mouse`.
   - **Validate** paid tab active: `wait_for_element("fpt/paid_tab.png", timeout=10)` to ensure the paid invoices filter applied.

8. **Download Invoices**
   - **Validate** first invoice row visible: `wait_for_element("fpt/download_button.png", timeout=10)` to ensure invoice list rendered.
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `y = 445 + (n * 70)`.
     - Click download button: `move_mouse(1780, y)` → `click_mouse`.
     - Wait: `wait(1)` before next invoice to avoid overwhelming the browser.

9. **Confirm Completion**
   - Verify every requested download initiated (e.g., download shelf or folder confirmation). Capture a screenshot only if evidence is required or an anomaly is observed.

## Recovery Guidance
- If `wait_for_element` times out on first attempt, retry once with the same timeout before escalating. If retry fails, capture a screenshot and **STOP AND ESCALATE** for updated reference image or timeout adjustment.
- If moving/clicking an element fails twice or the coordinates no longer match on-screen elements, **STOP AND ESCALATE** for updated documentation.
- If `type_credential_field` returns an error, confirm the credential reference and field name with the user before retrying once.
- For authentication failures, report the error without reattempting unless explicitly instructed.

## Completion Criteria
- All requested paid invoices have download processes started successfully.
- Final report includes the workflow name, key actions, confirmation that every download began, and notes any anomalies. Never include credential values.
