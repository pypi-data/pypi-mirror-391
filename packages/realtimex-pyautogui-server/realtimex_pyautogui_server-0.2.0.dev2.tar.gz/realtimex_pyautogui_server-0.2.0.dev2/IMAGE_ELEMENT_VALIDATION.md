# Image-Based Element Validation

**Target:** `realtimex-pyautogui-server`
**Goal:** Replace fixed waits with dynamic element detection using image matching

---

## Problem

Fixed waits are unreliable:

```python
open_browser("https://example.com")
wait(3)  # Hope page loaded
move_mouse(500, 90)
click_mouse()
```

**Issues:**
- Slow networks: page takes >3s → automation fails
- Fast networks: page loads in 1s → wastes 2s
- No validation element actually appeared

**Solution:** Wait for visible elements, not fixed time.

---

## Implementation

### Tool: `wait_for_element`

Wait for a visual element to appear by matching a reference image.

**Signature:**
```python
def wait_for_element(
    image_name: str,        # "login_button.png"
    timeout: float = 10.0,  # Max seconds to wait
    confidence: float = 0.8 # Match accuracy (0.5-1.0)
) -> Dict[str, Any]
```

**Usage:**
```python
# Wait for login button before clicking
result = wait_for_element("fpt/login_button.png", timeout=10)

if result["found"]:
    move_mouse(320, 670)
    click_mouse()
```

**Returns:**
```python
# Success
{
    "status": "success",
    "found": True,
    "x": 525,
    "y": 235,
    "elapsed_seconds": 2.1
}

# Timeout
{
    "status": "error",
    "found": False,
    "elapsed_seconds": 10.0
}
```

---

### Code

Add to `server.py`:

```python
import os
import time
from typing import Any, Dict

ELEMENTS_DIR = "./elements"

@mcp.tool()
def wait_for_element(
    image_name: str = Field(
        description="Reference image filename (e.g., 'fpt/login_button.png')"
    ),
    timeout: float = Field(
        default=10.0,
        gt=0.0,
        le=30.0,
        description="Maximum seconds to wait (0 < timeout ≤ 30)",
    ),
    confidence: float = Field(
        default=0.8,
        ge=0.5,
        le=1.0,
        description="Match confidence (0.5-1.0). Lower = more permissive. Default: 0.8",
    ),
) -> Dict[str, Any]:
    """Wait for visual element to appear using image matching."""
    start_time = time.time()
    poll_interval = 0.5
    image_path = os.path.join(ELEMENTS_DIR, image_name)

    if not os.path.exists(image_path):
        return {
            "status": "error",
            "found": False,
            "message": f"Image not found: {image_path}",
            "elapsed_seconds": 0.0,
        }

    while True:
        elapsed = time.time() - start_time

        if elapsed >= timeout:
            return {
                "status": "error",
                "found": False,
                "message": f"Element '{image_name}' not found within {timeout}s",
                "elapsed_seconds": round(elapsed, 1),
            }

        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return {
                    "status": "success",
                    "found": True,
                    "x": center.x,
                    "y": center.y,
                    "message": f"Element '{image_name}' found",
                    "elapsed_seconds": round(elapsed, 1),
                }
        except pyautogui.ImageNotFoundException:
            pass
        except Exception:
            pass

        time.sleep(min(poll_interval, timeout - elapsed))
```

---

## Reference Images

### Folder Structure

```
realtimex-pyautogui-server/
└── elements/
    ├── fpt/
    │   ├── username_field.png
    │   ├── password_field.png
    │   ├── login_button.png
    │   ├── contracts_menu.png
    │   ├── invoices_link.png
    │   └── paid_tab.png
    └── evn/
        └── ...
```

### Capture Process

1. Navigate to target page
2. Take screenshot: `screenshot()`
3. Crop element (include small margin)
4. Save as: `elements/{workflow}/{element}.png`
5. Test: `wait_for_element("workflow/element.png")`

**Naming:**
- Use workflow prefix: `fpt/`, `evn/`
- Descriptive names: `login_button.png`, not `img1.png`
- Lowercase with underscores

---

## Usage Examples

### Before (unreliable)

```python
open_browser("https://onmember.fpt.vn/login")
wait(3)
move_mouse(260, 525)
click_mouse()
```

### After (reliable)

```python
open_browser("https://onmember.fpt.vn/login")
wait_for_element("fpt/username_field.png", timeout=10)
move_mouse(260, 525)
click_mouse()
```

**Benefits:**
- Fast networks: returns in ~1s
- Slow networks: waits up to 10s
- Validates page actually loaded

---

### Multi-Step Flow

```python
# Login page loads
open_browser("https://onmember.fpt.vn/login")
wait_for_element("fpt/username_field.png", timeout=10)

# Enter username
move_mouse(260, 525)
click_mouse()
type_credential_field(cred_id, "username")

# Submit username
move_mouse(320, 610)
click_mouse()

# Wait for password field
wait_for_element("fpt/password_field.png", timeout=5)

# Enter password
move_mouse(270, 550)
click_mouse()
type_credential_field(cred_id, "password")

# Submit login
move_mouse(320, 670)
click_mouse()

# Wait for dashboard
wait_for_element("fpt/contracts_menu.png", timeout=15)
```

---

## Confidence Levels

- `0.8` (default): Good balance, handles minor variations
- `0.7`: More permissive, use if element changes slightly
- `0.9`: Strict, use for critical elements
- `1.0`: Exact match (rarely needed)

**Example:**
```python
# Strict matching for critical button
wait_for_element("fpt/login_button.png", confidence=0.9)

# Permissive for text that may vary
wait_for_element("fpt/welcome_text.png", confidence=0.7)
```

---

## Error Handling

**Image not found:**
```
"Image not found: ./elements/fpt/button.png"
```
→ Check filename and path

**Timeout:**
```
"Element 'fpt/login_button.png' not found within 10.0s"
```
→ Check confidence level, recapture image, or increase timeout

---

## Checklist

- [ ] Add `wait_for_element()` to `server.py`
- [ ] Register with `@mcp.tool()` decorator
- [ ] Create `elements/` directory structure
- [ ] Capture reference images for FPT workflow
- [ ] Test each image: `wait_for_element("workflow/image.png")`
- [ ] Update workflow docs to use `wait_for_element` instead of `wait(N)`
