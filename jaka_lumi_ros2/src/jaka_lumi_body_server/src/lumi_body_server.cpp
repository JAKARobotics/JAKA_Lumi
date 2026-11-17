#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "control_msgs/action/follow_joint_trajectory.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include <std_srvs/srv/empty.hpp>
#include <nlohmann/json.hpp>
#include <curl/curl.h>

// #include <memory>
#include <mutex>
#include <thread>
#include <chrono>

using namespace std::chrono_literals;
using json = nlohmann::json;
using std::placeholders::_1;
using std::placeholders::_2;

class LumiBodyServer : public rclcpp::Node
{
public:
    using FollowJointTrajectory = control_msgs::action::FollowJointTrajectory;
    using GoalHandleFollowJointTrajectory = rclcpp_action::ServerGoalHandle<FollowJointTrajectory>;
    
    void call_stop_api();

    LumiBodyServer()
        : Node("lumi_body_server")
    {
        action_server_ = rclcpp_action::create_server<FollowJointTrajectory>(
            this,
            "/jaka_lumi_body_controller/follow_joint_trajectory",
            std::bind(&LumiBodyServer::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
            std::bind(&LumiBodyServer::handle_cancel, this, std::placeholders::_1),
            std::bind(&LumiBodyServer::handle_accepted, this, std::placeholders::_1));

        joint_state_pub_ = this->create_publisher<sensor_msgs::msg::JointState>(
            "/joint_states", 10);

        // ROS services
        stop_srv_ = this->create_service<std_srvs::srv::Empty>(
            "lumi_body/stop",
            std::bind(&LumiBodyServer::stopService, this, _1, _2)
        );

        reset_srv_ = this->create_service<std_srvs::srv::Empty>(
            "lumi_body/reset",
            std::bind(&LumiBodyServer::resetService, this, _1, _2)
        );

        // Start polling thread
        poll_thread_ = std::thread([this](){
            rclcpp::Rate rate(5); // 5 Hz
            while (rclcpp::ok() && running_) {
                this->pollStatus();
                rate.sleep();
            }
        });

        RCLCPP_INFO(this->get_logger(), "Lumi body FollowJointTrajectory action server ready!");
    }

    ~LumiBodyServer()
    {
        running_ = false;
        if (poll_thread_.joinable())
            poll_thread_.join();
    }

private:
    rclcpp_action::Server<FollowJointTrajectory>::SharedPtr action_server_;
    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_state_pub_;
    rclcpp::Service<std_srvs::srv::Empty>::SharedPtr stop_srv_;
    rclcpp::Service<std_srvs::srv::Empty>::SharedPtr reset_srv_;

    std::thread poll_thread_;
    std::mutex mtx_;
    bool running_{true};


    rclcpp_action::GoalResponse handle_goal(
        const rclcpp_action::GoalUUID &uuid,
        std::shared_ptr<const FollowJointTrajectory::Goal> goal)
    {
        (void)uuid;
        RCLCPP_INFO(this->get_logger(), "Received new trajectory goal.");
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_cancel(
        const std::shared_ptr<GoalHandleFollowJointTrajectory> goal_handle)
    {
        RCLCPP_WARN(this->get_logger(), "Received request to cancel goal.");
        {
            std::lock_guard<std::mutex> lock(mtx_);
            call_stop_api();
        }
        return rclcpp_action::CancelResponse::ACCEPT;
    }

    void handle_accepted(const std::shared_ptr<GoalHandleFollowJointTrajectory> goal_handle)
    {
        std::thread{std::bind(&LumiBodyServer::execute, this, goal_handle)}.detach();
    }

    void execute(const std::shared_ptr<GoalHandleFollowJointTrajectory> goal_handle)
    {
        const auto goal = goal_handle->get_goal();
        auto result = std::make_shared<FollowJointTrajectory::Result>();

        // Lock during execution to avoid conflicts
        std::lock_guard<std::mutex> lock(mtx_);

        if (!enable_robot(true)) {
            RCLCPP_ERROR(this->get_logger(), "Lumi not enabled.");
            result->error_code = -10;
            goal_handle->abort(result);
            return;
        }
        RCLCPP_INFO(this->get_logger(), "Lumi enabled.");

        RCLCPP_DEBUG(this->get_logger(), "Received trajectory with %ld points:", goal->trajectory.points.size());
        for (size_t i = 0; i < goal->trajectory.points.size(); ++i) {
            const auto &pt = goal->trajectory.points[i];
            std::stringstream ss;
            ss << "Point " << i << ": ";
            for (const auto &pos : pt.positions) {
                ss << pos << ", ";
            }
            RCLCPP_DEBUG(this->get_logger(), "%s", ss.str().c_str());
        }

        const auto& pt = goal->trajectory.points.back();  // Only final target point is used
        RCLCPP_INFO(this->get_logger(), "Final target trajectory points: %.3f %.3f %.3f %.3f", 
                    pt.positions[0], pt.positions[1], pt.positions[2], pt.positions[3]);

        if (pt.positions.size() < 4) {
            RCLCPP_ERROR(this->get_logger(), "Trajectory point has fewer than 4 joints.");
            result->error_code = -1;
            goal_handle->abort(result);
            return;
        }

        // Convert positions to match HTTP API expectations
        std::vector<double> converted_pos(4);
        converted_pos[0] = pt.positions[0] * 1000.0;                        // meters → mm
        converted_pos[1] = pt.positions[1] * 180.0 / M_PI;                  // radians → degrees
        converted_pos[2] = pt.positions[2] * 180.0 / M_PI;
        converted_pos[3] = pt.positions[3] * 180.0 / M_PI;

        RCLCPP_INFO(this->get_logger(), "Sending converted trajectory: %.2f mm, %.2f°, %.2f°, %.2f°",
                    converted_pos[0], converted_pos[1], converted_pos[2], converted_pos[3]);

        json payload;
        payload["pos"] = {
            converted_pos[0],
            converted_pos[1],
            converted_pos[2],
            converted_pos[3]};
        payload["vel"] = 100;
        payload["acc"] = 100;

        if (!call_move_to_api(payload))
        {
            RCLCPP_ERROR(this->get_logger(), "Moveto API call failed.");
            result->error_code = -2;
            goal_handle->abort(result);
            return;
        }

        RCLCPP_INFO(this->get_logger(), "Moveto API call success.");

        if (!wait_until_reached(converted_pos)) {
            RCLCPP_ERROR(this->get_logger(), "Timeout waiting for robot to reach target.");
            result->error_code = -3;
            goal_handle->abort(result);
            return;
        }

        auto feedback = std::make_shared<FollowJointTrajectory::Feedback>();
        feedback->joint_names = goal->trajectory.joint_names;
        feedback->actual.positions = pt.positions;  // Keep feedback in ROS units
        goal_handle->publish_feedback(feedback);
            

        // for (size_t i = 0; i < goal->trajectory.points.size(); ++i)
        // {
        //     auto &pt = goal->trajectory.points[i];
        //     if (pt.positions.size() < 4)
        //     {
        //         RCLCPP_ERROR(this->get_logger(), "Trajectory point has fewer than 4 joints.");
        //         result->error_code = -1;
        //         goal_handle->abort(result);
        //         return;
        //     }

        //     json payload;
        //     payload["pos"] = {
        //         pt.positions[0],
        //         pt.positions[1],
        //         pt.positions[2],
        //         pt.positions[3]};
        //     payload["vel"] = 100;
        //     payload["acc"] = 100;

        //     if (!call_move_to_api(payload))
        //     {
        //         RCLCPP_ERROR(this->get_logger(), "Moveto API call failed.");
        //         result->error_code = -2;
        //         goal_handle->abort(result);
        //         return;
        //     }
        //     RCLCPP_INFO(this->get_logger(), "Moveto API call success.");

        //     // Wait for robot to reach position
        //     if (!wait_until_reached(pt.positions)) {
        //         RCLCPP_ERROR(this->get_logger(), "Timeout waiting for robot to reach target.");
        //         result->error_code = -3;
        //         goal_handle->abort(result);
        //         return;
        //     }

        //     // Optionally publish feedback
        //     auto feedback = std::make_shared<FollowJointTrajectory::Feedback>();
        //     feedback->joint_names = goal->trajectory.joint_names;
        //     feedback->actual.positions = pt.positions;
        //     goal_handle->publish_feedback(feedback);
        // }

        enable_robot(false);

        RCLCPP_INFO(this->get_logger(), "Trajectory execution completed.");
        result->error_code = 0;
        goal_handle->succeed(result);
    }

    void pollStatus()
    {
        std::vector<double> positions = read_current_positions();

        RCLCPP_DEBUG(this->get_logger(), "Current joint positions: %.2f %.2f %.2f %.2f",
            positions[0], positions[1], positions[2], positions[3]);

        if (positions.empty()) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000, 
                                "Failed to read joint positions for publishing.");
            return;
        }

        sensor_msgs::msg::JointState msg;
        msg.header.stamp = this->now();
        for (size_t i = 0; i < positions.size(); i++) {
            msg.name.push_back("l_" + std::to_string(i + 1));

            // Handle unit conversion
            double pos_converted = 0.0;
            if (i == 0) {
                // Prismatic joint: mm to meters
                pos_converted = positions[i] / 1000.0;
            } else {
                // Revolute joints: degrees to radians
                pos_converted = positions[i] * M_PI / 180.0;
            }

            msg.position.push_back(pos_converted);
        }

        RCLCPP_DEBUG(this->get_logger(), "Publishing converted joint positions: %.3f %.3f %.3f %.3f",
                    msg.position[0], msg.position[1], msg.position[2], msg.position[3]);

        joint_state_pub_->publish(msg);
    }

