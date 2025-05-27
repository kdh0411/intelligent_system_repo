const ros = new ROSLIB.Ros({
    url: "ws://localhost:9090"
  });
  
  ros.on("connection", () => console.log("✅ ROS 연결 성공"));
  ros.on("error", err => console.error("❌ 연결 오류:", err));
  ros.on("close", () => console.warn("🔌 ROS 연결 종료됨"));
  
  const zoneToPose = {
    "1번": { x: -5.649, y: -3.583, z: 0.0, oz: 0.99996, ow: 0.0084 },
    "2번": { x: -5.678, y: -1.247, z: 0.0, oz: -0.97556, ow: 0.2197 },
    "3번": { x: -5.896, y: 1.422, z: 0.0, oz: 0.99814, ow: 0.0608 },
    "4번": { x: -5.934, y: 3.652, z: 0.0, oz: 0.98531, ow: 0.1707 }
  };
  
  const navClient = new ROSLIB.ActionClient({
    ros: ros,
    serverName: "/navigate_to_pose",
    actionName: "nav2_msgs/action/NavigateToPose",
    actionType: "nav2_msgs/action/NavigateToPose"  
  });
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".call-robot-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const zone = btn.dataset.zone;
            console.log("📦 받은 zone:", `"${zone}"`);
            console.log("📦 zoneToPose keys:", Object.keys(zoneToPose));
          
            const pose = zoneToPose[zone];
            if (!pose) {
              alert("❗ 유효하지 않은 책장 번호입니다.");
              return;
            }
          
            const goal = new ROSLIB.Goal({
              actionClient: navClient,
              goalMessage: {
                pose: {
                  header: {
                    frame_id: "map",
                    stamp: { sec: 0, nanosec: 0 }
                  },
                  pose: {
                    position: { x: pose.x, y: pose.y, z: 0.0 },
                    orientation: { x: 0.0, y: 0.0, z: pose.oz, w: pose.ow }
                  }
                },
                behavior_tree: ""
              }
            });
            
            
  
        goal.send();
        alert(`📍 ${zone} 책장으로 이동 중입니다.`);
      });
    });
  });
  