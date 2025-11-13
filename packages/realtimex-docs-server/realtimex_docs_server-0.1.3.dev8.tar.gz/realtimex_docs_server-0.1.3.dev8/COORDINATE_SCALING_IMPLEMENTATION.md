# Coordinate Scaling Implementation Plan

## Objective

Modify `realtimex-pyautogui-server` to automatically scale coordinates based on screen resolution, eliminating the need for agents to manually call `calculate_screen_coordinates`.

## Current vs. Proposed Approach

### Current (Complex)
```python
# Agent workflow
coords = calculate_screen_coordinates(0.260, 0.083)  # Tool call 1
move_mouse(coords["x"], coords["y"])                 # Tool call 2
```

### Proposed (Simple)
```python
# Agent workflow
move_mouse(500, 90)  # Single tool call - scaling happens automatically
```

**Key Change:** `move_mouse` internally scales coordinates based on reference resolution.

---

## Implementation Details

### Location
**Repository:** `realtimex-pyautogui-server`
**File:** `src/realtimex_pyautogui_server/server.py` (or new helper module)

### Changes Required

#### 1. Add Internal Scaling Function

```python
def _scale_coordinates(
    x: int,
    y: int,
    reference_width: int = 1920,
    reference_height: int = 1080
) -> tuple[int, int]:
    """
    Scale coordinates from reference resolution to current screen resolution.

    Args:
        x: X coordinate from reference screen
        y: Y coordinate from reference screen
        reference_width: Width of reference screen (default: 1920)
        reference_height: Height of reference screen (default: 1080)

    Returns:
        Tuple of (scaled_x, scaled_y) for current screen
    """
    current_screen = pyautogui.size()

    scale_x = current_screen.width / reference_width
    scale_y = current_screen.height / reference_height

    scaled_x = int(x * scale_x)
    scaled_y = int(y * scale_y)

    return (scaled_x, scaled_y)
```

#### 2. Modify `move_mouse` Tool

**Before:**
```python
@mcp.tool()
def move_mouse(
    x: int = Field(description="The x-coordinate on the screen to move the mouse to."),
    y: int = Field(description="The y-coordinate on the screen to move the mouse to."),
) -> Dict[str, str]:
    """Move the mouse to the given coordinates."""
    try:
        pyautogui.moveTo(x, y)
        return _success(f"Mouse moved to coordinates ({x}, {y}).")
    except pyautogui.FailSafeException:
        return _failure("Operation cancelled - mouse moved to screen corner (failsafe).")
    except Exception as exc:
        return _failure(f"Failed to move mouse: {exc}")
```

**After:**
```python
@mcp.tool()
def move_mouse(
    x: int = Field(description="The x-coordinate from reference screen (1920×1080 by default)."),
    y: int = Field(description="The y-coordinate from reference screen (1920×1080 by default)."),
) -> Dict[str, str]:
    """Move the mouse to the given coordinates, automatically scaling for current screen resolution."""
    try:
        # Get reference resolution from environment or use defaults
        ref_width = int(os.getenv("REFERENCE_SCREEN_WIDTH", "1920"))
        ref_height = int(os.getenv("REFERENCE_SCREEN_HEIGHT", "1080"))

        # Scale coordinates to current screen
        scaled_x, scaled_y = _scale_coordinates(x, y, ref_width, ref_height)

        # Move to scaled position
        pyautogui.moveTo(scaled_x, scaled_y)

        return _success(f"Mouse moved to coordinates ({x}, {y}) [scaled to ({scaled_x}, {scaled_y})].")
    except pyautogui.FailSafeException:
        return _failure("Operation cancelled - mouse moved to screen corner (failsafe).")
    except Exception as exc:
        return _failure(f"Failed to move mouse: {exc}")
```

#### 3. Modify `drag_mouse` Tool (Similar Changes)

```python
@mcp.tool()
def drag_mouse(
    x: int = Field(description="The x-coordinate to drag to (from reference screen)."),
    y: int = Field(description="The y-coordinate to drag to (from reference screen)."),
    duration: float = Field(default=0.5, ge=0.0, le=10.0, description="Duration of the drag in seconds."),
) -> Dict[str, str]:
    """Drag the mouse to a target location, automatically scaling for current screen resolution."""
    try:
        ref_width = int(os.getenv("REFERENCE_SCREEN_WIDTH", "1920"))
        ref_height = int(os.getenv("REFERENCE_SCREEN_HEIGHT", "1080"))

        scaled_x, scaled_y = _scale_coordinates(x, y, ref_width, ref_height)

        pyautogui.dragTo(scaled_x, scaled_y, duration=duration)
        return _success(f"Mouse dragged to ({x}, {y}) [scaled to ({scaled_x}, {scaled_y})] over {duration} seconds.")
    except pyautogui.FailSafeException:
        return _failure("Operation cancelled - mouse in screen corner (failsafe).")
    except Exception as exc:
        return _failure(f"Failed to drag mouse: {exc}")
```

---

## Configuration

### Environment Variables

Add to server configuration or Docker/systemd environment:

```bash
# Reference screen resolution (coordinates in system prompt are based on this)
REFERENCE_SCREEN_WIDTH=1920
REFERENCE_SCREEN_HEIGHT=1080
```

### Default Behavior

- **Default reference:** 1920×1080 (most common development resolution)
- **Auto-scaling:** Always enabled
- **Transparency:** Success messages show both original and scaled coordinates for debugging

---

## System Prompt Updates

### Before (Complex)
```markdown
| Element | Normalized Coords | Ref Screen | Description |
|---------|------------------|------------|-------------|
| address_bar | (0.260, 0.083) | 1920×1080 | Browser address bar |

**Usage:**
1. coords = calculate_screen_coordinates(0.260, 0.083)
2. move_mouse(coords["x"], coords["y"])
```

