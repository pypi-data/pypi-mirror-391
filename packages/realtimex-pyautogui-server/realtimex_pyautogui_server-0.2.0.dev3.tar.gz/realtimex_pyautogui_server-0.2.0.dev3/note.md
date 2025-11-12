Previously, I encountered an issue when typing on macOS devices. When executing `type_text` with an input like `"https://example.com"`, the actual typed value appeared as `"https:??EXAMPLE>COM"` due to the "Shift" key getting stuck. After applying a fix with platform-specific typing, the text now types correctly.  

I have a few questions about the current implementation:  
1. Should I remove the potentially redundant `_release_modifiers()` calls in the `hotkey`, `press_key`, and `type_text` functions to improve efficiency, or is it better to keep them for safety?  
2. In the current implementation, I’m using AppleScript. Is there an alternative method that types correctly without relying on AppleScript? Using it requires explicit system permissions, which might make our application appear untrusted to some users when the OS asks for approval while running. You can check the implementation in the `pyautogui` folder (copied from the PyAutoGUI package) to explore potential alternatives. If no better solution exists, we can retain the current approach — I just want to ensure we’ve evaluated all viable options.


feat: Add wait_for_element tool for image-based validation
 
Implements the `wait_for_element` tool, which polls the screen for a visual element by matching a reference image. This provides a  reliable alternative to fixed-time waits, improving automation robustness against varying load times.
 
Key changes:
- Adds the `wait_for_element` tool to `server.py`.
- Introduces `opencv-python` dependency for image recognition.
- Adds reference images for the FPT workflow under `elements/fpt/`.
- Bumps project version to 0.2.0.dev2.
 
This change is based on the design specified in `IMAGE_ELEMENT_VALIDATION.md`.