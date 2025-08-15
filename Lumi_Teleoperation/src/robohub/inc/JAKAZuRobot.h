/**
* @last update Nov 30 2021 
* @Maintenance star@jaka
*/



#ifndef _JAKAAPI_H_
#define _JAKAAPI_H_

#include <stdio.h>
#include <string>
#include <stdint.h>
#include "jkerr.h"
#include "jktypes.h"

#if defined(_WIN32) || defined(WIN32)
/**
 * 低版本Visual Studio需要手动定义__cpluscplus宏
 */
#if __cpluscplus

#ifdef DLLEXPORT_API
#undef DLLEXPORT_API
#endif // DLLEXPORT_API

#ifdef DLLEXPORT_EXPORTS
#define DLLEXPORT_API __declspec(dllexport)
#else // DLLEXPORT_EXPORTS
#define DLLEXPORT_API __declspec(dllimport)
#endif // DLLEXPORT_EXPORTS

#else // __cpluscplus

#define DLLEXPORT_API

#endif // __cpluscplus

#elif defined(__linux__)

#define DLLEXPORT_API __attribute__((visibility("default")))

#else

#define DLLEXPORT_API

#endif // defined(_WIN32) || defined(WIN32)

class DLLEXPORT_API JAKAZuRobot
{
public:
	/**
	* @brief 机械臂控制类构造函数
	*/
	JAKAZuRobot();

	/**
	* @brief 创建机器人控制句柄
	* @param ip  控制器ip地址
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t login_in(const char *ip);

	/**
	* @brief 断开控制器连接
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t login_out();

	/**
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t power_on();

	/**
	* @brief 关闭机器人电源
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t power_off();

	/**
	* @brief 机器人控制柜关机
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t shut_down();

	/**
	* @brief 控制机器人上使能
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t enable_robot();

	/**
	* @brief 控制机器人下使能
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t disable_robot();

	/**
	* @brief 机器人SERVO MOVE模式使能
	* @param enable  TRUE为进入SERVO MOVE模式，FALSE表示退出该模式
	* @param robindex 机器人索引号，-1表示所有机器人
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_enable(BOOL enable, int robindex = 0);

	errno_t edg_servo_j(unsigned char robot_index, const JointValue *joint_pos, MoveMode move_mode, unsigned int step_num=1);
	errno_t edg_servo_p(unsigned char robot_index, const CartesianPose *cartesian_pose, MoveMode move_mode, unsigned int step_num=1);
	errno_t edg_get_stat(unsigned char robot_index, JointValue *joint_pos, CartesianPose *cartesian_pose);
	errno_t edg_stat_details(unsigned long int details[3]);
	errno_t edg_stat_free_key(bool keys[2]);
	errno_t edg_recv(struct timespec *next = nullptr);
	errno_t edg_send();

	/**
	* @brief 控制机器人进入或退出拖拽模式
	* @param enable  TRUE为进入拖拽模式，FALSE为退出拖拽模式
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t drag_mode_enable(int robot_id, BOOL enable);

	/**
	* @brief 查询机器人是否处于拖拽模式
	* @param in_drag 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t is_in_drag_mode(BOOL *in_drag);

	/**
	* @brief 查询机器人是否处于碰撞保护模式
	* @param in_collision 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t is_in_collision(BOOL *in_collision);

	/**
	* @brief 获取机器人状态
	* @param state 机器人状态查询结果, 双臂状态与结果； 即均上电才认为上电，均使能才认为使能
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_robot_state(RobotState *state);

	/**
	* @brief 碰撞之后从碰撞保护模式恢复
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t collision_recover();

	/**
	* @brief  错误状态清除
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t clear_error();

	/**
	* @brief 设置机器人碰撞等级
	* @param level  碰撞等级，等级0-5 ，0为关闭碰撞，1为碰撞阈值25N，2为碰撞阈值50N，3为碰撞阈值75N，4为碰撞阈值100N，5为碰撞阈值125N
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_collision_level(int robot_id, const int level);

	/**
	* @brief 获取机器人设置的碰撞等级
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_collision_level(int robot_id, int *level);

	/**
	* @brief 计算指定位姿在当前工具、当前安装角度以及当前用户坐标系设置下的逆解
	* @param ref_pos 逆解计算用的参考关节空间位置
	* @param cartesian_pose 笛卡尔空间位姿值
	* @param joint_pos 计算成功时关节空间位置计算结果
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t kine_inverse(int robot_id, const JointValue *ref_pos, const CartesianPose *cartesian_pose, JointValue *joint_pos);

	/**
	* @brief 计算指定关节位置在当前工具、当前安装角度以及当前用户坐标系设置下的位姿值
	* @param joint_pos 关节空间位置
	* @param cartesian_pose 笛卡尔空间位姿计算结果
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t kine_forward(int robot_id, const JointValue *joint_pos, CartesianPose *cartesian_pose);


	/**
	* @brief 注册机器人出现错误时的回调函数
	* @param func 指向用户定义的函数的函数指针
	* @param error_code 机器人的错误码
	*/
	errno_t set_error_handler(CallBackFuncType func);

