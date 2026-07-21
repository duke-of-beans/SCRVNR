"""Log the cartoon correction pair with the correct API signature."""
import sys
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.correction_capture import CorrectionCapture

cc = CorrectionCapture()
result = cc.capture(
    original="There's an old cartoon - two men in a rowboat, water gushing through a hole in one end, and the man in the dry end, arms folded, perfectly serene, saying: \"Glad the hole isn't in our end.\"",
    corrected="There's an old cartoon - a rowboat, water gushing through a hole in one end, and two men in the dry end, arms folded, perfectly serene: \"Glad the hole isn't in our end.\"",
    register="ARGUMENTATIVE",
    source="session",
)
print(f"Correction pair logged: {result}")
