# Dynamic Element Validation Design

## Problem Statement

Current automation workflows use **fixed wait times** to handle page loading and element rendering:

```python
# Current approach (unreliable)
open_browser("https://example.com")
wait(3)  # Hope the page loaded in 3 seconds
move_mouse(500, 90)
click_mouse()
```

**Issues with fixed waits:**
- Network speed varies (slow connections need longer waits)
- CPU performance differs across machines
- Page complexity affects load time
- Wasted time when page loads quickly
- Failures when page loads slowly
- No way to detect if action actually succeeded

**Critical problems:**
- Agent might click before element appears → automation fails
- Agent waits too long on fast connections → poor UX
- No validation that expected element is actually visible
- No confirmation that action (click, type) had expected effect

## Requirements for Robust Solution

### Must-Have Capabilities

1. **Dynamic Waiting**
   - Wait only as long as needed
   - Timeout if element never appears
   - Poll at reasonable intervals

2. **Element Validation**
   - Verify element is visible before acting
   - Confirm element appeared after action
   - Detect when page is ready

3. **Flexible Detection Methods**
   - Image-based: Find visual elements (buttons, icons)
   - Text-based: Detect specific text on screen
   - Region-based: Check screen area changes

4. **Agent-Friendly**
   - Simple to use
   - Clear success/failure feedback
   - Helpful error messages

### Nice-to-Have Capabilities

- Multiple element detection (wait for any of several elements)
- Percentage-based matching (handle slight visual changes)
- Element position return (for clicking)
- Screenshot capture on failure (debugging)

## Proposed Solutions

### Solution 1: OCR-Based Text Detection ⭐ Recommended

**Overview:** Use OCR (pytesseract) to detect specific text in defined screen regions.

**Why OCR is superior:**
- ✅ No reference images to maintain
- ✅ Works with dynamic content (user names, dates, etc.)
- ✅ Theme/style independent
- ✅ Leverages existing coordinate system for region selection
- ✅ More flexible and resilient to UI changes

**Dependency:** `pytesseract` + Tesseract OCR engine (acceptable trade-off)

**Architecture:**
```
Agent → wait_for_text("Login", region=(400, 50, 200, 100), timeout=10)
         ↓
PyAutoGUI Server → Poll every 1s
         ↓
Screenshot region → OCR → Check for text → Return when found or timeout
```

**Tools:**

#### 1. `wait_for_text` (Primary Tool)

```python
def wait_for_text(
    text: str = Field(description="Text to find on screen"),
    timeout: float = Field(default=10.0, description="Maximum seconds to wait"),
    region: tuple[int, int, int, int] | None = Field(
        default=None,
        description="Screen region to search (x, y, width, height). If None, searches full screen."
    ),
    case_sensitive: bool = Field(
        default=False,
        description="Whether to match text case-sensitively"
    )
) -> Dict[str, Any]:
    """
    Wait for specific text to appear in a screen region.

    Uses OCR to detect text. Polls at 1-second intervals.
    Combine with absolute coordinates to define precise search regions.
    """
    import time
    import pyautogui
    import pytesseract

    start_time = time.time()
    poll_interval = 1.0

    while (time.time() - start_time) < timeout:
        # Take screenshot of region
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()

        # OCR the screenshot
        detected_text = pytesseract.image_to_string(screenshot)

        # Check if text found
        if case_sensitive:
            text_found = text in detected_text
        else:
            text_found = text.lower() in detected_text.lower()

        if text_found:
            return {
                "status": "success",
                "found": True,
                "message": f"Text '{text}' found in region",
                "detected_text": detected_text.strip()  # For debugging
            }

        time.sleep(poll_interval)

    return {
        "status": "error",
        "found": False,
        "message": f"Text '{text}' not found within {timeout}s timeout"
    }
```

#### 2. `verify_text_visible` (Quick Check)

```python
def verify_text_visible(
    text: str = Field(description="Text to find"),
    region: tuple[int, int, int, int] | None = Field(
        default=None,
        description="Screen region to search (x, y, width, height)"
    ),
    case_sensitive: bool = Field(default=False)
) -> Dict[str, Any]:
    """
    Check if text is currently visible (no waiting).

    Returns immediately with true/false result.
    """
    import pyautogui
    import pytesseract

    # Take screenshot
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()

    # OCR
    detected_text = pytesseract.image_to_string(screenshot)

    # Check
    if case_sensitive:
        text_found = text in detected_text
    else:
        text_found = text.lower() in detected_text.lower()

    return {
        "status": "success",
        "visible": text_found,
        "detected_text": detected_text.strip() if text_found else None
    }
```