	/**
	* @brief 获取SDK版本号
	* @param version SDK版本号
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_sdk_version(char *version);

	/**
	* @brief 终止当前机械臂运动
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t motion_abort();

	/**
	* @brief 设置错误码文件路径，需要使用get_last_error接口时需要设置错误码文件路径，如果不使用get_last_error接口，则不需要设置该接口
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_errorcode_file_path(char *path);

	/**
	* @brief 获取机器人运行过程中最后一个错误码,当调用clear_error时，最后一个错误码会清零
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_last_error(ErrorCode *code);

	/**
	* @brief 设置是否开启调试模式，选择TRUE时，开始调试模式，此时会在标准输出流中输出调试信息，选择FALSE时，不输出调试信息
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_debug_mode(BOOL mode);

	/**
	* @brief SERVO模式下不使用滤波器,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_use_none_filter();

	/**
	* @brief SERVO模式下关节空间一阶低通滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param cutoffFreq 一阶低通滤波器截止频率
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_use_joint_LPF(double cutoffFreq);

	/**
	* @brief SERVO模式下关节空间非线性滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param max_vr 笛卡尔空间姿态变化速度的速度上限值（绝对值）°/s
	* @param max_ar 笛卡尔空间姿态变化速度的加速度上限值（绝对值）°/s^2
	* @param max_jr 笛卡尔空间姿态变化速度的加加速度上限值（绝对值）°/s^3
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_use_joint_NLF(double max_vr, double max_ar, double max_jr);

	/**
	* @brief SERVO模式下笛卡尔空间非线性滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param max_vp 笛卡尔空间下移动指令速度的上限值（绝对值）。单位：mm/s
	* @param max_ap 笛卡尔空间下移动指令加速度的上限值（绝对值）。单位：mm/s^2
	* @param max_jp 笛卡尔空间下移动指令加加速度的上限值（绝对值）单位：mm/s^3
	* @param max_vr 笛卡尔空间姿态变化速度的速度上限值（绝对值）°/s
	* @param max_ar 笛卡尔空间姿态变化速度的加速度上限值（绝对值）°/s^2
	* @param max_jr 笛卡尔空间姿态变化速度的加加速度上限值（绝对值）°/s^3
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_use_carte_NLF(double max_vp, double max_ap, double max_jp, double max_vr, double max_ar, double max_jr);

	/**
	* @brief SERVO模式下关节空间多阶均值滤波器,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param max_buf 均值滤波器缓冲区的大小
	* @param kp 加速度滤波系数
	* @param kv 速度滤波系数
	* @param ka 位置滤波系数
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_move_use_joint_MMF(int max_buf, double kp, double kv, double ka);

	/**
	* @brief SERVO模式下速度前瞻参数设置
	* @param max_buf 缓冲区的大小
	* @param kp 加速度滤波系数
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t servo_speed_foresight(int max_buf, double kp);

	/**
	* @brief 设置SDK日志路径
	* @param filepath SDK日志路径
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_SDK_filepath(const char *filepath);

	/**
	* @brief 同set_SDK_filepath
	*/
	static errno_t static_Set_SDK_filepath(const char *filepath);

