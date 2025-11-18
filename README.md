# SCH Medical AI Lab – DICOM T1 Axial Conversion Project  
### SCH AI LAB Seminar

---

## 📌 Seminar Information
- **Date:** November 12, 2025  
- **Location:** Soonchunhyang University, Multimedia Building 6F, Room 610

---

## 👥 Participants
- 조용원 교수님
- 이승수
- 강민재
- 김대현
- 하두호
- 김강현
- 심수빈
- 한혜원
- 홍유택
- 변경호

---

# 📘 Project Overview

This repository provides an automated Python pipeline for converting **T1 axial MRI DICOM files** into **normalized 8-bit PNG images**.  
The script was developed for a lab seminar demonstration and is intended to support medical AI research workflows such as segmentation, preprocessing, and dataset preparation.

The system scans the entire dataset, selects only T1 axial sequences based on metadata, normalizes pixel intensities, and exports them in a structured format for reproducible research.

---

# 🎯 Purpose of the Project

MRI studies often contain multiple sequences, and manually identifying the correct T1 axial series is both slow and error-prone.  
This tool:

- Automates extraction of **only T1 axial MRI sequences**
- Standardizes preprocessing across different datasets
- Produces clean 8-bit PNGs ready for machine learning pipelines
- Ensures reproducibility inside the lab and improves team collaboration

---

# ⚙ Features

- Full recursive scan of a DICOM dataset directory
- Folder-path parsing for:
  - Patient ID  
  - Scan date  
  - Modality (MR/CT/US, etc.)
- Metadata-based filtering:
  - `Modality == "MR"`
  - `SeriesDescription` matches predefined T1 axial names
- Image processing:
  - Pixel values normalized to **0–255**
  - Export as **8-bit grayscale PNG**
- Output directory automatically generated:
OUTPUT_ROOT/
 └── ANAM/
      └── [patient]/
           └── [date]/
                ├── patient_date_MR_001.png
                ├── patient_date_MR_002.png
                └── ...

---

# 🧠 How It Works (Pipeline Summary)

1. Recursively scans the entire dataset directory  
2. Finds all `.dcm` files  
3. Reads each DICOM file using **pydicom**  
4. Extracts metadata:  
   - `Modality`  
   - `SeriesDescription`  
   - `InstanceNumber`  
5. Normalizes `SeriesDescription` (lowercase, spacing fixed)  
6. Confirms whether the description matches the **T1 axial** list  
7. Normalizes pixel values:
   - Shift min to 0  
   - Divide by max  
   - Scale to 255  
8. Converts to 8-bit grayscale PNG  
9. Saves using format: `[patient]_[date]_[modality]_[slice:03d].png`

---

# 🔧 Configuration

Modify the two main paths in the script:

```python
ROOT_DIR = r"Z:\_LAB\11월\ANAM"          # Input DICOM directory
OUTPUT_ROOT = r"C:\Users\...\Desktop1"   # Output PNG folder
```
Add or adjust MRI sequence names here if needed:
```python
T1_AXIAL_NAMES = [
    "t1_mprage_tra_p2_iso",
    "t1_tra tirm 3mm",
    "t1wi_3d_ax",
    "t1 ir tse fov 180",
    "3d t1 tfe ax",
]
```

---

# 📦 Installation
Install required Python packages:
```bash
pip install pydicom pillow numpy
```

# 📝 Notes

Filtering is based on exact SeriesDescription matches.
MRI scanners with different naming conventions may require updating T1_AXIAL_NAMES.

Pixel normalization ensures uniform image intensity across slices.

PNG images are anonymized and suitable for:

Deep learning

QC/QA

Dataset preprocessing

Visualization

Ensure compliance with medical data handling policies.