**Usage Pattern:**

```python
# Robust workflow with region-based OCR
open_browser("https://example.com")

# Wait for page to load - check for "Login" text in header region
result = wait_for_text(
    text="Login",
    region=(400, 50, 200, 100),  # Top-center region
    timeout=10
)

if result["found"]:
    # Page loaded - proceed with login
    move_mouse(500, 90)  # Username field
    click_mouse()
    type_credential_field(cred_id, "username")

    # Wait for password field by detecting label
    wait_for_text(
        text="Password",
        region=(400, 120, 200, 50),  # Password label region
        timeout=5
    )

    move_mouse(500, 150)  # Password field
    click_mouse()
    type_credential_field(cred_id, "password")

    # Click login button
    move_mouse(500, 200)
    click_mouse()

    # Wait for successful login - check for welcome text
    wait_for_text(
        text="Welcome",
        region=(800, 50, 400, 100),  # Dashboard header
        timeout=15
    )
```

**Advantages:**
- ✅ No reference images to maintain
- ✅ Works with dynamic text content (names, dates, etc.)
- ✅ Theme/style independent
- ✅ Leverages existing coordinate system for precise regions
- ✅ More flexible than image matching
- ✅ Case-sensitive/insensitive options
- ✅ Returns detected text for debugging

**Dependency:**
- Requires `pytesseract` and Tesseract OCR engine installation

---

### Solution 2: Image-Based Element Detection (Fallback)

**Overview:** Use PyAutoGUI's `locateOnScreen()` for visual element matching.

**Use when:**
- Need to detect non-text elements (icons, logos, images)
- Text OCR is unreliable (unusual fonts, images as text)
- Need element position for clicking

**Tool:**

```python
def wait_for_element(
    element_image: str,
    timeout: float = 10.0,
    confidence: float = 0.8
) -> Dict[str, Any]:
    """Wait for visual element to appear. Returns element position."""
    import time
    import pyautogui

    start_time = time.time()

    while (time.time() - start_time) < timeout:
        try:
            location = pyautogui.locateOnScreen(
                f"./elements/{element_image}",
                confidence=confidence
            )
            if location:
                center = pyautogui.center(location)
                return {
                    "status": "success",
                    "found": True,
                    "x": center.x,
                    "y": center.y
                }
        except:
            pass
        time.sleep(0.5)

    return {"status": "error", "found": False}
```

**Limitations:**
- Requires maintaining reference image library
- Sensitive to UI theme changes
- Requires version control of images

---

### Solution 3: Pixel/Region Change Detection

**Overview:** Detect when screen region stops changing (page finished loading).

**Tool:**

```python
def wait_for_region_stable(
    x: int, y: int,
    width: int, height: int,
    stable_duration: float = 1.0,  # Must be stable for 1s
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Wait for a screen region to stop changing.

    Useful for detecting when page has finished loading.
    """
    import time
    import pyautogui
    from PIL import ImageChops

    start_time = time.time()
    last_screenshot = None
    stable_since = None

    while (time.time() - start_time) < timeout:
        current_screenshot = pyautogui.screenshot(region=(x, y, width, height))

        if last_screenshot is not None:
            diff = ImageChops.difference(current_screenshot, last_screenshot)

            if diff.getbbox() is None:  # No changes
                if stable_since is None:
                    stable_since = time.time()
                elif (time.time() - stable_since) >= stable_duration:
                    return {
                        "status": "success",
                        "stable": True,
                        "message": "Region stable"
                    }
            else:  # Changes detected
                stable_since = None

        last_screenshot = current_screenshot
        time.sleep(0.5)

    return {
        "status": "error",
        "stable": False,
        "message": "Region did not stabilize within timeout"
    }
```

**Advantages:**
- ✅ No reference images needed
- ✅ Detects when loading finishes
- ✅ Works with any dynamic content

**Limitations:**
- ⚠️ Doesn't validate specific elements
- ⚠️ Animations/videos cause false negatives
- ⚠️ Requires knowing region coordinates

---

## Recommended Implementation Strategy

### Phase 1: OCR Text Detection (Essential) ⭐

**Implement in:** `realtimex-pyautogui-server`

**Tools to add:**
1. `wait_for_text(text, timeout, region, case_sensitive)` - Wait for text in region
2. `verify_text_visible(text, region, case_sensitive)` - Quick text check

