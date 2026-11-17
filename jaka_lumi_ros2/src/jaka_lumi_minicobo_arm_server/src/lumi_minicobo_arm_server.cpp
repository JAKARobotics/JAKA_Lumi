#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/empty.hpp"
#include "std_srvs/srv/empty.hpp"
#include "std_srvs/srv/set_bool.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

#include "jaka_lumi_minicobo_arm_server/JAKAZuRobot.h"
#include "jaka_lumi_minicobo_arm_server/jkerr.h"
#include "jaka_lumi_minicobo_arm_server/jktypes.h"

#include <action_msgs/msg/goal_status_array.hpp>
#include <control_msgs/action/follow_joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include "rclcpp_action/rclcpp_action.hpp"

#include <string>
#include <map>
#include <thread>
using namespace std;

JAKAZuRobot robot;
const double PI = 3.1415926;
// bool in_pos;
// int ret_preempt;
// int ret_inPos;

typedef rclcpp_action::Server<control_msgs::action::FollowJointTrajectory> Server;
rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_states_pub;

// Map error codes to messages
map<int, string> mapErr = {
    {2,   "ERR_FUCTION_CALL_ERROR"},
    {-1,  "ERR_INVALID_HANDLER"},
    {-2,  "ERR_INVALID_PARAMETER"},
    {-3,  "ERR_COMMUNICATION_ERR"},
    {-4,  "ERR_KINE_INVERSE_ERR"},
    {-5,  "ERR_EMERGENCY_PRESSED"},
    {-6,  "ERR_NOT_POWERED"},
    {-7,  "ERR_NOT_ENABLED"},
    {-8,  "ERR_DISABLE_SERVOMODE"},
    {-9,  "ERR_NOT_OFF_ENABLE"},
    {-10, "ERR_PROGRAM_IS_RUNNING"},
    {-11, "ERR_CANNOT_OPEN_FILE"},
    {-12, "ERR_MOTION_ABNORMAL"}
};

// Determine if the robot has reached the target position.
bool jointStates(const JointValue &joint_pose)
{
    // RobotStatus robotstatus;
    JointValue joint_position;
    // robot.get_robot_status(&robotstatus);
    robot.get_joint_position(&joint_position);

    bool joint_state = true;
    for (int i = 0; i < 6; i++)
    {
        // double actual_deg = robotstatus.joint_position[i] * 180.0 / PI;
        double actual_deg = joint_position.jVal[i] * 180.0 / PI;
        double target_deg = joint_pose.jVal[i] * 180.0 / PI;
        // Within +/- 0.2 degrees tolerance
        bool ret = (target_deg - 0.2 < actual_deg) && (actual_deg < target_deg + 0.2);
        joint_state = joint_state && ret;
    }

    RCLCPP_INFO(rclcpp::get_logger("jointStates"), 
                "Whether the robot has reached the target position: %d", joint_state);
    return joint_state;
}

// Handle a new FollowJointTrajectory goal
void goalCb(const shared_ptr<rclcpp_action::ServerGoalHandle<control_msgs::action::FollowJointTrajectory>> goal_handle)
{
    // Enable servo mode
    robot.servo_move_enable(true);

    // Retrieve the trajectory from the goal
    auto goal = goal_handle->get_goal();
    const auto &traj = goal->trajectory;
    int point_num = traj.points.size();
    RCLCPP_INFO(rclcpp::get_logger("goalCb"), "number of points: %d", point_num);

    if (point_num == 0)
    {
        RCLCPP_ERROR(rclcpp::get_logger("goalCb"), "Trajectory has no points. Aborting goal.");
        goal_handle->abort(make_shared<control_msgs::action::FollowJointTrajectory::Result>());
        return;
    }

    float lastDuration = 0.0;
    JointValue joint_pose;

    for (int i = 1; i < point_num; i++)
    {
        // Grab the positions from the i-th trajectory point
        for (int j = 0; j < 6; j++) {
            joint_pose.jVal[j] = traj.points[i].positions[j];
        }

        // Convert time_from_start to a float seconds
        float Duration = static_cast<float>(traj.points[i].time_from_start.sec) +
                         static_cast<float>(traj.points[i].time_from_start.nanosec) * 1e-9;

        // Calculate time delta relative to previous point
        float dt = Duration - lastDuration;
        lastDuration = Duration;

        // step_num matches old ROS1 logic: step_num = dt / 0.008
        int step_num = static_cast<int>(dt / 0.008f);
        step_num = max(step_num, 1);

        int sdk_res = robot.servo_j(&joint_pose, MoveMode::ABS, step_num);
        if (sdk_res != 0)
        {
            RCLCPP_INFO(rclcpp::get_logger("goalCb"), "Servo_j Motion Failed");
        }

        RCLCPP_INFO(rclcpp::get_logger("goalCb"), "The return status of servo_j: %d", sdk_res);
        RCLCPP_INFO(rclcpp::get_logger("goalCb"), 
                    "For point no.: %d, Accepted joint angle: %f %f %f %f %f %f, dt=%f, step_num=%d", i,
                    joint_pose.jVal[0], joint_pose.jVal[1], joint_pose.jVal[2],
                    joint_pose.jVal[3], joint_pose.jVal[4], joint_pose.jVal[5],
                    dt, step_num);

        // // Check if the action was canceled in the middle
        // if (goal_handle->is_canceling())
        // {
        //     // stop motion
        //     robot.motion_abort();
        //     robot.servo_move_enable(false);
        //     RCLCPP_INFO(rclcpp::get_logger("goalCb"), "Servo Mode Disable, motion canceled");
        //     auto result = make_shared<control_msgs::action::FollowJointTrajectory::Result>();
        //     goal_handle->canceled(result);
        //     return;
        // }
    }

    // Wait until the robot is actually at the final position, or until canceled
    while (rclcpp::ok())
    {
        if (jointStates(joint_pose))
        {
            robot.servo_move_enable(false);
            RCLCPP_INFO(rclcpp::get_logger("goalCb"), "Servo Mode Disable: Target Reached");
            RCLCPP_INFO(rclcpp::get_logger("goalCb"), 
                        "==============Motion stops or reaches the target position==============");
            break;
        }

        // if (goal_handle->is_canceling())
        // {
        //     robot.motion_abort();
        //     robot.servo_move_enable(false);
        //     RCLCPP_INFO(rclcpp::get_logger("goalCb"), "Servo Mode Disable");
        //     RCLCPP_INFO(rclcpp::get_logger("goalCb"), 
        //                 "==============Motion stops or was canceled==============");
        //     auto result = make_shared<control_msgs::action::FollowJointTrajectory::Result>();
        //     goal_handle->canceled(result);
        //     return;
        // }

        rclcpp::sleep_for(chrono::milliseconds(500));
    }

    // // After processing all points, check if the goal was canceled
    // if (goal_handle->is_canceling()) {
    //     robot.motion_abort();
    //     robot.servo_move_enable(false);
    //     RCLCPP_INFO(rclcpp::get_logger("goalCb"), "Servo Mode Disabled, Motion Canceled");
    //     auto result = make_shared<control_msgs::action::FollowJointTrajectory::Result>();
    //     goal_handle->canceled(result);
    //     return;
    // }

    // If we get here, it succeeded
    auto result = make_shared<control_msgs::action::FollowJointTrajectory::Result>();
    goal_handle->succeed(result);
    rclcpp::sleep_for(chrono::milliseconds(500));
}

