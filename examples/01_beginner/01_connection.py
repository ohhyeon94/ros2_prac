"""
[입문 예제 1] 로봇 연결 및 상태 확인
---------------------------------------
목표: 로봇에 연결하고 현재 상태(조인트 각도, TCP 위치)를 읽어오기

학습 포인트:
- RB SDK 초기화 방법
- 로봇 연결/해제
- 상태값 읽기 (get_joint_pos, get_tcp_pos)
"""

import time

# ※ 실제 SDK import명은 레인보우 로보틱스 공식 문서를 확인하세요
# from rb.api import RBCOBOTClient  # 예시 import

ROBOT_IP = "192.168.0.1"   # 실제 로봇 IP로 변경
ROBOT_PORT = 5000           # 기본 포트


def connect_robot(ip: str, port: int):
    """로봇에 TCP 소켓으로 연결합니다."""
    # robot = RBCOBOTClient(ip, port)
    # robot.connect()
    print(f"[연결] {ip}:{port} 에 연결 시도 중...")
    # return robot
    print("[연결] 연결 성공 (시뮬레이션)")
    return None  # 실제 SDK 사용 시 robot 객체 반환


def read_robot_status(robot):
    """로봇의 현재 조인트 각도와 TCP 위치를 출력합니다."""
    # joint_pos = robot.get_joint_pos()  # [J1, J2, J3, J4, J5, J6] 단위: deg
    # tcp_pos   = robot.get_tcp_pos()    # [X, Y, Z, Rx, Ry, Rz] 단위: mm, deg

    # 시뮬레이션 값 (실제 사용 시 위 주석 해제)
    joint_pos = [0.0, -90.0, 90.0, 0.0, 90.0, 0.0]
    tcp_pos   = [400.0, 0.0, 500.0, 0.0, 180.0, 0.0]

    print("\n===== 로봇 현재 상태 =====")
    print(f"조인트 각도 (deg) : {[f'{v:.2f}' for v in joint_pos]}")
    print(f"TCP 위치 (mm/deg) : {[f'{v:.2f}' for v in tcp_pos]}")
    print("==========================\n")


def disconnect_robot(robot):
    """로봇 연결을 해제합니다."""
    # robot.disconnect()
    print("[연결 해제] 로봇 연결 종료")


def main():
    robot = connect_robot(ROBOT_IP, ROBOT_PORT)

    try:
        # 1초마다 3번 상태 출력
        for i in range(3):
            print(f"[{i+1}/3회 상태 읽기]")
            read_robot_status(robot)
            time.sleep(1.0)
    finally:
        disconnect_robot(robot)


if __name__ == "__main__":
    main()
