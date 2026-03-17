"""
[중급 예제 1] 궤적 계획 및 다중 웨이포인트 이동
--------------------------------------------------
목표: 여러 경유점을 부드럽게 통과하는 궤적 만들기

학습 포인트:
- movec() 원호 이동
- 웨이포인트 리스트로 연속 경로 실행
- 블렌딩 반경(blending radius)으로 경로 부드럽게 처리
- numpy를 사용한 궤적 사전 계산
"""

import time
import math
import numpy as np

ROBOT_IP = "192.168.0.1"

# 기준 자세
BASE_ORIENTATION = [0.0, 180.0, 0.0]   # [Rx, Ry, Rz] deg


def movel(robot, pos, speed=50.0, acc=50.0, blend_radius=0.0):
    """직선 이동. blend_radius > 0 이면 다음 포인트와 블렌딩."""
    print(f"  L [{pos[0]:6.1f},{pos[1]:6.1f},{pos[2]:6.1f}] "
          f"spd={speed:.0f} blend={blend_radius:.0f}")
    time.sleep(0.2)


def movec(robot, via_pos, target_pos, speed=50.0, acc=50.0):
    """원호 이동. via_pos를 지나 target_pos로 원호 경로."""
    print(f"  C via=[{via_pos[0]:.1f},{via_pos[1]:.1f},{via_pos[2]:.1f}] "
          f"-> [{target_pos[0]:.1f},{target_pos[1]:.1f},{target_pos[2]:.1f}] "
          f"spd={speed:.0f}")
    time.sleep(0.3)


# ── 예제 1: 웨이포인트 연속 이동 ──────────────────────────────────────────────

def run_waypoints(robot, waypoints: list, speed: float = 80.0, blend: float = 20.0):
    """
    웨이포인트 리스트를 순서대로 직선 이동.
    마지막 포인트를 제외하고 블렌딩 반경을 적용해 경로를 부드럽게 합니다.
    """
    print(f"\n[웨이포인트 이동] {len(waypoints)}개 경유점, 블렌딩={blend}mm")
    for i, wp in enumerate(waypoints):
        is_last = (i == len(waypoints) - 1)
        movel(robot, wp, speed=speed, blend_radius=0.0 if is_last else blend)


# ── 예제 2: numpy로 원 궤적 사전 계산 ────────────────────────────────────────

def generate_circle_waypoints(
    center_x: float,
    center_y: float,
    radius: float,
    z: float,
    num_points: int = 36,
) -> list:
    """
    XY 평면의 원형 궤적 포인트를 생성합니다.

    Args:
        center_x  : 원 중심 X (mm)
        center_y  : 원 중심 Y (mm)
        radius    : 반지름 (mm)
        z         : 높이 Z (mm)
        num_points: 분할 수 (많을수록 부드러움)

    Returns:
        list of [X, Y, Z, Rx, Ry, Rz]
    """
    angles = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
    waypoints = []
    for angle in angles:
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        waypoints.append([x, y, z] + BASE_ORIENTATION)
    return waypoints


def demo_circle_trajectory(robot):
    """원형 궤적 데모"""
    print("\n[원형 궤적 데모] 반지름=80mm, 36포인트")
    waypoints = generate_circle_waypoints(400.0, 0.0, radius=80.0, z=300.0, num_points=36)

    # 시작 지점으로 먼저 이동
    movel(robot, waypoints[0], speed=100.0)

    # 원형 경로 순환 (블렌딩으로 부드러운 원)
    run_waypoints(robot, waypoints + [waypoints[0]], speed=60.0, blend=15.0)
    print("  원 완성!")


# ── 예제 3: movec으로 정확한 반원 그리기 ─────────────────────────────────────

def demo_arc_move(robot):
    """movec을 사용해 반원 경로를 그립니다."""
    print("\n[원호(Arc) 이동 데모]")

    start  = [350.0,  0.0, 300.0] + BASE_ORIENTATION
    via    = [400.0, 80.0, 300.0] + BASE_ORIENTATION   # 원호 중간점
    end    = [450.0,  0.0, 300.0] + BASE_ORIENTATION

    movel(robot, start, speed=50.0)
    print("  반원 이동 시작")
    movec(robot, via, end, speed=40.0)
    print("  반원 완료")


# ── 예제 4: 지그재그 패턴 (용접/도포 경로) ────────────────────────────────────

def generate_zigzag_waypoints(
    start_x: float,
    start_y: float,
    length: float,
    width: float,
    num_rows: int,
    z: float,
) -> list:
    """
    용접/도포 작업용 지그재그 경로를 생성합니다.

    Args:
        start_x : 시작 X (mm)
        start_y : 시작 Y (mm)
        length  : 행 길이 (mm)
        width   : 행 간격 (mm)
        num_rows: 행 수
        z       : 작업 높이 Z (mm)
    """
    waypoints = []
    for row in range(num_rows):
        y = start_y + row * width
        if row % 2 == 0:                          # 짝수 행: 좌→우
            waypoints.append([start_x,          y, z] + BASE_ORIENTATION)
            waypoints.append([start_x + length, y, z] + BASE_ORIENTATION)
        else:                                     # 홀수 행: 우→좌
            waypoints.append([start_x + length, y, z] + BASE_ORIENTATION)
            waypoints.append([start_x,          y, z] + BASE_ORIENTATION)
    return waypoints


def demo_zigzag(robot):
    """지그재그 패턴 데모 (예: 도포 작업)"""
    print("\n[지그재그 패턴 데모]")
    waypoints = generate_zigzag_waypoints(
        start_x=350.0, start_y=-100.0,
        length=100.0, width=20.0, num_rows=6, z=300.0
    )
    run_waypoints(robot, waypoints, speed=40.0, blend=5.0)
    print("  지그재그 완료")


def main():
    robot = None  # 실제: RBCOBOTClient(ROBOT_IP); robot.connect()

    try:
        demo_circle_trajectory(robot)
        demo_arc_move(robot)
        demo_zigzag(robot)
    finally:
        print("\n[종료]")


if __name__ == "__main__":
    main()
