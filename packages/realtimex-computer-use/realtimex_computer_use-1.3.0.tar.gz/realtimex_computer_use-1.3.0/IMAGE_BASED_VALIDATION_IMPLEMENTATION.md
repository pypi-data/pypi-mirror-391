# Image-Based Element Validation Implementation

**Target Repository:** `realtimex-pyautogui-server`
**Implementation Scope:** Add `wait_for_element` tool for dynamic element validation using image matching
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

## Chosen Solution: Image-Based Element Detection

Implement a **`wait_for_element`** tool that uses PyAutoGUI's built-in image matching (`locateOnScreen`) to detect when specific UI elements appear on screen, enabling dynamic waiting that adapts to actual page load times.

### Why Image Matching?

**Advantages:**
- ✅ **Zero external dependencies**: Uses existing PyAutoGUI + Pillow (already installed)
- ✅ **No system requirements**: No Tesseract or additional software installation needed
- ✅ **User-friendly deployment**: Works out-of-the-box on user machines
- ✅ **Fast detection**: Image matching is faster than OCR (~0.1-0.5s per check)
- ✅ **Proven reliability**: PyAutoGUI's locateOnScreen is well-tested and stable
- ✅ **Returns element position**: Can click directly on found elements

**Trade-offs accepted:**
- ⚠️ Requires maintaining reference images (captured once, stored in version control)
- ⚠️ May need multiple images for different themes (light/dark mode)
- ⚠️ UI changes require updating reference images

**Why this beats OCR:**
- No external dependencies (critical for user deployment)
- Faster execution (important for responsiveness)
- Works perfectly for buttons, icons, logos, and labeled fields
- User tested and confirmed working

---

## Implementation Specification

### Tool: `wait_for_element`

**Purpose:** Wait for a visual element to appear on screen by matching a reference image.

**Function Signature:**

```python
@mcp.tool()
def wait_for_element(
    image_name: str = Field(
        description="Filename of the reference image in the elements directory (e.g., 'login_button.png', 'username_field.png')."
    ),
    timeout: float = Field(
        default=10.0,
        gt=0.0,
        le=30.0,
        description="Maximum seconds to wait for element to appear (0 < timeout ≤ 30).",
    ),
    confidence: float = Field(
        default=0.8,
        ge=0.5,
        le=1.0,
        description="Match confidence level (0.5-1.0). Lower values are more permissive. Default: 0.8",
    ),
    region: tuple[int, int, int, int] | None = Field(
        default=None,
        description="Screen region to search as (x, y, width, height) from reference screen (1920×1080). If None, searches full screen. Regions are automatically scaled to current screen resolution.",
    ),
) -> Dict[str, Any]:
    """
    Wait for a visual element to appear on screen using image matching.

    Polls at 0.5-second intervals until element is found or timeout is reached.
    Returns element position when found, enabling immediate clicking.

    Reference images must be stored in: ./elements/{image_name}

    Examples:
        # Wait for login button to appear
        wait_for_element("login_button.png", timeout=10, confidence=0.8)

        # Search in specific region (faster)
        wait_for_element("username_field.png", region=(200, 400, 400, 200), timeout=5)

        # Lower confidence for elements that change slightly
        wait_for_element("welcome_text.png", confidence=0.7, timeout=15)
    """
```

**Return Value:**

```python
# Success - element found before timeout
{
    "status": "success",
    "found": True,
    "message": "Element 'login_button.png' found on screen",
    "x": 525,  # Center X coordinate (already scaled to current screen)
    "y": 235,  # Center Y coordinate (already scaled to current screen)
    "elapsed_seconds": 2.3
}

# Failure - timeout reached
{
    "status": "error",
    "found": False,
    "message": "Element 'login_button.png' not found within 10.0s timeout",
    "elapsed_seconds": 10.0
}
```

---

## Implementation Details

### Algorithm

