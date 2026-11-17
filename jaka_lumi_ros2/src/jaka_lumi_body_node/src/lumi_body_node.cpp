#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_srvs/srv/empty.hpp>
#include "std_srvs/srv/set_bool.hpp"

#include "jaka_lumi_body_node/srv/move_service.hpp"
#include "jaka_lumi_body_node/srv/read_status_service.hpp"

#include <curl/curl.h>
#include <nlohmann/json.hpp>

#include <string>
#include <vector>
#include <thread>
#include <mutex>

using json = nlohmann::json;
using std::placeholders::_1;
using std::placeholders::_2;

class LumiBodyNode : public rclcpp::Node
{
public:
    LumiBodyNode()
    : Node("lumi_body_node")
    {
        // Publisher for joint_states
        pub_ = this->create_publisher<sensor_msgs::msg::JointState>("/joint_states", 10);

        // // Subscriber for target joint_states (from RViz sliders)
        // sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
        //     "/joint_states", 10,
        //     std::bind(&LumiBodyNode::jointStateCallback, this, _1)
        // );

        // ROS services
        stop_srv_ = this->create_service<std_srvs::srv::Empty>(
            "lumi_body/stop",
            std::bind(&LumiBodyNode::stopService, this, _1, _2)
        );

        reset_srv_ = this->create_service<std_srvs::srv::Empty>(
            "lumi_body/reset",
            std::bind(&LumiBodyNode::resetService, this, _1, _2)
        );

        enable_srv_ = this->create_service<std_srvs::srv::SetBool>(
            "lumi_body/enable",
            std::bind(&LumiBodyNode::enableService, this, _1, _2)
        );

        move_srv_ = this->create_service<jaka_lumi_body_node::srv::MoveService>(
            "lumi_body/move",
            std::bind(&LumiBodyNode::moveService, this, _1, _2)
        );

        read_status_srv_ = this->create_service<jaka_lumi_body_node::srv::ReadStatusService>(
            "lumi_body/read_status",
            std::bind(&LumiBodyNode::readStatusService, this, _1, _2)
        );

        current_positions_.resize(4, 0.0);

        // Start polling thread
        poll_thread_ = std::thread([this](){
            rclcpp::Rate rate(5); // 5 Hz
            while (rclcpp::ok() && running_) {
                this->pollStatus();
                rate.sleep();
            }
        });

        RCLCPP_INFO(this->get_logger(), "Lumi body node started!");
    }

    ~LumiBodyNode()
    {
        running_ = false;
        if (poll_thread_.joinable())
            poll_thread_.join();
    }

private:
    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr pub_;
    // rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_;
    rclcpp::Service<std_srvs::srv::Empty>::SharedPtr stop_srv_;
    rclcpp::Service<std_srvs::srv::Empty>::SharedPtr reset_srv_;
    rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr enable_srv_;
    rclcpp::Service<jaka_lumi_body_node::srv::MoveService>::SharedPtr move_srv_;
    rclcpp::Service<jaka_lumi_body_node::srv::ReadStatusService>::SharedPtr read_status_srv_;

    std::thread poll_thread_;
    std::mutex mtx_;
    bool running_{true};

    std::vector<double> current_positions_;
    std::vector<double> last_commanded_positions_;

    inline double deg2rad(double deg) { return deg * M_PI / 180.0; }
    inline double rad2deg(double rad) { return rad * 180.0 / M_PI; }

    // Polls the Lumi API for current joint states and publishes them
    void pollStatus()
    {
        CURL* curl = curl_easy_init();
        if (!curl) return;

        std::string url = "http://192.168.10.90:5000/api/extaxis/status";
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

        std::string response_string;
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &writeCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            RCLCPP_WARN(this->get_logger(), "Failed HTTP GET");
            curl_easy_cleanup(curl);
            return;
        }

        curl_easy_cleanup(curl);