	/**
	* @brief 设置网络异常，SDK与机器人控制器失去连接后多长时间机器人控制器终止机械臂当前运动
	* @param millisecond 时间参数，单位毫秒
	* @param mnt 网络异常时机器人需要进行的动作类型
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_network_exception_handle(float millisecond, ProcessType mnt);

	/**
	* @brief 设置机器人状态数据自动更新时间间隔
	* @param millisecond 时间参数，单位毫秒
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_status_data_update_time_interval(float millisecond);

	/**
	* @brief 设置机器人阻塞等待超时时间
	* @param seconds 时间参数，单位秒
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_block_wait_timeout(float seconds);

	/**
	* @brief 与控制器建立ftp链接
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t init_ftp_client();

	/**
	* @brief 与控制器建立加密ftp链接(需要app登录且控制器版本支持)
	* @param password 机器人登陆密码
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t init_ftp_client_with_ssl(char* password);

	/**
	* @brief 断开与控制器ftp链接
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t close_ftp_client();
	/**
	* @brief 从控制器下载指定类型和名称的文件到本地
	* @param remote 控制器内部文件名绝对路径
	* @param local 下载到本地文件名绝对路径
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t download_file(char* local, char* remote, int opt);

	/**
	* @brief 从控制器上传指定类型和名称的文件到本地
	* @param remote 上传到控制器内部文件名绝对路径
	* @param local 本地文件名绝对路径
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t upload_file(char* local, char* remote, int opt);


	/**
	* @brief 从控制器删除指定类型和名称的文件
	* @param remote 控制器内部文件名
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t del_ftp_file(char* remote, int opt);

	/**
	* @brief 重命名控制器指定类型和名称的文件
	* @param remote 控制器内部文件名原名称
	* @param des 重命名的目标名
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t rename_ftp_file(char* remote, char* des, int opt);

	/**
	* @brief 查询控制器目录
	* @param remotedir 控制器内部文件夹名称
	* @param type 0文件和文件夹 1文件 2文件夹
	* @param ret 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_ftp_dir(const char* remotedir, int type, char* ret);

	/**
	* @brief 设置7轴全运动学参数补偿, 一组机器人同时生效
	* @param flag 1： 补偿；0：不补偿
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_full_dh_flag(int flag);

	/**
	* @brief 设置重力相对机器人基座的方向, 一组机器人同时生效
	* @param rpy rpy旋转角；T = rotx(rpy[0]) * roty(rpy[1]) * rotz(rpy[2])
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t set_gravity_direction(const double* rpy);

	/**
	* @brief 读取重力相对机器人基座的方向
	* @param rpy rpy旋转角；T = rotx(rpy[0]) * roty(rpy[1]) * rotz(rpy[2])
	* @return ERR_SUCC 成功 其他失败
	*/
	errno_t get_gravity_direction(double* rpy);

	/// @brief 多机器人同步运动指令
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param move_mode ABS(绝对运动) or INCR（相对运动）
	/// @param is_block TRUE(阻塞运动) or FALSE(非阻塞运动)
	/// @param joint_pos 两个机器人的位置指令
	/// @param vel 两个机器人速度指令
	/// @param acc 两个机器人的加速度指令
	/// @return 
    errno_t robot_run_multi_movj(int robot_id, const MoveMode *move_mode, BOOL is_block, const JointValue *joint_pos, const double* vel, const double* acc);