**Dependencies:**
```toml
dependencies = [
    "pyautogui>=0.9.54",
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0"
]
```

**System requirements:**
- Tesseract OCR engine must be installed on system
- Installation:
  - macOS: `brew install tesseract`
  - Ubuntu: `apt-get install tesseract-ocr`
  - Windows: Download from GitHub releases

**Configuration:**
- Default poll interval: 1 second (OCR is CPU intensive)
- Support region-based scanning (leverages coordinate system)
- Case-sensitive and case-insensitive matching
- Return detected text for debugging

### Phase 2: Image Detection (Fallback)

**Implement in:** `realtimex-pyautogui-server`

**Tools to add:**
1. `wait_for_element(element_image, timeout, confidence)` - For non-text elements
2. `verify_element_visible(element_image, confidence)` - Quick check

**Use cases:**
- Detecting icons, logos, images
- When OCR is unreliable

### Phase 3: Advanced Features (Optional)

1. **Multiple text options:**
   ```python
   wait_for_any_text(["Login", "Sign In", "Continue"], region=(...))
   ```

2. **Text disappearance:**
   ```python
   wait_for_text_gone("Loading...", region=(...), timeout=30)
   ```

3. **Screenshot on failure:**
   ```python
   wait_for_text("Success", save_screenshot_on_fail=True)
   ```

4. **OCR with preprocessing:**
   ```python
   wait_for_text("Login", region=(...), preprocess="threshold")
   # Improve OCR accuracy with image preprocessing
   ```

---

## System Prompt Updates

### Before (Unreliable Fixed Waits)

```markdown
Login Workflow:
1. open_browser("https://example.com/login")
2. wait(3)  # Hope page loaded
3. move_mouse(500, 90)
4. click_mouse()
5. wait(1)  # Hope field is ready
6. type_credential_field(cred_id, "username")
```

### After (Robust Dynamic Waiting with OCR)

```markdown
Reference Screen: 1920×1080

Element Regions:
| Element | Region (x, y, w, h) | Expected Text | Coordinates |
|---------|---------------------|---------------|-------------|
| Username Label | (400, 70, 200, 40) | "Username" or "Email" | Username field at (500, 90) |
| Password Label | (400, 140, 200, 40) | "Password" | Password field at (500, 160) |
| Login Button | (450, 210, 150, 50) | "Login" or "Sign In" | Button at (525, 235) |
| Dashboard Header | (800, 50, 400, 80) | "Welcome" or "Dashboard" | - |

Login Workflow:
1. open_browser("https://example.com/login")
2. wait_for_text("Username", region=(400, 70, 200, 40), timeout=10)
   - Waits up to 10s for login form to appear
   - Returns immediately when "Username" label detected
   - Validates page actually loaded
3. move_mouse(500, 90)
4. click_mouse()
5. type_credential_field(cred_id, "username")
6. wait_for_text("Password", region=(400, 140, 200, 40), timeout=5)
   - Confirms password field is visible
7. move_mouse(500, 160)
8. click_mouse()
9. type_credential_field(cred_id, "password")
10. wait_for_text("Login", region=(450, 210, 150, 50), timeout=2)
    - Verify login button is ready
11. move_mouse(525, 235)
12. click_mouse()
13. wait_for_text("Welcome", region=(800, 50, 400, 80), timeout=15)
    - Confirms login succeeded and dashboard loaded
```

**Benefits:**
- ✅ Waits only as long as needed (adaptive timing)
- ✅ Validates text elements before acting
- ✅ Confirms actions succeeded
- ✅ Handles varying page load times
- ✅ Works with dynamic content (user names, etc.)
- ✅ Theme/style independent
- ✅ No image files to maintain
- ✅ Leverages existing coordinate system for precise regions

---

## Region Definition Best Practices

### System Prompt Documentation Format

Define precise regions for OCR scanning in your system prompt:

```markdown
Reference Screen: 1920×1080

OCR Validation Regions:
| Page | Element | Region (x, y, width, height) | Expected Text | Notes |
|------|---------|------------------------------|---------------|-------|
| Login | Username Label | (400, 70, 200, 40) | "Username", "Email" | Above username field |
| Login | Password Label | (400, 140, 200, 40) | "Password" | Above password field |
| Login | Login Button | (450, 210, 150, 50) | "Login", "Sign In", "Continue" | Submit button |
| Dashboard | Welcome Header | (800, 50, 400, 80) | "Welcome", "Dashboard" | Top-right area |
| Dashboard | User Name | (900, 55, 200, 30) | Dynamic (user's name) | After "Welcome" |
```