```python
import time
import pyautogui
from typing import Any, Dict

# Create elements directory if it doesn't exist
ELEMENTS_DIR = "./elements"

def wait_for_element(
    image_name: str,
    timeout: float = 10.0,
    confidence: float = 0.8,
    region: tuple[int, int, int, int] | None = None,
) -> Dict[str, Any]:
    import os

    start_time = time.time()
    poll_interval = 0.5  # 0.5 seconds between checks (fast)

    # Construct image path
    image_path = os.path.join(ELEMENTS_DIR, image_name)

    # Check if image exists
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "found": False,
            "message": f"Reference image not found: {image_path}",
            "elapsed_seconds": 0.0,
        }

    while True:
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed >= timeout:
            return {
                "status": "error",
                "found": False,
                "message": f"Element '{image_name}' not found within {timeout}s timeout",
                "elapsed_seconds": round(elapsed, 1),
            }

        try:
            # Scale region if provided
            search_region = None
            if region:
                search_region = _scale_region(*region)

            # Locate element on screen
            location = pyautogui.locateOnScreen(
                image_path,
                confidence=confidence,
                region=search_region
            )

            if location:
                # Get center coordinates
                center = pyautogui.center(location)

                return {
                    "status": "success",
                    "found": True,
                    "message": f"Element '{image_name}' found on screen",
                    "x": center.x,
                    "y": center.y,
                    "elapsed_seconds": round(elapsed, 1),
                }

        except pyautogui.ImageNotFoundException:
            # Element not found this iteration - continue polling
            pass
        except Exception as exc:
            # Other errors - continue polling (don't fail immediately)
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

**Dependencies:** None (PyAutoGUI already has locateOnScreen built-in)

**Tool registration:**

The `@mcp.tool()` decorator will automatically register the tool. Add the function after the existing tools (e.g., after `scroll()`).

**Elements directory:**

Create `./elements/` directory at runtime (or include in repository):

```python
import os

ELEMENTS_DIR = "./elements"

# Ensure elements directory exists
os.makedirs(ELEMENTS_DIR, exist_ok=True)
```

---

## Reference Image Management

### Directory Structure

```
realtimex-pyautogui-server/
├── elements/                    # Reference images directory
│   ├── fpt/                     # FPT portal images
│   │   ├── username_field.png
│   │   ├── password_field.png
│   │   ├── login_button.png
│   │   ├── contracts_menu.png
│   │   ├── invoices_link.png
│   │   └── paid_tab.png
│   └── evn/                     # EVN portal images
│       └── ...
└── server.py
```

### Image Capture Guidelines

**Best practices for reference images:**

1. **Capture tight regions** - Include just the element and small margin
   ```
   Good: 100×40px button capture
   Bad: 800×600px screenshot with button somewhere inside
   ```

2. **Consistent resolution** - Capture on reference screen (1920×1080)
   - PyAutoGUI scales automatically for other resolutions

3. **Single element per image** - One button, one field, one label
   ```
   Good: login_button.png (just the button)
   Bad: login_form.png (entire form)
   ```

4. **Stable elements** - Capture elements that don't change
   ```
   Good: Static button with fixed text
   Bad: Dynamic text showing username
   ```

5. **Naming convention** - Descriptive, lowercase, underscores
   ```
   Good: username_field.png, login_button.png
   Bad: img1.png, screenshot.png
   ```

### Capture Process

**Step-by-step:**

1. Navigate to target page in workflow
2. Take full screenshot: `screenshot()`
3. Open in image editor (Preview, Paint, etc.)
4. Crop to element of interest (include small margin)
5. Save as PNG with descriptive name
6. Place in `elements/{workflow}/` directory
7. Test with: `wait_for_element("element_name.png", confidence=0.8)`

**Example for FPT login button:**

```bash
# 1. Agent takes screenshot
screenshot()  # Returns full screen

# 2. User crops login button from screenshot
# - Button location: around (270, 655, 100, 40)
# - Crop to: slightly larger region for safety

# 3. Save as: elements/fpt/login_button.png

# 4. Test
wait_for_element("fpt/login_button.png", confidence=0.8)
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
result = wait_for_element("fpt/username_field.png", timeout=10, confidence=0.8)

if result["found"]:
    # Element found - can use returned coordinates
    move_mouse(260, 525)  # Or use result["x"], result["y"]
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
wait_for_element("fpt/username_field.png", timeout=10)

# Enter username
move_mouse(260, 525)
click_mouse()
type_credential_field(cred_id, "username")

# Click username submit button
move_mouse(320, 610)
click_mouse()

# Wait for password field to appear (multi-step login)
wait_for_element("fpt/password_field.png", timeout=5)

# Enter password
move_mouse(270, 550)
click_mouse()
type_credential_field(cred_id, "password")

# Click final login button
move_mouse(320, 670)
click_mouse()

# Wait for dashboard to load - check for contracts menu
wait_for_element("fpt/contracts_menu.png", timeout=15)
```

---

### Example 3: Using Returned Coordinates

```python
# Find and click button in one flow
result = wait_for_element("download_button.png", timeout=10)

if result["found"]:
    # Use returned coordinates to click
    move_mouse(result["x"], result["y"])
    click_mouse()
else:
    # Handle timeout
    screenshot()
    return {"error": "Download button not found"}
