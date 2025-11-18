# 2025-11-12 세미나
# 이승수 학생 발표 내용

import os
import re
import numpy as np
import pydicom
from PIL import Image

# ====== 1. 경로 설정 ======
# 원본 DICOM 루트 (교수님 데이터)
ROOT_DIR = r"Z:\_LAB\11월\ANAM"

# PNG를 저장할 "최상위" 로컬 폴더
# 이 아래에 ANAM\환자코드\날짜\*.png 구조로 만들어짐
# 아래 OUTPUT_ROOT에 저장된 경로는 이승수 학생의 로컬 디렉터리이므로 본인에 맞게 수정
OUTPUT_ROOT = r"C:\Users\oopsla\Desktop1"

# 최종 구조 예:
# C:\Users\oopsla\Desktop\ANAM\00456343\20191103\00456343_20191103_MR_001.png

# ====== 2. T1 axial 시퀀스 이름 (SeriesDescription 기준) ======
# 교수님께서 주신 readme 마지막 부분에 있는 시퀀스 이름
T1_AXIAL_NAMES = [
    "t1_mprage_tra_p2_iso",
    "t1_tra tirm 3mm",
    "t1wi_3d_ax",
    "t1 ir tse fov 180",
    "3d t1 tfe ax",
]

# 문자열을 전부 소문자로 변환
# 양 끝 공백 제거
# 여러 개의 공백을 하나의 공백으로 변경
# -> 문자열을 정리하는 함수
def normalize_series_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    return name

NORMALIZED_T1_NAMES = {normalize_series_name(n) for n in T1_AXIAL_NAMES}

def is_t1_axial(series_desc: str) -> bool:
    """이 DICOM 시퀀스가 우리가 원하는 T1 axial인지 확인"""
    return normalize_series_name(series_desc) in NORMALIZED_T1_NAMES


def dicom_to_png(ds: pydicom.dataset.Dataset) -> Image.Image:
    """DICOM 픽셀 데이터를 0~255 범위의 8bit PNG 이미지로 변환"""
    arr = ds.pixel_array.astype(np.float32)

    arr -= arr.min()
    if arr.max() > 0:
        arr /= arr.max()
    arr *= 255.0

    return Image.fromarray(arr.astype(np.uint8))


def main():
    # 전체 DICOM 개수 / 실제로 PNG로 저장된 개수 카운트
    total_dicom = 0
    saved_png = 0

    # ROOT_DIR 아래를 재귀적으로 모두 탐색
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        for fname in filenames:
            # 파일 확장자가 .dcm이 아니면 스킵 (다른 이미지, 텍스트 파일 등 제외)
            if not fname.lower().endswith(".dcm"):
                continue

            dicom_path = os.path.join(dirpath, fname)
            total_dicom += 1

            # ROOT_DIR을 기준으로 한 상대 경로를 이용해서
            # [환자코드]\[날짜]\[모달리티]\... 구조를 해석한다.
            # 예) Z:\_LAB\11월\ANAM\00456343\20191103\MR\xxx.dcm
            # -> rel = "00456343\20191103\MR\xxx.dcm"
            rel = os.path.relpath(dicom_path, ROOT_DIR)
            parts = rel.split(os.sep)
            if len(parts) < 3:
                # 환자/날짜/MR 구조가 아닌 예외적인 폴더는 처리하지 않음
                continue

            patient_code = parts[0]    # 예: "00456343"
            date_folder = parts[1]     # 예: "20191103"
            modality_folder = parts[2] # 예: "MR" 또는 "US" 등

            # 이 스크립트에서는 MR(MRI)만 처리 대상
            if modality_folder.upper() != "MR":
                continue

            # 1) DICOM 파일 읽기
            try:
                ds = pydicom.dcmread(dicom_path, force=True)
            except Exception as e:
                print(f"[SKIP] DICOM 읽기 실패: {dicom_path} ({e})")
                continue

            # 2) 태그 상에서도 Modality가 MR인지 한 번 더 확인 (폴더 구조가 잘못되었을 경우 대비)
            if getattr(ds, "Modality", "").upper() != "MR":
                continue

            # 3) SeriesDescription으로 T1 axial 시퀀스인지 필터링
            series_desc = getattr(ds, "SeriesDescription", "")
            if not is_t1_axial(series_desc):
                # 우리가 지정한 5개 T1 axial 시퀀스가 아니면 스킵
                continue

            # 여기까지 왔다면 우리가 원하는 T1 axial MR 슬라이스 한 장

            # 4) 슬라이스 번호 (InstanceNumber)를 읽어와서 파일 이름에 사용
            instance_number = getattr(ds, "InstanceNumber", 0)
            try:
                instance_number = int(instance_number)
            except Exception:
                instance_number = 0  # 숫자로 변환 실패 시 0으로 처리

            # 5) 출력 폴더 경로 구성
            # OUTPUT_ROOT\ANAM\[환자코드]\[날짜]
            out_dir = os.path.join(
                OUTPUT_ROOT,
                "ANAM",
                patient_code,
                date_folder
            )
            os.makedirs(out_dir, exist_ok=True)

            # 6) 출력 파일 이름 패턴
            # [환자코드]_[날짜]_[모달리티]_[슬라이스번호3자리].png
            # 예: 00456343_20191103_MR_001.png
            out_fname = f"{patient_code}_{date_folder}_{modality_folder}_{instance_number:03d}.png"
            out_path = os.path.join(out_dir, out_fname)

            # 7) 실제 DICOM -> PNG 변환 및 저장
            try:
                img = dicom_to_png(ds)
                img.save(out_path)
                saved_png += 1
                print(f"[SAVE] {dicom_path} -> {out_path}")
            except Exception as e:
                print(f"[SKIP] PNG 저장 실패: {dicom_path} ({e})")
                continue

    # 처리 요약 출력
    print("\n===== 완료 =====")
    print(f"전체 DICOM 개수         : {total_dicom}")
    print(f"T1 axial PNG 저장 개수 : {saved_png}")
    print(f"출력 루트 폴더          : {OUTPUT_ROOT}\\ANAM")

if __name__ == "__main__":
    main()