### Region Selection Tips

1. **Tight regions:** Smaller regions = faster OCR + fewer false positives
2. **Label-based:** Detect field labels rather than input fields themselves
3. **Multiple text options:** List variations ("Login", "Sign In")
4. **Strategic positioning:** Use regions that won't shift with minor UI changes
5. **Dynamic content:** OCR handles variable text (names, dates) naturally

### Region Coordinate Scaling

Since coordinates auto-scale with screen resolution:
- Define regions using reference screen (1920×1080)
- Regions scale automatically to actual screen
- Example: (400, 70, 200, 40) on 1920×1080 → (533, 93, 267, 53) on 2560×1440

---

## Error Handling Strategy

### Common Scenarios

**1. Element Never Appears (Timeout)**
```python
result = wait_for_element("login_button.png", timeout=10)

if not result["found"]:
    # Element didn't appear - handle error
    screenshot()  # Capture current state
    return {"error": "Login page did not load"}
```

**2. Error State Detection**
```python
# Check for error messages before proceeding
error_check = verify_text_visible(
    text="Error",
    region=(400, 300, 600, 100)  # Error message region
)

if error_check["visible"]:
    # Error state detected
    screenshot()
    return {
        "error": "Error message appeared",
        "details": error_check["detected_text"]
    }
```

**3. Multiple Possible Outcomes**
```python
# Wait for either success or error text
while time.time() - start < timeout:
    success = verify_text_visible("Success", region=(400, 200, 600, 100))
    if success["visible"]:
        return {"status": "success"}

    error = verify_text_visible("Error", region=(400, 200, 600, 100))
    if error["visible"]:
        return {"status": "error", "message": error["detected_text"]}

    time.sleep(1.0)
```

---

## Performance Considerations

### Polling Intervals

| Operation | Recommended Interval | Reason |
|-----------|---------------------|--------|
| OCR text detection | 1.0s | CPU intensive, balance accuracy vs. responsiveness |
| Image detection | 0.5s | Fast, lightweight (if used) |
| Region stability | 0.5s | Need quick response |

### Optimization Tips

1. **Always use regions with OCR**
   ```python
   # Faster: Scan small targeted region (RECOMMENDED)
   wait_for_text("Login", region=(400, 200, 200, 50))

   # Slower: Scan entire screen (AVOID)
   wait_for_text("Login")  # region=None
   ```
   **Impact:** Region scanning is 10-50x faster depending on region size

2. **Strategic region sizing**
   ```python
   # Good: Tight region around expected text
   wait_for_text("Submit", region=(450, 300, 150, 50))

   # Bad: Unnecessarily large region
   wait_for_text("Submit", region=(0, 0, 1920, 1080))
   ```

3. **Tesseract optimization**
   ```python
   # Configure Tesseract for speed/accuracy tradeoff
   pytesseract.image_to_string(
       image,
       config='--psm 7 --oem 1'  # PSM 7: single line, OEM 1: LSTM only
   )
   ```

4. **Preprocess images for better OCR**
   ```python
   # Convert to grayscale and increase contrast
   from PIL import ImageEnhance
   screenshot = screenshot.convert('L')  # Grayscale
   enhancer = ImageEnhance.Contrast(screenshot)
   screenshot = enhancer.enhance(2.0)  # Increase contrast
   ```

---

## Testing Plan

### Test Cases

1. **Fast Page Load**
   - Page loads in 1s
   - Verify tool returns in ~1s, not waiting full timeout

2. **Slow Page Load**
   - Page loads in 8s
   - Verify tool waits and finds element at 8s

3. **Element Never Appears**
   - Element doesn't exist
   - Verify timeout after specified duration
   - Verify helpful error message

4. **Multiple Elements Sequential**
   - Wait for element A, then B, then C
   - Verify each found before proceeding

5. **Theme/Scaling Variations**
   - Test with different themes
   - Test at different resolutions
   - Verify confidence parameter handles variations

---

## Migration from Fixed Waits

### Step-by-Step Process

**1. Identify Critical Wait Points**
```markdown
Review system prompts for all `wait(N)` calls
Categorize:
- Page loads (wait for initial elements)
- Action responses (wait for result of click/type)
- Form field readiness (wait for input to be ready)
```