```

---

### Example 4: Region-Based Search (Performance)

```python
# Fast: Search only in expected region
wait_for_element(
    "fpt/login_button.png",
    region=(200, 600, 400, 150),  # Bottom-left area only
    timeout=5,
    confidence=0.8
)

# Slow: Search entire screen
wait_for_element(
    "fpt/login_button.png",
    timeout=5,
    confidence=0.8
)
```

---

## Performance Considerations

### Poll Interval Rationale

**Why 0.5 seconds?**
- Image matching is fast (~0.1-0.5s per check)
- More responsive than OCR (1.0s interval)
- Balances CPU usage with quick detection
- Acceptable for page loads and UI transitions

**Confidence levels:**
- `0.8` (default): Good balance - catches element with minor variations
- `0.7`: More permissive - use for elements that change slightly (hover states, fonts)
- `0.9`: Strict - use for critical elements that must match exactly
- `1.0`: Exact match - rarely needed, may fail on minor rendering differences

### Region-Based Search

**Always use regions when possible:**

```python
# Fast: Targeted search (0.1-0.2s per check)
wait_for_element("button.png", region=(400, 200, 400, 200))

# Slow: Full-screen search (0.3-0.5s per check)
wait_for_element("button.png")  # region=None
```

**Region estimation:**
- Use approximate coordinates from workflow docs
- Add generous margins (±50-100px) for safety
- Test and refine based on actual performance

---

## Testing Requirements

### Unit Tests

**Test cases to implement:**

1. **Fast detection** (element appears in <1s)
   - Verify tool returns in ~1s, not waiting full timeout
   - Confirms adaptive timing works

2. **Slow detection** (element appears in 5-8s)
   - Verify tool continues polling and finds element
   - Confirms patience for slow loads

3. **Timeout behavior** (element never appears)
   - Verify timeout after specified duration
   - Verify error message is helpful

4. **Confidence levels**
   - Test with 0.7, 0.8, 0.9 confidence
   - Verify lower confidence catches more variations

5. **Region vs. full screen**
   - Verify region-based search is faster
   - Verify regions scale correctly across resolutions

6. **Image not found**
   - Verify clear error when reference image missing
   - Suggest checking image path

7. **Coordinate scaling**
   - Test on different screen resolutions
   - Verify returned coordinates are scaled correctly

### Integration Tests

**Real-world scenario:**

```python
# Test FPT login page detection
def test_fpt_login_detection():
    open_browser("https://onmember.fpt.vn/login")
    result = wait_for_element("fpt/username_field.png", timeout=15, confidence=0.8)
    assert result["status"] == "success"
    assert result["found"] == True
    assert result["elapsed_seconds"] < 15
    assert "x" in result and "y" in result
```

---

## Error Handling

### Common Issues and Solutions

**1. Reference image not found**
```
"Reference image not found: ./elements/login_button.png"
```
**Solution:** Verify image exists in `./elements/` directory, check filename spelling.

**2. Element not detected (false negative)**
- Try lower confidence (0.7 instead of 0.8)
- Recapture reference image (may have changed)
- Check if element is partially obscured
- Verify image resolution matches reference screen

**3. False timeouts (element is visible but not found)**
- Element may have changed appearance (hover state, theme change)
- Capture new reference image
- Try lower confidence level
- Expand search region

**4. Slow performance**
- Use regions to limit search area
- Reduce image size (crop tighter)
- Check confidence level (higher = slower)

**5. Wrong coordinates returned**
- Verify screen resolution scaling is working
- Check if element moved on page
- Recapture reference image at reference resolution

---

## Maintenance Guidelines

### When to Update Reference Images

**Triggers for updates:**

1. **UI redesign** - Portal changes button styles, colors, layout
2. **Text changes** - Button labels change (e.g., "Login" → "Sign In")
3. **Theme support** - Need to support both light and dark modes
4. **Resolution changes** - Reference screen resolution changes

**Versioning strategy:**

```
elements/
├── fpt/
│   ├── v1/  # Original captures
│   │   ├── login_button.png
│   │   └── username_field.png
│   └── v2/  # Updated after UI redesign
│       ├── login_button.png
│       └── username_field.png
```

### Multi-Theme Support

**For sites with theme variations:**

```
elements/
├── fpt/
│   ├── light/
│   │   └── login_button.png
│   └── dark/
│       └── login_button.png
```

**Detection logic:**
```python
# Try light theme first
result = wait_for_element("fpt/light/login_button.png", timeout=3)

if not result["found"]:
    # Fallback to dark theme
    result = wait_for_element("fpt/dark/login_button.png", timeout=2)
