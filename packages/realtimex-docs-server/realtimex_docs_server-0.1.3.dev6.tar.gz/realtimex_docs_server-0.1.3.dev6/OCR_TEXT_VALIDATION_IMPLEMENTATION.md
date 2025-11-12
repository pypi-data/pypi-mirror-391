# OCR Text Validation Implementation

**Target Repository:** `realtimex-pyautogui-server`
**Implementation Scope:** Add `wait_for_text` tool for dynamic element validation
**Priority:** High - Required for reliable automation workflows

---

## Problem Statement

Current automation workflows rely on **fixed wait times** to handle page loading and element rendering:

```python
# Current approach (unreliable)
open_browser("https://example.com/login")
wait(3)  # Hope the page loaded in 3 seconds
move_mouse(500, 90)
click_mouse()
```

**Critical issues:**
- Network speed varies (slow connections need longer waits, fast connections waste time)
- CPU performance differs across machines
- Page complexity affects load time
- No validation that expected elements actually appeared
- Agent may click before element is ready → automation fails
- Over-waiting on fast connections → poor user experience

**Real-world impact:**
- FPT invoice workflow uses `wait(3)` after browser open, hoping login page loads
- EVN portal uses `wait(2)` between steps, with no confirmation elements are ready
- Failures occur on slow networks when pages take >3s to load
- Wasted time on fast networks when pages load in <1s

---

## Chosen Solution: OCR-Based Text Detection

Implement a **`wait_for_text`** tool that uses OCR (Optical Character Recognition) to detect when specific text appears on screen, enabling dynamic waiting that adapts to actual page load times.

### Why OCR?

**Advantages over alternatives:**
- ✅ **No maintenance overhead**: No reference images to capture, version control, or update when UI changes
- ✅ **Theme-independent**: Works across light/dark modes, different color schemes
- ✅ **Resolution-independent**: Text detection works at any screen resolution
- ✅ **Handles dynamic content**: Can detect user-specific text (e.g., "Welcome, John")
- ✅ **Leverages existing coordinate system**: Uses the same region-based approach already implemented
- ✅ **Self-documenting**: `wait_for_text("Login")` is clearer than `wait(3)`

**Trade-offs accepted:**
- ⚠️ OCR is CPU-intensive (~0.5-1s per check with regions)
- ⚠️ Requires Tesseract OCR engine installed on deployment systems
- ⚠️ Poll interval of 1 second (acceptable for most use cases)

**Alternatives considered and rejected:**
- Image-based matching: High maintenance (must capture/update reference images)
- Pixel stability detection: Doesn't validate specific elements appeared
- Browser automation APIs: Not applicable (workflows include desktop apps, not just browsers)

---

## Implementation Specification

### Tool: `wait_for_text`

**Purpose:** Wait for specific text to appear in a screen region, with configurable timeout.

**Function Signature:**

```python
@mcp.tool()
def wait_for_text(
    text: str = Field(
        description="Text to find on screen (e.g., 'Login', 'Welcome', 'Submit')."
    ),
    timeout: float = Field(
        default=10.0,
        gt=0.0,
        le=30.0,
        description="Maximum seconds to wait for text to appear (0 < timeout ≤ 30).",
    ),
    region: tuple[int, int, int, int] | None = Field(
        default=None,
        description="Screen region to search as (x, y, width, height) from reference screen (1920×1080). If None, searches full screen. Regions are automatically scaled to current screen resolution.",
    ),
    case_sensitive: bool = Field(
        default=False,
        description="Whether to match text case-sensitively. Default: False (case-insensitive).",
    ),
) -> Dict[str, Any]:
    """
    Wait for specific text to appear in a screen region using OCR.

    Polls at 1-second intervals until text is found or timeout is reached.
    Returns immediately when text is detected.

    Examples:
        # Wait for login page to load (check header region)
        wait_for_text("Username", region=(400, 70, 200, 40), timeout=10)

        # Wait for dashboard after login
        wait_for_text("Welcome", region=(800, 50, 400, 80), timeout=15)

        # Full-screen search (slower)
        wait_for_text("Error", timeout=5)
    """
```

**Return Value:**

