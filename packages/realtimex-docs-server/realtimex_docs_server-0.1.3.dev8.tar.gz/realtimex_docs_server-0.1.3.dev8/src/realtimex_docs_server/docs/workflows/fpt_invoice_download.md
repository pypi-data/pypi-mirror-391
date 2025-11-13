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

## Execution Rules
- **Validate → Move → Click → Type**. Every interaction MUST follow that sequence. Skipping any step is a failure.
- **Image validation is mandatory** whenever an image is listed. Call `wait_for_element(image, timeout)` (retry once). STOP the workflow if validation fails twice.
- **Pointer order is STRICT**: `move_mouse` MUST ALWAYS precede `click_mouse`. Moving without clicking never focuses a field.
- **Typing order is STRICT**: `move_mouse` → `click_mouse` → `type_credential_field` (or `type_text`). Typing without a preceding click is FORBIDDEN.
- **Sequential tool calls only**: finish the full sequence for one step BEFORE starting another. NEVER overlap tool execution.
- **No screenshots**: if validation fails, report the issue and stop. Do not capture the screen.
- **Missing assets**: if an image or region appears outdated, PAUSE and request an updated asset before proceeding.

## Reference Images (Use with `wait_for_element`)
| Image Name | Purpose | Timeout |
| --- | --- | --- |
| `fpt/username_field.png` | Login form loaded; username input visible | 12s |
| `fpt/username_submit_button.png` | Submit button ready after username entry | 12s |
| `fpt/password_field.png` | Password field rendered after submitting username | 12s |
| `fpt/login_button.png` | Final login button available | 12s |
| `fpt/contracts_menu.png` | Dashboard loaded (`Hợp Đồng` menu visible) | 15s |
| `fpt/invoices_link.png` | Contracts page loaded; invoices link visible | 12s |
| `fpt/paid_tab.png` | Paid tab rendered or active | 12s |
| `fpt/download_button.png` | Invoice list rendered with download button visible | 12s |

> Regions for these images follow the reference coordinates above. If they do not match your environment, pause immediately and request updated regions/images.

## Step-by-Step Procedure
For each action: **validate (if image listed) → move_mouse(reference_x, reference_y) → click_mouse → type (if needed)**. `wait(seconds)` is used ONLY when explicitly stated.

1. **Open Browser and Navigate**
   - Call `open_browser("https://onmember.fpt.vn/login")`.
   - **Validate**: `wait_for_element("fpt/username_field.png", timeout=12)`. Retry once; STOP if still missing.

2. **Select Credentials**
   - Call `get_credentials()` and select the credential entry labeled for the FPT portal (e.g., `fpt_portal`). If multiple candidates match, clarify with the user; otherwise proceed immediately.

3. **Enter Username**
   - Focus field: `move_mouse(260, 525)` → `click_mouse`.
   - Type username: `type_credential_field(credential_id, "username")`.
   - **Validate** submit button ready: `wait_for_element("fpt/username_submit_button.png", timeout=12)`.
   - Submit username: `move_mouse(320, 610)` → `click_mouse`.
   - **Validate** password field: `wait_for_element("fpt/password_field.png", timeout=12)`.

4. **Enter Password**
   - Focus field: `move_mouse(270, 550)` → `click_mouse`.
   - Type password: `type_credential_field(credential_id, "password")`.
   - **Validate** login button ready: `wait_for_element("fpt/login_button.png", timeout=12)`.
   - Submit login: `move_mouse(320, 670)` → `click_mouse`.
   - **Validate** dashboard loaded: `wait_for_element("fpt/contracts_menu.png", timeout=15)`.

5. **Open Contracts Page**
   - Click menu: `move_mouse(70, 390)` → `click_mouse`.
   - **Validate** invoices link visible: `wait_for_element("fpt/invoices_link.png", timeout=12)`.

6. **Open Invoices**
   - Click invoices link: `move_mouse(1620, 440)` → `click_mouse`.
   - **Validate** paid tab rendered: `wait_for_element("fpt/paid_tab.png", timeout=12)`.

7. **Filter Paid Invoices**
   - Click paid tab: `move_mouse(420, 340)` → `click_mouse`.
   - **Validate** paid tab active: `wait_for_element("fpt/paid_tab.png", timeout=12)`.

8. **Download Invoices**
   - **Validate** invoice rows visible: `wait_for_element("fpt/download_button.png", timeout=12)`.
   - For each invoice index `n` from `0` to `(requested_count - 1)`:
     - Compute `y = 445 + (n * 70)`.
     - Click download button: `move_mouse(1780, y)` → `click_mouse`.
     - `wait(1)` before the next invoice to avoid overwhelming the browser.

9. **Confirm Completion**
   - Verify every requested download initiated (e.g., download shelf or folder confirmation). Do not collect screenshots unless explicitly asked outside this workflow.

## Recovery Guidance
- If `wait_for_element` times out, retry once. If it fails again, **STOP** and report: `"Element image <name> not detected. Workflow terminated."`
- If `type_credential_field` returns an error, confirm the credential reference with the user before retrying once.
- For authentication failures, report the error without reattempting unless explicitly instructed.

## Completion Criteria
- All requested paid invoices have download processes started successfully.
- Final report includes the workflow name, key actions, confirmation that every download began, and notes any anomalies. Never include credential values.
