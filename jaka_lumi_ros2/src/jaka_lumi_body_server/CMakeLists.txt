cmake_minimum_required(VERSION 3.8)
project(jaka_lumi_body_server)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(control_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# Find libcurl
find_package(CURL REQUIRED)

# Create executable
add_executable(lumi_body_server
  src/lumi_body_server.cpp
)

# Add include paths for external header-only libraries like nlohmann_json
target_include_directories(lumi_body_server PUBLIC
  /usr/include
)

target_link_libraries(lumi_body_server
  CURL::libcurl
)

# Link dependencies
ament_target_dependencies(lumi_body_server
  rclcpp
  rclcpp_action
  control_msgs
  sensor_msgs
  std_msgs
  std_srvs
)

# Install
install(TARGETS lumi_body_server
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files, if any (optional)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