```python
# Success - text found before timeout
{
    "status": "success",
    "found": True,
    "message": "Text 'Login' found in region",
    "elapsed_seconds": 2.3,
    "detected_text": "Username\nLogin\nPassword"  # Full OCR output for debugging
}

# Failure - timeout reached
{
    "status": "error",
    "found": False,
    "message": "Text 'Login' not found within 10.0s timeout",
    "elapsed_seconds": 10.0
}
```

---

## Implementation Details

### Algorithm

```python
import time
import pyautogui
import pytesseract
from typing import Any, Dict

def wait_for_text(
    text: str,
    timeout: float = 10.0,
    region: tuple[int, int, int, int] | None = None,
    case_sensitive: bool = False,
) -> Dict[str, Any]:
    start_time = time.time()
    poll_interval = 1.0  # 1 second between checks (OCR is CPU-intensive)

    while True:
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed >= timeout:
            return {
                "status": "error",
                "found": False,
                "message": f"Text '{text}' not found within {timeout}s timeout",
                "elapsed_seconds": round(elapsed, 1),
            }

        try:
            # Screenshot the region (or full screen)
            if region:
                # Scale region coordinates to current screen resolution
                scaled_region = _scale_region(*region)
                screenshot = pyautogui.screenshot(region=scaled_region)
            else:
                screenshot = pyautogui.screenshot()

            # Perform OCR
            detected_text = pytesseract.image_to_string(screenshot)

            # Check if text is present
            if case_sensitive:
                text_found = text in detected_text
            else:
                text_found = text.lower() in detected_text.lower()

            if text_found:
                return {
                    "status": "success",
                    "found": True,
                    "message": f"Text '{text}' found in {'region' if region else 'screen'}",
                    "elapsed_seconds": round(elapsed, 1),
                    "detected_text": detected_text.strip(),
                }

        except Exception as exc:
            # Continue polling even if OCR fails once
            pass

        # Wait before next poll (don't exceed timeout)
        time.sleep(min(poll_interval, timeout - elapsed))


def _scale_region(
    x: int, y: int, width: int, height: int,
    reference_width: int = 1920,
    reference_height: int = 1080,
) -> tuple[int, int, int, int]:
    """
    Scale region coordinates from reference resolution to current screen.

    Follows same pattern as _scale_coordinates() for consistency.
    """
    current_screen = pyautogui.size()

    scale_x = current_screen.width / reference_width
    scale_y = current_screen.height / reference_height

    return (
        int(x * scale_x),
        int(y * scale_y),
        int(width * scale_x),
        int(height * scale_y),
    )
```

### Integration Points

**File:** `reference/realtimex_pyautogui_server/server.py`

**Dependencies to add:**

```python
# Add to imports at top of server.py
import pytesseract
from typing import Any  # Update existing typing import
```

**Tool registration:**

The `@mcp.tool()` decorator will automatically register the tool. Add the function after the existing tools (e.g., after `scroll()`).

**Dependency declaration:**

Update the `mcp` instance dependencies:

```python
mcp = FastMCP(
    "RealTimeX PyAutoGUI Server",
    dependencies=["pyautogui", "Pillow", "pytesseract"],  # Add pytesseract
)
```

---

## System Requirements

### Tesseract OCR Installation

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
apt-get install tesseract-ocr
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

**Path Configuration (if needed):**
```python
# If Tesseract is not in PATH, configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
```

### Python Dependencies

Add to package configuration (e.g., `pyproject.toml` or `requirements.txt`):

```toml
dependencies = [
    "pyautogui>=0.9.54",
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0",
]
```

---

## Usage Examples

### Example 1: FPT Login Workflow (Before/After)

**Before (unreliable fixed waits):**
```python
open_browser("https://onmember.fpt.vn/login")
wait(3)  # Hope page loaded
move_mouse(260, 525)  # Username field
click_mouse()
```

**After (dynamic validation):**
```python
open_browser("https://onmember.fpt.vn/login")
wait_for_text("Username", region=(200, 500, 150, 50), timeout=10)  # Wait for login form
move_mouse(260, 525)  # Now certain field is ready
click_mouse()
```

**Benefits:**
- Returns in 1-2s on fast networks (vs. always waiting 3s)
- Waits up to 10s on slow networks (vs. failing after 3s)
- Validates page actually loaded before proceeding

---

