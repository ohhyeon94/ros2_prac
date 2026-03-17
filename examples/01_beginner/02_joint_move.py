"""
[입문 예제 2] 조인트 공간 이동 (Joint Move)
----------------------------------------------
목표: 각 조인트를 지정한 각도로 이동시키기

학습 포인트:
- movej() 명령 사용법
- 속도/가속도 파라미터 의미
- 블로킹(blocking) vs 논블로킹 이동
- 홈 포지션 개념
"""

import time

ROBOT_IP = "192.168.0.1"
MOVE_SPEED = 30     # 최대 속도의 30 %
MOVE_ACC   = 30     # 최대 가속도의 30 %


# 자주 사용하는 조인트 포지션 정의 (단위: deg)
HOME_POSITION  = [0.0,   0.0,  0.0,  0.0,  0.0,  0.0]
READY_POSITION = [0.0, -90.0, 90.0,  0.0, 90.0,  0.0]
POSE_A         = [30.0, -60.0, 70.0, 10.0, 80.0, 15.0]
POSE_B         = [-30.0, -70.0, 80.0, -10.0, 100.0, -15.0]


def movej(robot, joint_angles: list, speed: int = 20, acc: int = 20, blocking: bool = True):
    """
    조인트 공간 이동 래퍼 함수.

    Args:
        robot       : 로봇 클라이언트 객체
        joint_angles: 6개 조인트 목표 각도 [J1~J6] (deg)
        speed       : 이동 속도 (0~100 %)
        acc         : 가속도 (0~100 %)
        blocking    : True면 이동 완료까지 대기
    """
    # robot.movej(joint_angles, speed, acc, blocking)  # 실제 SDK 호출
    print(f"  movej -> {[f'{v:6.1f}' for v in joint_angles]}, "
          f"speed={speed}%, acc={acc}%, blocking={blocking}")
    time.sleep(0.5)  # 시뮬레이션 딜레이


def demo_basic_sequence(robot):
    """홈 → 준비 → A → B → 준비 → 홈 순서로 이동"""
    print("\n[시퀀스 시작] Home → Ready → A → B → Ready → Home")

    steps = [
        ("Home",  HOME_POSITION),
        ("Ready", READY_POSITION),
        ("Pose A", POSE_A),
        ("Pose B", POSE_B),
        ("Ready", READY_POSITION),
        ("Home",  HOME_POSITION),
    ]

    for name, pos in steps:
        print(f"\n  이동: {name}")
        movej(robot, pos, speed=MOVE_SPEED, acc=MOVE_ACC)
        time.sleep(0.3)

    print("\n[시퀀스 완료]")


def demo_speed_comparison(robot):
    """같은 동작을 서로 다른 속도로 수행하여 차이 체험"""
    print("\n[속도 비교 데모]")
    for speed in [10, 30, 60]:
        print(f"\n  속도 {speed}%로 POSE_A → POSE_B 이동")
        movej(robot, POSE_A, speed=speed, acc=speed)
        movej(robot, POSE_B, speed=speed, acc=speed)
    movej(robot, HOME_POSITION, speed=30, acc=30)


def main():
    # robot = RBCOBOTClient(ROBOT_IP); robot.connect()
    robot = None  # 시뮬레이션

    try:
        demo_basic_sequence(robot)
        demo_speed_comparison(robot)
    finally:
        # robot.disconnect()
        print("\n[종료] 연결 해제")


if __name__ == "__main__":
    main()