        // Parse JSON
        try {
            auto j = json::parse(response_string);
            sensor_msgs::msg::JointState msg;
            msg.header.stamp = this->get_clock()->now();

            std::vector<double> new_positions(4, 0.0);
            for (const auto& joint : j) {
                int id = joint["id"];
                if (id < 0 || id >= 4) continue;
                double raw_pos = joint["pos"].get<double>();
                double converted_pos = raw_pos;

                if (id == 0) {
                    converted_pos = raw_pos / 1000.0;  // mm -> meters
                } else {
                    converted_pos = deg2rad(raw_pos);  // degrees -> radians
                }

                msg.name.push_back("l-" + std::to_string(id+1));
                msg.position.push_back(converted_pos);
                msg.velocity.push_back(joint["vel"].get<double>());  // Assuming velocity is in degrees/sec or mm/s, adjust if needed

                new_positions[id] = raw_pos;
            }

            {
                std::lock_guard<std::mutex> lock(mtx_);
                current_positions_ = new_positions;

                RCLCPP_DEBUG(this->get_logger(), 
                    "Read current position: [%.2f mm, %.2f deg, %.2f deg, %.2f deg]",
                    current_positions_[0], current_positions_[1],
                    current_positions_[2], current_positions_[3]);

                // // Initialize last_commanded_positions_ if empty
                // if (previous_positions_.empty()) {
                //     previous_positions_ = new_positions;
                //     RCLCPP_INFO(this->get_logger(), "Initialized previous_positions_ from hardware state.");
                // }
                // else {
                //     std::lock_guard<std::mutex> lock(mtx_);
                //     // Print only if significant change
                //     for (size_t i = 0; i < 4; ++i) {
                //         double delta = std::abs(current_positions_[i] - previous_positions_[i]);
                //         if ((i == 0 && delta > 1.0) || (i > 0 && delta > 1.0)) {  // mm for joint 0, degrees for 1–3
                //             RCLCPP_INFO(this->get_logger(), 
                //                 "Joint %zu changed: old=%.3f, new=%.3f (Δ=%.3f)", 
                //                 i, previous_positions_[i], current_positions_[i], delta);
                //         }
                //     }
                // }
            }

            pub_->publish(msg);

        } catch (const std::exception& e) {
            RCLCPP_WARN(this->get_logger(), "Failed to parse JSON: %s", e.what());
        }
    }

    // // Called whenever sliders in RViz publish new joint_states
    // void jointStateCallback(const sensor_msgs::msg::JointState::SharedPtr msg)
    // {
    //     if (msg->position.size() < 4) {
    //         RCLCPP_WARN(this->get_logger(), "Expected at least 4 joints, got %ld", msg->position.size());
    //         return;
    //     }

    //     std::vector<double> prev_positions;
    //     {
    //         std::lock_guard<std::mutex> lock(mtx_);
    //         prev_positions = current_positions_;
    //     }

    //     bool should_send = false;
    //     std::vector<double> pos_command;

    //     {
    //         std::lock_guard<std::mutex> lock(mtx_);
    //         if (last_commanded_positions_.empty()) {
    //             // We have not yet received hardware positions. Skip until ready.
    //             RCLCPP_WARN(this->get_logger(), "Skipping slider update: hardware state not yet available.");
    //             return;
    //         }
    //         pos_command = last_commanded_positions_;
    //     }


    //     for (size_t i = 0; i < 4; i++) {
    //         double new_val = msg->position[i];
    //         double last_cmd_val = pos_command[i];

    //         if (std::abs(new_val - last_cmd_val) > 1e-3) {
    //             // Check if it's different from current hardware too
    //             if (std::abs(new_val - prev_positions[i]) > 1e-3) {
    //                 pos_command[i] = new_val;
    //                 should_send = true;
    //                 RCLCPP_INFO(this->get_logger(), 
    //                     "Detected change for joint %zu: last commanded=%.5f, new=%.5f, current_hw=%.5f",
    //                     i, last_cmd_val, new_val, current_positions_[i]);
    //                 break;
    //             }
    //         }
    //     }

    //     if (should_send) {
    //         sendMoveTo(pos_command);
    //         {
    //             std::lock_guard<std::mutex> lock(mtx_);
    //             last_commanded_positions_ = pos_command;
    //         }
    //     }
    // }

    void moveService(const std::shared_ptr<jaka_lumi_body_node::srv::MoveService::Request> req,
                     std::shared_ptr<jaka_lumi_body_node::srv::MoveService::Response> res)
    {
        if (req->target.size() != 4) {
            RCLCPP_WARN(this->get_logger(), "Target must have 4 elements.");
            res->success = false;
            return;
        }

        RCLCPP_INFO(this->get_logger(), "Received new target position: [%.2f mm, %.2f deg, %.2f deg, %.2f deg]",
                    req->target[0], req->target[1], req->target[2], req->target[3]);

        {
            std::lock_guard<std::mutex> lock(mtx_);
            RCLCPP_INFO(this->get_logger(), 
                "Current position before move: [%.2f mm, %.2f deg, %.2f deg, %.2f deg]",
                current_positions_[0], current_positions_[1],
                current_positions_[2], current_positions_[3]);
        }

        std::vector<double> cmd(req->target.begin(), req->target.end());
        sendMoveTo(cmd);

        rclcpp::sleep_for(std::chrono::seconds(3));

        std::lock_guard<std::mutex> lock(mtx_);
        bool reached = true;
        for (size_t i = 0; i < 4; ++i) {
            double err = std::abs(current_positions_[i] - cmd[i]);
            if ((i == 0 && err > 0.001) || (i > 0 && err > deg2rad(1.0))) {
                reached = false;
                break;
            }
        }

        res->success = reached;
        if (reached)
            RCLCPP_INFO(this->get_logger(), "Target reached.");
        else
            RCLCPP_WARN(this->get_logger(), "Target not reached. Current pos: [%.3f, %.3f, %.3f, %.3f]",
                current_positions_[0], current_positions_[1], current_positions_[2], current_positions_[3]);
    }

    void sendMoveTo(const std::vector<double>& pos_command)
    {
        // std::vector<double> pos_command_api(4);
        // pos_command_api[0] = pos_command_ros[0] * 1000.0;  // meters -> mm
        // pos_command_api[1] = rad2deg(pos_command_ros[1]); // radians -> degrees
        // pos_command_api[2] = rad2deg(pos_command_ros[2]);
        // pos_command_api[3] = rad2deg(pos_command_ros[3]);

        json j;
        j["pos"] = pos_command;
        j["vel"] = 100;
        j["acc"] = 100;

        std::string payload = j.dump();

        CURL* curl = curl_easy_init();
        if (!curl) return;

        std::string url = "http://192.168.10.90:5000/api/extaxis/moveto";
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());

        struct curl_slist *headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            RCLCPP_WARN(this->get_logger(), "HTTP POST failed");
        } else {
            RCLCPP_INFO(this->get_logger(), "Sent moveto command to Lumi.");
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    void readStatusService(
        const std::shared_ptr<jaka_lumi_body_node::srv::ReadStatusService::Request> /*req*/,
        std::shared_ptr<jaka_lumi_body_node::srv::ReadStatusService::Response> res)
    {
        std::lock_guard<std::mutex> lock(mtx_);
        res->position = {current_positions_[0], current_positions_[1], current_positions_[2], current_positions_[3]};
        RCLCPP_INFO(this->get_logger(), 
            "Read status service called. Current pos: [%.3f, %.3f, %.3f, %.3f]",
            current_positions_[0], current_positions_[1],
            current_positions_[2], current_positions_[3]);
    }

    void stopService(
        const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
        std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/)
    {
        sendSimplePost("/api/extaxis/stop");
        RCLCPP_INFO(this->get_logger(), "Stop command sent.");
    }

    void resetService(
        const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
        std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/)
    {
        sendSimplePost("/api/extaxis/reset");
        RCLCPP_INFO(this->get_logger(), "Reset command sent.");
    }

    void enableService(
        const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
        std::shared_ptr<std_srvs::srv::SetBool::Response> res)
    {
        json j;
        j["enable"] = req->data ? 1 : 0;

        std::string payload = j.dump();

        CURL* curl = curl_easy_init();
        if (!curl) {
            res->success = false;
            return;
        }

        std::string url = "http://192.168.10.90:5000/api/extaxis/enable";
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());

        struct curl_slist *headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode http_res = curl_easy_perform(curl);
        if (http_res != CURLE_OK) {
            res->success = false;
            RCLCPP_WARN(this->get_logger(), "HTTP POST failed");
        } else {
            res->success = true;
            if (req->data)
                RCLCPP_INFO(this->get_logger(), "Enable command sent to Lumi.");
            else
                RCLCPP_INFO(this->get_logger(), "Disable command sent to Lumi.");
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    void sendSimplePost(const std::string& endpoint)
    {
        CURL* curl = curl_easy_init();
        if (!curl) return;

        std::string url = "http://192.168.10.90:5000" + endpoint;
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

        // POST with empty body
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "");

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            RCLCPP_WARN(this->get_logger(), "HTTP POST failed for %s", endpoint.c_str());
        }

        curl_easy_cleanup(curl);
    }

    // libcurl helper
    static size_t writeCallback(void* contents, size_t size, size_t nmemb, void* userp)
    {
        ((std::string*)userp)->append((char*)contents, size * nmemb);
        return size * nmemb;
    }
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<LumiBodyNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