### Example 2: Multi-Step Workflow with Validation

```python
# Open browser and wait for login form
open_browser("https://example.com/login")
wait_for_text("Username", region=(400, 70, 200, 40), timeout=10)

# Enter username
move_mouse(500, 90)
click_mouse()
type_credential_field(cred_id, "username")

# Wait for password field to appear (some forms load in stages)
wait_for_text("Password", region=(400, 140, 200, 40), timeout=5)

# Enter password
move_mouse(500, 160)
click_mouse()
type_credential_field(cred_id, "password")

# Click login
move_mouse(525, 235)
click_mouse()

# Wait for successful login - dashboard appears
wait_for_text("Welcome", region=(800, 50, 400, 80), timeout=15)
```

---

### Example 3: Error Detection

```python
# Click submit button
move_mouse(500, 300)
click_mouse()

# Wait for either success or error
result = wait_for_text("Success", region=(400, 200, 600, 100), timeout=10)

if not result["found"]:
    # Check if error appeared instead
    error_check = wait_for_text("Error", region=(400, 200, 600, 100), timeout=1)
    if error_check["found"]:
        return {"error": "Form validation failed", "details": error_check["detected_text"]}
```

---

## Performance Considerations

### Poll Interval Rationale

**Why 1 second?**
- OCR is CPU-intensive (~0.5-1s per check with regions)
- Balance between responsiveness and system load
- Acceptable latency for page loads (most pages load in 2-5 seconds)
- Prevents excessive CPU usage during waiting

**Region-based scanning performance:**
```python
# Fast: Scan small targeted region (200×40 pixels)
wait_for_text("Login", region=(400, 200, 200, 40))
# OCR time: ~0.1-0.3s per check

# Slow: Scan full screen (1920×1080 pixels)
wait_for_text("Login")  # region=None
# OCR time: ~1-3s per check
```

**Best practice:** Always specify regions to minimize OCR processing time.

---

### Region Selection Tips

**1. Tight regions around expected text**
```python
# Good: Label region only (200×40 pixels)
wait_for_text("Username", region=(400, 70, 200, 40))

# Bad: Large region (600×400 pixels) - slower OCR
wait_for_text("Username", region=(300, 50, 600, 400))
```

**2. Strategic positioning**
```python
# Detect field labels (more reliable than input fields)
wait_for_text("Password", region=(400, 140, 200, 40))  # Label area

# Not: Input field itself (no text to detect)
wait_for_text("password_field", region=(500, 160, 300, 30))  # Won't work - field is empty
```

**3. Multiple text variations**
```python
# Some sites use different text - check primary first, then fallback
result = wait_for_text("Sign In", region=(450, 210, 150, 50), timeout=5)
if not result["found"]:
    result = wait_for_text("Login", region=(450, 210, 150, 50), timeout=1)
```

---

## Testing Requirements

### Unit Tests

**Test cases to implement:**

1. **Fast detection** (text appears in <1s)
   - Verify tool returns in ~1s, not waiting full timeout
   - Confirms adaptive timing works

2. **Slow detection** (text appears in 5-8s)
   - Verify tool continues polling and finds text
   - Confirms patience for slow loads

3. **Timeout behavior** (text never appears)
   - Verify timeout after specified duration
   - Verify error message is helpful

4. **Case sensitivity**
   - `wait_for_text("LOGIN", case_sensitive=False)` finds "login"
   - `wait_for_text("LOGIN", case_sensitive=True)` doesn't find "login"

5. **Region vs. full screen**
   - Verify region coordinates are scaled correctly
   - Verify region-based search is faster than full screen

6. **Coordinate scaling**
   - Test on different screen resolutions
   - Verify regions scale correctly (e.g., 1920×1080 → 2560×1440)

### Integration Tests

**Real-world scenario:**

```python
# Test FPT login page detection
def test_fpt_login_detection():
    open_browser("https://onmember.fpt.vn/login")
    result = wait_for_text("Username", region=(200, 500, 150, 50), timeout=15)
    assert result["status"] == "success"
    assert result["found"] == True
    assert result["elapsed_seconds"] < 15
```

---

## Error Handling

### Common Issues and Solutions

**1. Tesseract not found**
```
pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```
**Solution:** Install Tesseract OCR engine, or configure path in code.