	/// @brief 多机器人同步运动指令
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param move_mode ABS(绝对运动) or INCR（相对运动）
	/// @param is_block TRUE(阻塞运动) or FALSE(非阻塞运动)
	/// @param end_pos 两个机器人的位置指令
	/// @param vel 两个机器人速度指令
	/// @param acc 两个机器人的加速度指令
	/// @return 
    errno_t robot_run_multi_movl(int robot_id, const MoveMode *move_mode, BOOL is_block, const CartesianPose* end_pos, const double* vel, const double* acc);


    /// @brief 获取两个机器人的DH参数
    /// @param dh_param dh参数， 2维
    /// @return 
    errno_t robot_get_multi_robot_dh(DHParam *dh_param);

    /// @brief 获取两个机器人是否到位
    /// @param inpos 1 到位； 0 未到位； 2维
    /// @return 
    errno_t robot_is_inpos(int* inpos);

    /// @brief 设置机器人末端工具负载
    /// @param robot_id  机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1)
    /// @param payload 机器人负载参数， 2维
    /// @return 
    errno_t robot_set_tool_payload(int robot_id, const PayLoad* payload);

    errno_t robot_get_tool_payload(PayLoad* payload);

	/// @brief 设置传感器灵敏度接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-20
	/// @param deadzone_percent 传感器灵敏度死区占默认最大死区的百分比，数据范围0-1
	/// @return 
    errno_t robot_set_ftsensor_deadzone(int robot_id, int sensor_id, const double* deadzone_percent);

    errno_t robot_get_ftsensor_deadzone(int robot_id, int sensor_id, double* deadzone_percent);

    errno_t robot_get_cst_ftframe(int robot_id, int* ftframe);

	/// @brief 设置力控坐标系接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param ftframe 力控坐标系 接受工具(0) 世界(1)
	/// @return 
    errno_t robot_set_cst_ftframe(int robot_id, int ftframe);

	/// @brief 设置恒力柔顺参数接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param axis 要设置的方向，数据范围0-5，依次代表x,y,z,rx,ry,rz
	/// @param enable 是否开启力控，接受关(0) 开(1)
	/// @param ftUser 力控刚度，需为正数，请勿设置为0，一般建议x,y,z设置10以上的数值，mx,my,mz设置1以上的数值
	/// @param ftReboundFK 回弹弹力系数，需为正数，可以设置为0
	/// @param ftConstant 目标力，请勿设置超出机器人承受范围的目标力
	/// @return 
    errno_t robot_set_cst_ftconfig(int robot_id, int axis, int enable, double ftUser, double ftReboundFK, double ftConstant);

    errno_t robot_get_cst_ftconfig(int robot_id, RobotAdmitCtrl* config);

	/// @brief 开启恒力柔顺控制接口，恒力柔顺控制可以配合直线或关节运动以及笛卡尔伺服运动模式使用，不可以配合拖拽模式或手动示教JOG使用
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @return 
    errno_t robot_enable_force_control(int robot_id);

	/// @brief 关闭恒力柔顺控制接口，注意关闭力控将使力控立即失效但不会退出力控模式
	/// 直至机器人执行完成当前运动（或退出伺服运动模式）后力控模式才会真正退出，因此在此期间无法再次开启力控
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @return 
    errno_t robot_disable_force_control(int robot_id);

	/// @brief 传感器校零接口，注意校零需要约1秒的时间，期间无法开启力控，固建议调用此接口后等待1秒。
	/// 一般建议在开启力控前都进行一次传感器校零，注意校零时传感器不要受到除负载重力以外的任何外力。
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @return
    errno_t robot_zero_ftsensor(int robot_id, int sensor_id);

	/// @brief 设置传感器负载接口，注意传感器负载与机器人负载可以不同（也可以相同），需要单独设置
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param payload 负载数据，单位kg，mm
	/// @return
    errno_t robot_set_ftsensor_payload(int robot_id, int sensor_id, PayLoad payload);

    errno_t robot_get_ftsensor_payload(int robot_id, int sensor_id, PayLoad* payload);

