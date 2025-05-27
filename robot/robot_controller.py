import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient

zone_to_pose = {
    #책장
    "1번": (-5.71, -3.71, -0.01, 0.99),
    "2번": (-4.99, -1.39,  0.02, 0.99),
    "3번": (-5.44,  1.19, -0.00, 0.99),
    "4번": (-5.26,  3.73,  0.10, 0.99),

    #테이블
    "shelf1": (4.26,  0.81, -0.65, 0.76),  
    "shelf2": (2.38,  0.50,  0.73, 0.69),  
    "shelf3": (-0.13, 0.28, -0.78, 0.63),  
    "shelf4": (-1.90, 0.08,  0.71, 0.71), 

    #홈
    "home": (5.44, -3.89, 0.71, 0.71)
}   

#책장 이동
def send_goal_to_bookshelf(zone: str):
    if zone not in {"1번", "2번", "3번", "4번"}:
        return False, "❌ 유효하지 않은 책장 zone입니다."
    return _send_goal(zone, label="책장")

#홈, 테이블 이동
def send_goal_to_table_or_home(zone: str):
    if zone not in {"shelf1", "shelf2", "shelf3", "shelf4", "home"}:
        return False, "❌ 유효하지 않은 테이블/home zone입니다."
    return _send_goal(zone, label="지점")

# 내부 공통 동작
def _send_goal(zone: str, label="지점"):
    x, y, oz, ow = zone_to_pose[zone]

    try:
        rclpy.init()
        node = Node("robot_goal_sender")
        client = ActionClient(node, NavigateToPose, "/navigate_to_pose")

        if not client.wait_for_server(timeout_sec=3.0):
            node.destroy_node()
            rclpy.shutdown()
            return False, "❌ 액션 서버 연결 실패"

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = oz
        goal_msg.pose.pose.orientation.w = ow

        future = client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(node, future)

        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(node, result_future)

        node.destroy_node()
        rclpy.shutdown()
        return True, f"✅ 로봇이 {zone} {label}으로 이동 중입니다."
    except Exception as e:
        return False, f"❗ 예외 발생: {str(e)}"