    bool http_post(const std::string& url, const std::string& payload)
    {
        CURL* curl = curl_easy_init();
        if (!curl) return false;

        struct curl_slist *headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());

        CURLcode res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);

        if (res != CURLE_OK)
        {
            RCLCPP_ERROR(this->get_logger(), "HTTP POST request failed: %s", curl_easy_strerror(res));
            return false;
        }
        else
        {
            RCLCPP_INFO(this->get_logger(), "HTTP POST request to Lumi.");
            return true;
        }
    }

    bool http_get(const std::string& url, std::string& out_response)
    {
        CURL* curl = curl_easy_init();
        if (!curl) return false;

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &out_response);

        CURLcode res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if (res != CURLE_OK)
        {
            RCLCPP_ERROR(this->get_logger(), "HTTP GET request failed: %s", curl_easy_strerror(res));
            return false;
        }
        else
        {
            RCLCPP_DEBUG(this->get_logger(), "HTTP GET request to Lumi.");
            return true;
        }
    }

    static size_t writeCallback(void *contents, size_t size, size_t nmemb, void *userp)
    {
        ((std::string*)userp)->append((char*)contents, size * nmemb);
        return size * nmemb;
    }

    bool enable_robot(bool enable)
    {
        json payload;
        payload["enable"] = enable ? 1 : 0;
        std::string url = "http://192.168.10.90:5000/api/extaxis/enable";
        return http_post(url, payload.dump());
    }

    bool call_move_to_api(const json &payload)
    {
        std::string url = "http://192.168.10.90:5000/api/extaxis/moveto";
        return http_post(url, payload.dump());
    }

    // void call_stop_api()
    // {
    //     std::string url = "http://192.168.10.90:5000/api/extaxis/stop";
    //     http_post(url, "");
    // }

    bool wait_until_reached(const std::vector<double>& target_positions)
    {
        const int max_attempts = 50;
        int attempts = 0;

        while (attempts < max_attempts) {
            std::vector<double> current_pos = read_current_positions();

            if (current_pos.empty()) {
                RCLCPP_WARN(this->get_logger(), "Could not read current positions.");
                return false;
            }

            bool all_close = true;
            for (size_t i = 0; i < 4; i++) {
                if (std::abs(current_pos[i] - target_positions[i]) > 0.5) {
                    all_close = false;
                    break;
                }
            }

            if (all_close) {
                return true;
            }

            std::this_thread::sleep_for(200ms);
            ++attempts;
        }

        return false;
    }

    std::vector<double> read_current_positions()
    {
        std::string url = "http://192.168.10.90:5000/api/extaxis/status";
        std::string response;

        if (!http_get(url, response)) {
            return {};
        }

        std::vector<double> pos(4, 0.0);
        try {
            auto j = json::parse(response);
            for (const auto& joint : j) {
                int id = joint["id"];
                if (id >= 0 && id < 4) {
                    pos[id] = joint["pos"].get<double>();
                }
            }
        } catch (...) {
            return {};
        }
        return pos;
    }

    void stopService(
        const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
        std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/)
    {
        call_stop_api();
        RCLCPP_INFO(this->get_logger(), "Stop command sent.");
    }

    void resetService(
        const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
        std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/)
    {
        std::string url = "http://192.168.10.90:5000/api/extaxis/reset";
        http_post(url, "");
        RCLCPP_INFO(this->get_logger(), "Reset command sent.");
    }

};

std::shared_ptr<LumiBodyServer> lumi_action_node = nullptr;

void LumiBodyServer::call_stop_api()
{
    std::string url = "http://192.168.10.90:5000/api/extaxis/stop";
    http_post(url, "");
}

void sigintHandler(int /*sig*/) {
    if (lumi_action_node) {
        lumi_action_node->call_stop_api();
        RCLCPP_WARN(lumi_action_node->get_logger(), "SIGINT received! Stopping Lumi body via API...");
    }
    rclcpp::shutdown();
}

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    signal(SIGINT, sigintHandler);
    lumi_action_node = std::make_shared<LumiBodyServer>();
    rclcpp::spin(lumi_action_node);
    // auto node = std::make_shared<LumiBodyServer>();
    // rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
