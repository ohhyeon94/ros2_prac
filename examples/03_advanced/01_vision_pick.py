"""
[고급 예제 1] 비전 기반 픽앤플레이스
---------------------------------------
목표: 카메라로 물체 위치를 인식하여 자동으로 픽앤플레이스 수행

학습 포인트:
- Eye-to-Hand 카메라 캘리브레이션 개념
- 픽셀 좌표 → 로봇 좌표 변환
- OpenCV 기반 간단한 물체 감지
- 비전 + 로봇 통합 자동화 파이프라인
"""

import time
import math
import numpy as np

# 카메라/비전 설정
CAMERA_WIDTH   = 1280
CAMERA_HEIGHT  = 720
ROBOT_IP       = "192.168.0.1"

# Eye-to-Hand 캘리브레이션 파라미터 (실제 캘리브레이션으로 구해야 함)
# 카메라 픽셀 → 로봇 월드 좌표 변환 행렬 (예시값)
CAM_TO_ROBOT_SCALE_X = 0.5    # mm/pixel
CAM_TO_ROBOT_SCALE_Y = 0.5    # mm/pixel
CAM_TO_ROBOT_OFFSET_X = 200.0  # mm
CAM_TO_ROBOT_OFFSET_Y = -150.0  # mm
WORK_HEIGHT_Z = 200.0          # mm (작업 테이블 높이)
APPROACH_HEIGHT_Z = 350.0      # mm (접근 높이)

BASE_ORIENTATION = [0.0, 180.0, 0.0]  # [Rx, Ry, Rz]


# ── 카메라/비전 시뮬레이션 ────────────────────────────────────────────────────

class MockCamera:
    """실제 카메라 대신 시뮬레이션하는 클래스."""

    def capture(self) -> np.ndarray:
        """프레임 캡처 (시뮬레이션)."""
        frame = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
        return frame

    def release(self):
        pass


def detect_objects_mock() -> list:
    """
    물체 감지 시뮬레이션.
    실제 구현: OpenCV, YOLO, 등 사용

    Returns:
        list of {'cx': int, 'cy': int, 'angle': float, 'label': str}
    """
    # 3개의 임의 물체 반환 (시뮬레이션)
    objects = [
        {"cx": 320, "cy": 240, "angle": 15.0,  "label": "부품A"},
        {"cx": 640, "cy": 360, "angle": -30.0, "label": "부품B"},
        {"cx": 960, "cy": 480, "angle": 45.0,  "label": "부품A"},
    ]
    print(f"  [비전] {len(objects)}개 물체 감지")
    for obj in objects:
        print(f"    - {obj['label']}: 픽셀({obj['cx']}, {obj['cy']}), 각도={obj['angle']}°")
    return objects


# ── 좌표 변환 ─────────────────────────────────────────────────────────────────

def pixel_to_robot(cx: int, cy: int) -> tuple:
    """
    카메라 픽셀 좌표를 로봇 월드 좌표(mm)로 변환.

    단순 선형 변환 사용 (실제 캘리브레이션은 homography 행렬 사용 권장).

    Args:
        cx, cy: 픽셀 좌표 (이미지 중심 기준)

    Returns:
        (robot_x, robot_y) in mm
    """
    # 이미지 중심 기준으로 오프셋 계산
    offset_x = cx - CAMERA_WIDTH / 2
    offset_y = cy - CAMERA_HEIGHT / 2

    robot_x = CAM_TO_ROBOT_OFFSET_X + offset_x * CAM_TO_ROBOT_SCALE_X
    robot_y = CAM_TO_ROBOT_OFFSET_Y + offset_y * CAM_TO_ROBOT_SCALE_Y

    return robot_x, robot_y


# ── 로봇 동작 ─────────────────────────────────────────────────────────────────

def movej(robot, joints, speed=30, acc=30):
    print(f"  movej {[f'{v:.1f}' for v in joints]}")
    time.sleep(0.3)


def movel(robot, pos, speed=50, acc=50):
    print(f"  movel X={pos[0]:.1f} Y={pos[1]:.1f} Z={pos[2]:.1f}")
    time.sleep(0.3)


def set_gripper(robot, closed: bool):
    state = "닫기(파지)" if closed else "열기"
    print(f"  [그리퍼] {state}")
    time.sleep(0.3)


# ── 비전 픽앤플레이스 파이프라인 ─────────────────────────────────────────────

def pick_object(robot, robot_x: float, robot_y: float, rotation_deg: float):
    """감지된 물체 좌표로 픽업."""
    rz = rotation_deg  # 물체 회전 각도를 TCP Rz에 반영

    approach_pos = [robot_x, robot_y, APPROACH_HEIGHT_Z, 0.0, 180.0, rz]
    pick_pos     = [robot_x, robot_y, WORK_HEIGHT_Z,     0.0, 180.0, rz]

    set_gripper(robot, closed=False)     # 그리퍼 열기
    movel(robot, approach_pos, speed=80) # 접근
    movel(robot, pick_pos,     speed=20) # 하강 (느리게)
    set_gripper(robot, closed=True)      # 파지
    movel(robot, approach_pos, speed=30) # 들어올리기


def place_object(robot, place_x: float, place_y: float, rotation_deg: float = 0.0):
    """지정 위치에 물체 내려놓기."""
    approach_pos = [place_x, place_y, APPROACH_HEIGHT_Z, 0.0, 180.0, rotation_deg]
    place_pos    = [place_x, place_y, WORK_HEIGHT_Z,     0.0, 180.0, rotation_deg]

    movel(robot, approach_pos, speed=80)
    movel(robot, place_pos,    speed=20)
    set_gripper(robot, closed=False)
    movel(robot, approach_pos, speed=50)


# 플레이스 위치 (정렬 팔레트)
PLACE_POSITIONS = [
    (500.0,  50.0),
    (500.0,  -50.0),
    (500.0, -150.0),
]


def vision_pick_and_place_pipeline(robot):
    """비전 기반 픽앤플레이스 전체 파이프라인."""
    print("\n[비전 픽앤플레이스 파이프라인]")

    # 1) 홈 위치로 이동
    print("\n  [1] 홈 위치 이동")
    movej(robot, [0.0, -90.0, 90.0, 0.0, 90.0, 0.0])

    # 2) 카메라로 촬영 및 물체 감지
    print("\n  [2] 물체 감지")
    detected_objects = detect_objects_mock()

    if not detected_objects:
        print("  감지된 물체 없음. 종료.")
        return

    # 3) 각 물체 픽앤플레이스
    for i, obj in enumerate(detected_objects):
        if i >= len(PLACE_POSITIONS):
            print(f"  플레이스 위치 부족, {i+1}번째 물체 스킵")
            break

        print(f"\n  [3-{i+1}] {obj['label']} 처리")

        # 픽셀 → 로봇 좌표 변환
        robot_x, robot_y = pixel_to_robot(obj["cx"], obj["cy"])
        print(f"    픽셀({obj['cx']}, {obj['cy']}) → 로봇({robot_x:.1f}, {robot_y:.1f})")

        # 픽업
        pick_object(robot, robot_x, robot_y, obj["angle"])

        # 플레이스
        px, py = PLACE_POSITIONS[i]
        place_object(robot, px, py, rotation_deg=0.0)

    # 4) 홈 복귀
    print("\n  [4] 홈 복귀")
    movej(robot, [0.0, -90.0, 90.0, 0.0, 90.0, 0.0])
    print("\n[파이프라인 완료]")


def main():
    robot = None

    try:
        vision_pick_and_place_pipeline(robot)
    finally:
        print("\n[종료]")


if __name__ == "__main__":
    main()
