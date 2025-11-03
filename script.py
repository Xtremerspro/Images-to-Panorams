import importlib
import subprocess
import sys


# --- Auto-install helper ---
def ensure_package(package, import_name=None):
    """Import the package, installing it via pip if not present."""
    import_name = import_name or package
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"📦 Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(import_name)


# --- Ensure dependencies ---
cv2 = ensure_package("opencv-python", "cv2")
np = ensure_package("numpy")
py360convert = ensure_package("py360convert")
argparse = ensure_package("argparse")


# --- Core logic ---
def center_crop_square(img):
    h, w = img.shape[:2]
    s = min(h, w)
    y0 = (h - s) // 2
    x0 = (w - s) // 2
    return img[y0 : y0 + s, x0 : x0 + s]


def main():
    parser = argparse.ArgumentParser(
        description="Convert cubemap faces to equirectangular panorama."
    )
    parser.add_argument(
        "--face", type=int, default=1024, help="Face resolution (e.g. 512, 1024, 2048)"
    )
    args = parser.parse_args()

    # Load and crop cube faces
    R = center_crop_square(cv2.imread("posx.png"))  # +X → Right
    L = center_crop_square(cv2.imread("negx.png"))  # -X → Left
    U = center_crop_square(cv2.imread("posy.png"))  # +Y → Up
    D = center_crop_square(cv2.imread("negy.png"))  # -Y → Down
    F = center_crop_square(cv2.imread("posz.png"))  # +Z → Front
    B = center_crop_square(cv2.imread("negz.png"))  # -Z → Back

    # Resize faces to target resolution
    faces = [cv2.resize(x, (args.face, args.face)) for x in [F, R, B, L, U, D]]

    # Convert to equirectangular
    equirect = py360convert.c2e(faces, h=args.face, w=args.face * 2, cube_format="list")

    cv2.imwrite("panorama.png", equirect)
    print("✅ Saved as panorama.png")


if __name__ == "__main__":
    main()
