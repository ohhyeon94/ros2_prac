"""
[입문 예제 3] 직선 이동 (Linear Move / movel)
-----------------------------------------------
목표: TCP(공구 끝점)를 직선 경로로 이동시키기

학습 포인트:
- movel() 명령 사용법
- TCP 좌표계 (X, Y, Z, Rx, Ry, Rz)
- 조인트 이동(movej)과 직선 이동(movel) 차이
- 안전한 접근/후퇴 경로 설계
"""

import time

ROBOT_IP = "192.168.0.1"
SPEED    = 50   # mm/s
ACC      = 50   # mm/s²

# TCP 포지션: [X(mm), Y(mm), Z(mm), Rx(deg), Ry(deg), Rz(deg)]
HOME_TCP   = [400.0,   0.0, 500.0,   0.0, 180.0,   0.0]
APPROACH   = [400.0, 200.0, 300.0,   0.0, 180.0,   0.0]  # 목표 위 100mm
TARGET     = [400.0, 200.0, 200.0,   0.0, 180.0,   0.0]  # 실제 작업 지점
RETREAT    = [400.0, 200.0, 300.0,   0.0, 180.0,   0.0]  # 후퇴 (= APPROACH)


def movel(robot, tcp_pos: list, speed: float = 50.0, acc: float = 50.0, blocking: bool = True):
    """
    직선(Linear) 이동 래퍼 함수.

    Args:
        robot   : 로봇 클라이언트 객체
        tcp_pos : 목표 TCP 포즈 [X, Y, Z, Rx, Ry, Rz]
        speed   : 이동 속도 (mm/s)
        acc     : 가속도 (mm/s²)
        blocking: True면 완료까지 대기
    """
    # robot.movel(tcp_pos, speed, acc, blocking)
    print(f"  movel -> X={tcp_pos[0]:.1f}, Y={tcp_pos[1]:.1f}, Z={tcp_pos[2]:.1f}, "
          f"Rx={tcp_pos[3]:.1f}, Ry={tcp_pos[4]:.1f}, Rz={tcp_pos[5]:.1f} "
          f"| {speed}mm/s")
    time.sleep(0.5)


def pick_and_place_demo(robot):
    """
    간단한 픽앤플레이스 경로:
      홈 → 접근 → 픽업 → 후퇴 → 홈
    """
    print("\n[픽앤플레이스 경로 데모]")

    print("  1) 홈 위치로 이동")
    movel(robot, HOME_TCP, speed=100)

    print("  2) 픽업 지점 위 (접근)")
    movel(robot, APPROACH, speed=100)

    print("  3) 픽업 지점으로 하강 (느리게)")
    movel(robot, TARGET, speed=20)   # 접촉 전 속도 감속

    print("  4) [그리퍼 닫기] - 실제 구현 시 그리퍼 신호 출력")
    time.sleep(0.5)

    print("  5) 후퇴 (느리게)")
    movel(robot, RETREAT, speed=20)

    print("  6) 홈으로 복귀")
    movel(robot, HOME_TCP, speed=100)

    print("\n[픽앤플레이스 완료]")


def draw_square(robot, center_x: float, center_y: float, side: float, z: float, speed: float):
    """
    XY 평면에서 정사각형을 직선 이동으로 그립니다.

    Args:
        center_x: 사각형 중심 X
        center_y: 사각형 중심 Y
        side    : 한 변의 길이 (mm)
        z       : 작업 높이 Z
        speed   : 이동 속도 (mm/s)
    """
    half = side / 2
    orientation = [0.0, 180.0, 0.0]  # Rx, Ry, Rz

    corners = [
        [center_x - half, center_y - half, z] + orientation,
        [center_x + half, center_y - half, z] + orientation,
        [center_x + half, center_y + half, z] + orientation,
        [center_x - half, center_y + half, z] + orientation,
        [center_x - half, center_y - half, z] + orientation,  # 시작점으로 복귀
    ]

    print(f"\n[사각형 그리기] 중심=({center_x},{center_y}), 변길이={side}mm")
    for i, corner in enumerate(corners):
        label = "시작/종료" if i in (0, 4) else f"꼭짓점 {i}"
        print(f"  {label}")
        movel(robot, corner, speed=speed)


def main():
    robot = None  # 실제: RBCOBOTClient(ROBOT_IP); robot.connect()

    try:
        pick_and_place_demo(robot)
        draw_square(robot, center_x=400.0, center_y=0.0, side=100.0, z=250.0, speed=30.0)
    finally:
        print("\n[종료] 연결 해제")


if __name__ == "__main__":
    main()