**2. OCR accuracy issues (text not detected)**
- Verify region coordinates are correct (screenshot and check)
- Try case-insensitive matching (`case_sensitive=False`)
- Increase region size slightly (might be clipping text)
- Check if text has poor contrast (light gray on white)

**3. False timeouts (text is visible but not found)**
- OCR may not recognize unusual fonts or stylized text
- Try full-screen search instead of region
- Consider alternative text in the same area

**4. Slow performance**
- Ensure regions are used (not full-screen scans)
- Check Tesseract installation (binary vs. source build)
- Monitor CPU usage during polling

---

## Future Enhancements (Not in Scope)

These features are **explicitly deferred** for now:

1. `verify_text_visible()` - Immediate check without polling (use `wait_for_text(..., timeout=1)` instead)
2. `wait_for_any_text([...])` - Match multiple text options in one call
3. `wait_for_text_gone(...)` - Wait for text to disappear (e.g., loading spinners)
4. OCR preprocessing - Image enhancement for better accuracy
5. Image-based element detection - For icons/logos (use OCR for MVP)

---

## Acceptance Criteria

**Definition of Done:**

- ✅ `wait_for_text` tool implemented with all parameters (text, timeout, region, case_sensitive)
- ✅ Region coordinate scaling works correctly (follows existing `_scale_coordinates` pattern)
- ✅ Tool registered with FastMCP and appears in tool list
- ✅ Returns correct status format (`{"status": "success/error", "found": bool, "message": str, "elapsed_seconds": float}`)
- ✅ Poll interval is 1 second (not faster)
- ✅ pytesseract dependency added to package configuration
- ✅ Tesseract installation documented in README
- ✅ Unit tests cover success, timeout, and case sensitivity
- ✅ Integration test validates real page load detection
- ✅ Code follows existing patterns (same style as `wait()`, `move_mouse()`, etc.)
- ✅ No breaking changes to existing tools

---

## Implementation Checklist

**Step 1: Dependencies**
- [ ] Add `pytesseract>=0.3.10` to dependencies
- [ ] Update `mcp` instance to include "pytesseract" in dependencies list
- [ ] Add `import pytesseract` and `from typing import Any` to imports
- [ ] Document Tesseract installation requirements

**Step 2: Core Implementation**
- [ ] Implement `_scale_region()` helper function (follows `_scale_coordinates()` pattern)
- [ ] Implement `wait_for_text()` with polling logic
- [ ] Add `@mcp.tool()` decorator
- [ ] Handle all parameters: text, timeout, region, case_sensitive
- [ ] Return correct response format

**Step 3: Testing**
- [ ] Unit tests: fast detection, timeout, case sensitivity
- [ ] Integration test: real page load (FPT login or similar)
- [ ] Test coordinate scaling on different resolutions
- [ ] Verify error handling (missing Tesseract, invalid regions)

**Step 4: Documentation**
- [ ] Add usage examples to tool docstring
- [ ] Update README with Tesseract installation instructions
- [ ] Document region selection best practices

**Step 5: Validation**
- [ ] Code review for consistency with existing patterns
- [ ] Performance test: verify 1s poll interval
- [ ] Verify no breaking changes to existing tools
- [ ] Confirm tool appears in MCP tool list

---

## Questions for Implementer

If you encounter any of these scenarios, please escalate:

1. **Tesseract path configuration**: Should we auto-detect Tesseract path, or require manual configuration?
2. **OCR accuracy**: Should we add image preprocessing (grayscale, contrast) in this phase, or defer?
3. **Poll interval**: Is 1 second acceptable, or should we make it configurable via parameter?
4. **Detected text length**: Should we truncate long detected_text in responses, or return full OCR output?
5. **Error handling**: Should single OCR failures (mid-polling) be logged, or silently ignored?

---

## Document Metadata

- **Version:** 1.0
- **Author:** RTA (realtimex-computer-use team)
- **Date:** 2025-11-12
- **Target Repository:** realtimex-pyautogui-server
- **Related Documents:**
  - `DYNAMIC_ELEMENT_VALIDATION_DESIGN.md` (upstream design exploration)
  - `COORDINATE_SCALING_IMPLEMENTATION.md` (coordinate system reference)
- **Status:** Ready for Implementation