**2. Define OCR Regions**
```markdown
For each wait point, identify:
- Which text indicates "ready state"
- Screen region where text appears (x, y, width, height)
- Alternative text variations

Example:
- Wait point: Login page loaded
- Text: "Username" or "Email"
- Region: (400, 70, 200, 40) [label above username field]
```

**3. Replace Fixed Waits**
```markdown
Before:
  wait(3)

After:
  wait_for_text("Username", region=(400, 70, 200, 40), timeout=10)
```

**4. Add Validation**
```markdown
After actions, verify expected result:
  click_mouse()
  wait_for_text("Menu", region=(800, 100, 200, 50), timeout=2)
```

**5. Document Regions in System Prompt**
```markdown
Create OCR region reference table
Include multiple text variations
Note dynamic content areas
```

**6. Test Thoroughly**
```markdown
Test on different network speeds
Test on different machines
Test with different themes/languages
Verify OCR accuracy in all regions
Verify faster response on fast connections
```

---

## Cost-Benefit Analysis

### OCR-Based Approach (Recommended) ⭐

**Setup Cost:** Low-Medium
- Install Tesseract OCR engine (one-time system setup)
- Add `pytesseract` dependency
- Define OCR regions in system prompt
- Test OCR accuracy on target UI

**Runtime Cost:** Medium
- OCR is CPU intensive (~0.5-1s per check with regions)
- Region-based scanning significantly faster than full-screen
- Poll interval: 1 second (reasonable for most use cases)

**Maintenance Cost:** Very Low
- ✅ No image files to maintain
- ✅ Text strings rarely change
- ✅ Works across UI updates (as long as text stays)
- ✅ No version control of visual assets

**Reliability Benefit:** Very High
- ✅ Works with dynamic content (user names, dates)
- ✅ Theme/style independent
- ✅ Resolution independent (regions auto-scale)
- ✅ Eliminates timing guesswork
- ✅ Self-validating workflows

**Recommended:** This is the superior approach for your use case.

---

### Image-Based Approach (Fallback)

**Setup Cost:** Medium-High
- Capture reference images for each element
- Version control image library
- Organize and maintain image files
- Handle resolution/theme variations

**Runtime Cost:** Low
- Fast image detection (< 0.1s per check)
- Minimal CPU overhead
- Scales well

**Maintenance Cost:** Medium-High
- Update images when UI changes
- Add new images for new workflows
- Test across resolutions and themes
- Git storage for image files

**Reliability Benefit:** Medium-High
- Good for icons, logos, non-text elements
- Sensitive to UI styling changes
- May need multiple reference images

**Use when:** OCR is unreliable (images as text, unusual fonts, icons)

---

## Recommendation Summary

### Immediate Implementation (Phase 1) ⭐

**Add to `realtimex-pyautogui-server`:**

**Core Tools:**
1. `wait_for_text(text, timeout, region, case_sensitive)` - Primary validation tool
2. `verify_text_visible(text, region, case_sensitive)` - Quick check

**Dependencies:**
```toml
dependencies = [
    "pyautogui>=0.9.54",
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0"
]
```

**System Setup:**
- Install Tesseract OCR engine on deployment machines
- Configure pytesseract path if needed

**Update system prompts:**
- Define OCR regions for each page/workflow
- Replace all fixed `wait()` calls with `wait_for_text()`
- Add text validation before/after actions
- Document expected text variations

**Example system prompt update:**
```markdown
OCR Validation Regions (Reference: 1920×1080):
| Page | Text | Region | Coordinates |
|------|------|--------|-------------|
| Login | "Username" | (400, 70, 200, 40) | Field: (500, 90) |
| Login | "Password" | (400, 140, 200, 40) | Field: (500, 160) |
```

### Future Enhancements (Phase 2+)

1. **Multiple text matching**
   - `wait_for_any_text(["Login", "Sign In"], region=...)`

2. **Image-based fallback**
   - `wait_for_element()` for icons/logos

3. **OCR preprocessing**
   - Automatic contrast enhancement
   - Grayscale conversion
   - Noise reduction

4. **Performance optimization**
   - Tesseract config tuning
   - OCR result caching
   - Parallel region scanning

---

**Document Version:** 1.0
**Author:** RTA
**Status:** Proposed - Ready for Review and Implementation
**Related Documents:**
- `COORDINATE_SCALING_IMPLEMENTATION.md` (coordinate handling)
- `SECURE_CREDENTIAL_TYPING_DESIGN.md` (credential workflows)