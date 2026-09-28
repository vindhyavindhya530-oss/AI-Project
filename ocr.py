import cv2
import pytesseract
import shutil
import os


# --------------------------------------------------
# TESSERACT PATH
# --------------------------------------------------

tesseract_path = shutil.which("tesseract")

if tesseract_path:

    pytesseract.pytesseract.tesseract_cmd = (
        tesseract_path
    )

elif os.path.exists(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
):

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
# --------------------------------------------------
# GET OCR CONFIDENCE
# --------------------------------------------------

def get_confidence(data):

    values = []

    for conf in data["conf"]:

        try:

            value = float(conf)

            if value >= 0:
                values.append(value)

        except:
            pass

    if values:
        return sum(values) / len(values)

    return 0


# --------------------------------------------------
# RUN OCR
# --------------------------------------------------

def run_ocr(image, config):

    text = pytesseract.image_to_string(
        image,
        config=config
    )

    data = pytesseract.image_to_data(
        image,
        config=config,
        output_type=pytesseract.Output.DICT
    )

    confidence = get_confidence(data)

    return text, confidence


# --------------------------------------------------
# PREPROCESS IMAGE
# --------------------------------------------------

def preprocess(image):

    # Resize image
    image = cv2.resize(
        image,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # Grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # OTSU threshold
    otsu = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return image, gray, otsu, adaptive


# --------------------------------------------------
# MAIN OCR FUNCTION
# --------------------------------------------------

def extract_text(image_path):

    original = cv2.imread(image_path)

    if original is None:
        raise ValueError(
            "Unable to read receipt image."
        )

    image, gray, otsu, adaptive = preprocess(
        original
    )

    # Different image versions
    images = [
        image,
        gray,
        otsu,
        adaptive
    ]

    # Different Tesseract layouts
    configs = [
        "--psm 6",
        "--psm 11",
        "--psm 12"
    ]

    all_results = []

    best_text = ""
    best_confidence = 0

    # --------------------------------------------------
    # TRY MULTIPLE OCR COMBINATIONS
    # --------------------------------------------------

    for img in images:

        for config in configs:

            text, confidence = run_ocr(
                img,
                config
            )

            if text.strip():

                all_results.append(
                    text.strip()
                )

            # Keep highest confidence result
            if confidence > best_confidence:

                best_confidence = confidence

                best_text = text


    # --------------------------------------------------
    # REMOVE DUPLICATE OCR RESULTS
    # --------------------------------------------------

    unique_results = []

    for result in all_results:

        if result not in unique_results:

            unique_results.append(result)


    # --------------------------------------------------
    # COMBINE RESULTS
    # --------------------------------------------------

    combined_text = "\n\n".join(
        unique_results
    )


    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    if not combined_text.strip():

        combined_text = best_text


    return combined_text, best_confidence