	/// @brief 设置传感器数据平滑滤波器截止频率
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1)
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param filter 截止频率，需为正数，单位Hz
	/// @return
    errno_t robot_set_ftsensor_filter(int robot_id, int sensor_id, double filter);

    errno_t robot_get_ftsensor_filter(int robot_id, int sensor_id, double* filter);

	/// @brief 获取力控模式状态，注意当调用disable_force_control后但机器人尚未完成当前运动期间力控模式仍被视作开启状态
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1)
	/// @param force_control_stat 0代表关闭，1代表开启
	/// @return
    errno_t robot_get_force_control_stat(int robot_id, int* force_control_stat);

	/// @brief 获取传感器状态
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1)
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param status 正常(1) 错误(-1)
	/// @param errcode 无数据(1) 数据错误(2) 过载(4)
	/// @param ft_original 传感器在自身坐标系下的原始读数
	/// @param ft_actual 传感器在法兰坐标系下的经过负载和零点补偿后的读数
	/// @return 
    errno_t robot_get_ftsensor_stat(int robot_id, int sensor_id, int* status, int* errcode, double* ft_original, double* ft_actual);

	/**
	 * @brief 设置关节的控制环参数
	 * @param robot_id 机器人ID 接受LEFT(0) RIGHT(1)
	 * @param joint_id 关节ID
	 * @param pos_kp 位置环比例增益,推荐30， 范围0~100.参数越大，位置环越刚，该参数设置过大会导致机器人出现振动，建议在默认值附近调整
	 * @param vel_kp 速度环比列增益,推荐50， 范围0~200.参数越大，速度环越刚，该参数设置过大会导致机器人出现振动，建议在默认值附近调整
	 * @param vel_ti 速度环积分常数,推荐2000， 范围500~16777216.参数越大，积分作用越弱，该参数设置过小会导致速度超调甚至失稳，建议在默认值附近调整
	 * @note 当且仅当开启controlloop时才有效。关闭controlloop后，参数会被重置为内部默认值
	 * @note 仅支持3.0.3_ZY1及其以上版本
	 */
	errno_t set_joint_controlloop(int robot_id, int joint_id, uint32_t pos_kp, uint32_t vel_kp, uint32_t vel_ti);

	/**
	 * @brief 开启或关闭关节的控制环参数
	 * @param robot_id 机器人ID 接受LEFT(0) RIGHT(1)
	 * @param joint_id 关节ID
	 * @param en 是否开启控制环参数
	 * @note 关闭controlloop后，控制环参数会被重置为内部默认值
	 * @note 仅支持3.0.3_ZY1及其以上版本
	 */
	errno_t enable_joint_controlloop(int robot_id, int joint_id, bool en);
	
    /// @brief 查詢机器人当前是否超出软限位 
    /// @param robot_id 接受LEFT(0) RIGHT(1)
    /// @param limit 0 代表无超出，1代表超出
    /// @return 
    errno_t robot_is_on_soft_limit(int robot_id, int* limit);

	/// @brief 确认机器人是否处于错误状态
	/// @param in_error 0 代表机器人处于正常状态，1代表机器人处于错误状态
	/// @return 
    errno_t robot_is_in_error(int* in_error);

    errno_t robot_set_tool_offset(int robot_id, CartesianPose tool);

    errno_t robot_get_tool_offset(int robot_id, CartesianPose* offset);

    errno_t robot_get_default_base(int robot_id, CartesianPose* base_offset);

    errno_t ext_power_on();

    errno_t ext_power_off();

    errno_t ext_enable_on();

    errno_t ext_enable_off();

    errno_t ext_jog_to(int slave_id, int pos, double vel, double acc);

    errno_t ext_servo_home(int robot_id);

    errno_t ext_get_status(int slave_id, ExtStatus&);

	~JAKAZuRobot();

private:
	class BIFClass;
	BIFClass *ptr;
};


#undef DLLEXPORT_API
#endif