```

---

## Migration from Fixed Waits

### Step-by-Step Process

**1. Identify Critical Wait Points**
```markdown
Review workflow for all `wait(N)` calls
Categorize:
- Page loads (wait for initial elements)
- Action responses (wait for result of click/type)
- Form field readiness (wait for input to be ready)
```

**2. Capture Reference Images**
```markdown
For each wait point:
1. Navigate to that step in workflow
2. Take screenshot
3. Crop element of interest
4. Save as elements/{workflow}/{element_name}.png
5. Test with wait_for_element()
```

**3. Replace Fixed Waits**
```markdown
Before:
  open_browser("...")
  wait(3)

After:
  open_browser("...")
  wait_for_element("workflow/page_ready_element.png", timeout=10)
```

**4. Add Validation After Actions**
```markdown
After clicking, verify expected result:
  click_mouse()
  wait_for_element("workflow/next_page_element.png", timeout=5)
```

**5. Update Workflow Documentation**
```markdown
Document reference images used:
- Image: fpt/username_field.png
- Purpose: Validates login page loaded
- Timeout: 10s
- Confidence: 0.8
```

**6. Test Thoroughly**
```markdown
Test on different network speeds
Test on different machines
Test on different resolutions
Verify faster response on fast connections
```

---

## Implementation Checklist

**Step 1: Core Implementation**
- [ ] Implement `wait_for_element()` with all parameters
- [ ] Implement `_scale_region()` helper (reuse pattern from `_scale_coordinates()`)
- [ ] Add `@mcp.tool()` decorator
- [ ] Create `./elements/` directory structure
- [ ] Return correct response format with coordinates

**Step 2: Reference Image Setup**
- [ ] Create `elements/` directory in repository
- [ ] Capture reference images for FPT workflow (6-8 images)
- [ ] Organize images by workflow: `elements/fpt/`, `elements/evn/`
- [ ] Document image naming conventions
- [ ] Test each image with `wait_for_element()`

**Step 3: Testing**
- [ ] Unit tests: fast detection, timeout, confidence levels
- [ ] Integration test: real FPT page load detection
- [ ] Test coordinate scaling on different resolutions
- [ ] Verify region-based search performance
- [ ] Test missing image error handling

**Step 4: Documentation**
- [ ] Add usage examples to tool docstring
- [ ] Document image capture process
- [ ] Document reference image organization
- [ ] Create maintenance guidelines for updating images

**Step 5: Validation**
- [ ] Code review for consistency with existing patterns
- [ ] Performance test: verify 0.5s poll interval
- [ ] Verify no breaking changes to existing tools
- [ ] Confirm tool appears in MCP tool list
- [ ] Test on user machine (no external dependencies required)

---

## Acceptance Criteria

**Definition of Done:**

- ✅ `wait_for_element` tool implemented with all parameters (image_name, timeout, confidence, region)
- ✅ Region coordinate scaling works correctly (follows existing `_scale_coordinates` pattern)
- ✅ Tool registered with FastMCP and appears in tool list
- ✅ Returns correct status format with element coordinates
- ✅ Poll interval is 0.5 seconds (not faster)
- ✅ No external dependencies added (uses existing PyAutoGUI + Pillow)
- ✅ Elements directory structure created
- ✅ Reference images captured for FPT workflow
- ✅ Unit tests cover success, timeout, and confidence levels
- ✅ Integration test validates real page load detection
- ✅ Code follows existing patterns (same style as `wait()`, `move_mouse()`, etc.)
- ✅ No breaking changes to existing tools
- ✅ Works on user machines without additional software installation

---

## Questions for Implementer

If you encounter any of these scenarios, please escalate:

1. **Image storage**: Should images be in repository or loaded dynamically from external storage?
2. **Confidence tuning**: Should we provide automatic confidence adjustment on failures?
3. **Poll interval**: Is 0.5 seconds optimal, or should we make it configurable?
4. **Multi-theme**: Should we implement automatic fallback between light/dark themes?
5. **Coordinate usage**: Should we add a parameter to auto-click found element?

---

## Document Metadata

- **Version:** 1.0
- **Author:** RTA (realtimex-computer-use team)
- **Date:** 2025-11-12
- **Target Repository:** realtimex-pyautogui-server
- **Related Documents:**
  - `DYNAMIC_ELEMENT_VALIDATION_DESIGN.md` (upstream design exploration)
  - `OCR_TEXT_VALIDATION_IMPLEMENTATION.md` (alternative approach - not chosen)
  - `COORDINATE_SCALING_IMPLEMENTATION.md` (coordinate system reference)
- **Status:** Ready for Implementation