### After (Simple)
```markdown
Reference Screen: 1920×1080

| Element | Coordinates | Description |
|---------|------------|-------------|
| address_bar | (500, 90) | Browser address bar |
| search_button | (960, 540) | Center search button |
| settings_icon | (1824, 54) | Top-right settings |

**Usage:**
- move_mouse(500, 90)  # Coordinates auto-scale to your screen
```

**Instructions for agents:**
```markdown
All coordinates in this document are based on a 1920×1080 reference screen.
The move_mouse tool automatically scales these coordinates to your actual screen resolution.
Simply use the coordinates as documented - no calculation needed.
```

---

## Testing Plan

### Test Cases

1. **Same Resolution (1920×1080)**
   - Input: `move_mouse(500, 90)`
   - Expected: Mouse at (500, 90)
   - Scaling: 1:1

2. **Higher Resolution (2560×1440)**
   - Input: `move_mouse(500, 90)`
   - Expected: Mouse at (666, 120)
   - Scaling: 1.33x both axes

3. **Lower Resolution (1366×768)**
   - Input: `move_mouse(500, 90)`
   - Expected: Mouse at (355, 64)
   - Scaling: ~0.71x both axes

4. **Custom Reference (via env vars)**
   - Set: `REFERENCE_SCREEN_WIDTH=2560`, `REFERENCE_SCREEN_HEIGHT=1440`
   - Input: `move_mouse(1280, 720)`
   - On 1920×1080: Expected (960, 540)
   - Scaling: 0.75x both axes

5. **Drag Mouse**
   - Same scaling logic applies
   - Verify smooth dragging to scaled coordinates

---

## Migration Path

### Phase 1: Implementation
1. Add `_scale_coordinates()` helper function
2. Modify `move_mouse()` tool
3. Modify `drag_mouse()` tool
4. Add environment variable support
5. Update tool descriptions

### Phase 2: Documentation
1. Update README with new behavior
2. Document environment variables
3. Update system prompt templates
4. Add scaling examples

### Phase 3: Testing
1. Test on reference resolution (1920×1080)
2. Test on common resolutions (2560×1440, 1366×768)
3. Test with custom reference resolution
4. Verify success messages include scaled coordinates

### Phase 4: Rollout
1. Update `realtimex-pyautogui-server` package
2. Update system prompts to use absolute coordinates
3. Remove `calculate_screen_coordinates` from `realtimex-computer-use` (no longer needed)
4. Update agent documentation

---

## Benefits Summary

✅ **Simpler agent workflows** - One tool call instead of two
✅ **Lower token costs** - No extra tool call overhead
✅ **Less error-prone** - No chance of forgetting to scale
✅ **Easier documentation** - Absolute coordinates are more intuitive
✅ **Better maintainability** - Scaling logic where it belongs
✅ **Transparent debugging** - Success messages show both coordinates
✅ **Flexible configuration** - Environment variables for custom references

---

## Risks & Mitigations

### Risk: Breaking Existing Workflows
**Mitigation:** This is a new server (`realtimex-pyautogui-server`), not modifying existing production code.

### Risk: Incorrect Scaling on Non-Standard Displays
**Mitigation:**
- Environment variables allow custom reference resolution
- Success messages show scaled coordinates for verification
- Test on multiple common resolutions

### Risk: Browser Chrome Doesn't Scale Linearly
**Mitigation:**
- Document that browser UI elements may need testing/adjustment
- Future enhancement: Window-relative coordinates mode
- Suggest testing coordinates on target resolutions

---

## Alternative Considered: Keep Both Approaches

**Option:** Provide both `move_mouse` (auto-scaling) and `move_mouse_absolute` (no scaling)

**Decision:** Not recommended
- Adds complexity
- Agents might use wrong tool
- Two ways to do the same thing
- Auto-scaling should work for 99% of cases

---

## Future Enhancements

**Phase 2: Window-Relative Mode**
```python
move_mouse(x, y, relative_to="active_window")
```
Calculate coordinates relative to active window instead of screen.

**Phase 3: Multi-Monitor Support**
```python
move_mouse(x, y, monitor=1)
```
Support coordinate scaling across multiple monitors.

**Phase 4: Coordinate Validation**
```python
validate_coordinates(x, y)  # Tool to check if coordinates are on-screen
```

---

## Implementation Checklist

### Code Changes (realtimex-pyautogui-server)
- [ ] Add `_scale_coordinates()` helper function
- [ ] Modify `move_mouse()` to use scaling
- [ ] Modify `drag_mouse()` to use scaling
- [ ] Add environment variable support (REFERENCE_SCREEN_WIDTH/HEIGHT)
- [ ] Update tool descriptions
- [ ] Add scaled coordinates to success messages

### Documentation
- [ ] Update README with scaling behavior
- [ ] Document environment variables
- [ ] Add usage examples
- [ ] Create migration guide

### Testing
- [ ] Test on 1920×1080 (reference)
- [ ] Test on 2560×1440 (higher res)
- [ ] Test on 1366×768 (lower res)
- [ ] Test with custom reference resolution
- [ ] Verify drag_mouse scaling

### Cleanup
- [ ] Remove `calculate_screen_coordinates` from realtimex-computer-use (optional)
- [ ] Update COORDINATE_SCALING_DESIGN.md to reflect new approach
- [ ] Update system prompt templates

---

**Document Version:** 1.0
**Author:** RTA
**Status:** Proposed - Ready for Review and Implementation
**Delegation Target:** `realtimex-pyautogui-server` repository