// Publish the robot's joint states to /joint_states (for RViz / MoveIt feedback)
void joint_states_callback(rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr &joint_states_pub)
{
    sensor_msgs::msg::JointState joint_msg;
    // RobotStatus robotstatus;
    JointValue joint_position;
    // robot.get_robot_status(&robotstatus);
    robot.get_joint_position(&joint_position);

    for (int i = 0; i < 6; i++)
    {
        // joint_msg.position.push_back(robotstatus.joint_position[i]);
        joint_msg.position.push_back(joint_position.jVal[i]);
        joint_msg.name.push_back("l_a" + to_string(i+1));
    }
    joint_msg.header.stamp = rclcpp::Clock().now();
    joint_states_pub->publish(joint_msg);
}

void sigintHandler(int /*sig*/) {
    rclcpp::shutdown();
}

int main(int argc, char *argv[])
{
    setlocale(LC_ALL, "");
    rclcpp::init(argc, argv);
    signal(SIGINT, sigintHandler);
    auto node = rclcpp::Node::make_shared("lumi_minicobo_arm_server");

    // Read parameters
    // string default_ip = "10.5.5.100";
    string default_ip = "192.168.10.90";
    string robot_ip = node->declare_parameter("ip", default_ip);

    // Connect to robot
    robot.login_in(robot_ip.c_str(), true);
    rclcpp::Rate rate(125);

    // Turn off servo at startup
    robot.servo_move_enable(false);
    rclcpp::sleep_for(chrono::milliseconds(500));

    // Filter param
    robot.servo_move_use_joint_LPF(0.5);

    // Power on + enable
    robot.power_on();
    rclcpp::sleep_for(chrono::seconds(8));
    robot.enable_robot();
    rclcpp::sleep_for(chrono::seconds(4));

    // Publisher for /joint_states
    joint_states_pub = node->create_publisher<sensor_msgs::msg::JointState>("/joint_states", 10);

    // Create Action Server for FollowJointTrajectory
    auto lumi_minicobo_arm_server = rclcpp_action::create_server<control_msgs::action::FollowJointTrajectory>(
        node,
        "/jaka_lumi_minicobo_arm_controller/follow_joint_trajectory",
        // Goal callback
        [](const rclcpp_action::GoalUUID &uuid,
           shared_ptr<const control_msgs::action::FollowJointTrajectory::Goal> goal) {
            RCLCPP_INFO(rclcpp::get_logger("lumi_minicobo_arm_server"), "Received goal request");
            (void)uuid; // Avoid unused parameter warning
            (void)goal; // Avoid unused parameter warning
            return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        // // Cancel callback
        // [](const shared_ptr<rclcpp_action::ServerGoalHandle<control_msgs::action::FollowJointTrajectory>> goal_handle) {
        //     (void)goal_handle;  // Avoid unused parameter warning
        //     RCLCPP_INFO(rclcpp::get_logger("lumi_minicobo_arm_server"), "Received cancel request");
        //     return rclcpp_action::CancelResponse::ACCEPT;
        // },
        nullptr,  // Cancel callback removed
        // Execute callback
        [](const shared_ptr<rclcpp_action::ServerGoalHandle<control_msgs::action::FollowJointTrajectory>> goal_handle) {
            RCLCPP_INFO(rclcpp::get_logger("lumi_minicobo_arm_server"), "Executing goal");
            goalCb(goal_handle); 
        }
    );

    RCLCPP_INFO(rclcpp::get_logger("lumi_minicobo_arm_server"), "==================Moveit Start==================");

    // Main spin loop
    while (rclcpp::ok())
    {
        // Publish joint states at ~125Hz
        joint_states_callback(joint_states_pub);
        rate.sleep();
        rclcpp::spin_some(node);
    }

    rclcpp::shutdown();
    return 0;
}
