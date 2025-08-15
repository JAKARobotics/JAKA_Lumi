/**
* @last update Nov 30 2021 
* @Maintenance star@jaka
*/

#ifndef _JAKA_API_
#define _JAKA_API_

#include "jkerr.h"
#include "jktypes.h"

#if defined(_WIN32) || defined(WIN32)
/**
 * 低版本Visual Studio需要手动定义__cpluscplus宏
 */
#ifdef __cpluscplus

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

#ifdef __cpluscplus
extern "C"
{
#endif // __cpluscplus

	/**
	* @brief 创建机器人控制句柄
	* @param ip  控制器ip地址
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t create_handler(const char *ip, JKHD *handle);

	/**
	* @brief 断开控制器连接
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t destory_handler(const JKHD *handle);

	/**
	* @brief 打开机器人电源
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t power_on(const JKHD *handle);

	/**
	* @brief 关闭机器人电源
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t power_off(const JKHD *handle);

	/**
	* @brief 机器人控制柜关机
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t shut_down(const JKHD *handle);

	/**
	* @brief 控制机器人上使能
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t enable_robot(const JKHD *handle);

	/**
	* @brief 控制机器人下使能
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t disable_robot(const JKHD *handle);

	/**
	* @brief 控制机器人手动模式下运动
	* @param handle  机器人控制句柄
	* @param aj_num 1_based标识值，在关节空间下代表关节号，笛卡尔下依次为x，y，z，rx，ry，rz
	* @param move_mode 机器人运动模式，增量运动、绝对运动或者连续运动
	* @param coord_type 机器人运动坐标系，工具坐标系，基坐标系（当前的世界/用户坐标系）或关节空间
	* @param vel_cmd 指令速度，旋转轴或关节运动单位为rad/s，移动轴单位为mm/s
	* @param pos_cmd 指令位置，旋转轴或关节运动单位为rad，移动轴单位为mm
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t jog(const JKHD *handle, int aj_num, MoveMode move_mode, CoordType coord_type, double vel_cmd, double pos_cmd);

	/**
	* @brief 控制机器人手动模式下运动停止
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t jog_stop(const JKHD *handle, int num);

	/**
	* @brief 机器人关节运动
	* @param handle  机器人控制句柄
	* @param joint_pos 机器人关节运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE为阻塞接口 FALSE为非阻塞接口
	* @param speed 机器人关节运动速度，单位：rad/s
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t joint_move(const JKHD *handle, const JointValue *joint_pos, MoveMode move_mode, BOOL is_block, double speed);

	/**
	* @brief 机器人关节运动
	* @param joint_pos 机器人关节运动目标位置
	* @move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE为阻塞接口 FALSE为非阻塞接口
	* @param speed 机器人关节运动速度，单位：rad/s
	* @param acc 机器人关节运动角加速度,单位：rad/s^2
	* @param tol 机器人关节运动终点误差,单位：mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t joint_move_extend(const JKHD *handle, const JointValue *joint_pos, MoveMode move_mode, BOOL is_block, double speed, double acc, double tol, const OptionalCond *option_cond);

	/**
	* @brief 机器人末端直线运动
	* @param handle  机器人控制句柄
	* @param end_pos 机器人末端运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人直线运动速度，单位：mm/s
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t linear_move(const JKHD *handle, const CartesianPose *end_pos, MoveMode move_mode, BOOL is_block, double speed);

	/**
	* @brief 机器人末端直线运动
	* @param end_pos 机器人末端运动目标位置
	* @move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人直线运动速度，单位：mm/s
	* @param acc 机器人直线运动加速度,单位mm/s^2
	* @param tol 机器人直线运动终点误差, 单位mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t linear_move_extend(const JKHD *handle, const CartesianPose *end_pos, MoveMode move_mode, BOOL is_block, double speed, double accel, double tol, const OptionalCond *option_cond);
	
	/**
	* @brief 机器人末端直线运动
	* @param end_pos 机器人末端运动目标位置
	* @move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人直线运动速度，单位：mm/s
	* @param acc 机器人直线运动加速度,单位mm/s^2
	* @param tol 机器人直线运动终点误差, 单位mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @param ori_vel 姿态速度,单位rad/s
	* @param ori_acc 姿态加速度,单位rad/s^2
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t linear_move_extend_ori(const JKHD *handle, const CartesianPose *end_pos, MoveMode move_mode, BOOL is_block, double speed, double accel, double tol, const OptionalCond *option_cond, double ori_vel, double ori_acc);

	/**
	* @brief 机器人末端圆弧运动
	* @param end_pos 机器人末端运动目标位置
	* @param mid_pos 机器人末端运中间点
	* @move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人圆弧速度，单位：rad/s
	* @param acc 机器人圆弧运动加速度，单位：rad/s^2
	* @param tol 机器人关节运动终点误差, 单位mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t circular_move(const JKHD *handle, const CartesianPose *end_pos, const CartesianPose *mid_pos, MoveMode move_mode, BOOL is_block, double speed, double accel, double tol, const OptionalCond *option_cond);

	/**
	* @brief 机器人末端圆弧运动
	* @param end_pos 机器人末端运动目标位置
	* @param mid_pos 机器人末端运中间点
	* @param move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人圆弧速度，单位：rad/s
	* @param acc 机器人圆弧运动加速度，单位：rad/s^2
	* @param tol 机器人关节运动终点误差, 单位mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @param circle_cnt 指定机器人圆弧运动圈数。为0时等价于circular_move
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t circular_move_extend(const JKHD *handle, const CartesianPose *end_pos, const CartesianPose *mid_pos, MoveMode move_mode, BOOL is_block, double speed, double accel, double tol, const OptionalCond *option_cond, int circle_cnt);

	/**
	* @brief 机器人末端圆弧运动
	* @param end_pos 机器人末端运动目标位置
	* @param mid_pos 机器人末端运中间点
	* @param move_mode 指定运动模式：增量运动(相对运动)或绝对运动
	* @param is_block 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口
	* @param speed 机器人圆弧速度，单位：rad/s
	* @param acc 机器人圆弧运动加速度，单位：rad/s^2
	* @param tol 机器人关节运动终点误差, 单位mm
	* @param option_cond 机器人关节可选参数，如果不需要，该值可不赋值,填入空指针就可
	* @param circle_cnt 指定机器人圆弧运动圈数。为0时等价于circular_move
	* @param circle_mode 指定机器人圆弧运动模式，参数解释如下：
	- 0：固定采用起始姿态到终止姿态旋转角度小于180°的轴角进行姿态变化；(当前方案)
	- 1：固定采用起始姿态到终止姿态旋转角度大于180°的轴角进行姿态变化；
	- 2：根据中间点姿态自动选择选择角度小于180°还是大于180°；
	- 3： 姿态夹角与圆弧轴线始终保持一致。(当前整圆运动)
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t circular_move_extend_mode(const JKHD *handle, const CartesianPose *end_pos, const CartesianPose *mid_pos, MoveMode move_mode, BOOL is_block, double speed, double accel, double tol, const OptionalCond *option_cond, int circle_cnt, int circle_mode);


	/**
	* @brief 机器人SERVO MOVE模式使能
	* @param handle  机器人控制句柄
	* @param enable  TRUE为进入SERVO MOVE模式，FALSE表示退出该模式
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_enable(const JKHD *handle, BOOL enable);

	/**
	* @brief 机器人关节空间位置控制模式
	* @param handle  机器人控制句柄
	* @param joint_pos 机器人关节运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @return ERR_SUCC成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_j(const JKHD *handle, const JointValue *joint_pos, MoveMode move_mode);

	/**
	* @brief 机器人关节空间位置控制模式
	* @param handle  机器人控制句柄
	* @param joint_pos 机器人关节运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @step_num  倍分周期，servo_j运动周期为step_num*8ms，其中step_num>=1
	* @return ERR_SUCC成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_j_extend(const JKHD *handle, const JointValue *joint_pos, MoveMode move_mode, unsigned int step_num);

	/**
	* @brief 机器人笛卡尔空间位置控制模式
	* @param handle  机器人控制句柄
	* @param cartesian_pose 机器人笛卡尔空间运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_p(const JKHD *handle, const CartesianPose *cartesian_pose, MoveMode move_mode);

	/**
	* @brief 机器人笛卡尔空间位置控制模式
	* @param handle  机器人控制句柄
	* @param cartesian_pose 机器人笛卡尔空间运动目标位置
	* @move_mode 指定运动模式：增量运动或绝对运动
	* @step_num  倍分周期，servo_p运动周期为step_num*8ms，其中step_num>=1
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_p_extend(const JKHD *handle, const CartesianPose *cartesian_pose, MoveMode move_mode, unsigned int step_num);

	/**
	* @brief 设置数字输出变量(DO)的值
	* @param handle 机器人控制句柄
	* @param type DO类型
	* @param index DO索引
	* @param value DO设置值
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_digital_output(const JKHD *handle, IOType type, int index, BOOL value);

	/**
	* @brief 设置模拟输出变量的值(AO)的值
	* @param handle 机器人控制句柄
	* @param type AO类型
	* @param index AO索引
	* @param value AO设置值
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_analog_output(const JKHD *handle, IOType type, int index, float value);

	/**
	* @brief 查询数字输入(DI)状态
	* @param handle 机器人控制句柄
	* @param type DI类型
	* @param index DI索引
	* @param result DI状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_digital_input(const JKHD *handle, IOType type, int index, BOOL *result);

	/**
	* @brief 查询数字输出(DO)状态
	* @param handle 机器人控制句柄
	* @param type DO类型
	* @param index DO索引
	* @param result DO状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_digital_output(const JKHD *handle, IOType type, int index, BOOL *result);

	/**
	* @brief 获取模拟量输入变量(AI)的值
	* @param handle 机器人控制句柄
	* @param type AI的类型
	* @param index AI索引
	* @param result 指定AI状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_analog_input(const JKHD *handle, IOType type, int index, float *result);

	/**
	* @brief 获取模拟量输出变量(AO)的值
	* @param handle 机器人控制句柄
	* @param type AO的类型
	* @param index AO索引
	* @param result 指定AO状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_analog_output(const JKHD *handle, IOType type, int index, float *result);

	/**
	* @brief 查询扩展IO模块是否运行
	* @param handle 机器人控制句柄
	* @param is_running 扩展IO模块运行状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t is_extio_running(const JKHD *handle, BOOL *is_running);

	/**
	* @brief 运行当前加载的作业程序
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t program_run(const JKHD *handle);

	/**
	* @brief 暂停当前运行的作业程序
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t program_pause(const JKHD *handle);

	/**
	* @brief 继续运行当前暂停的作业程序
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t program_resume(const JKHD *handle);

	/**
	* @brief 终止当前执行的作业程序
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t program_abort(const JKHD *handle);

	/**
	* @brief 加载指定的作业程序
	* @param handle 机器人控制句柄
	* @param file 程序文件路径
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t program_load(const JKHD *handle, const char *file);

	/**
	* @brief 获取已加载的作业程序路径
	* @param handle 机器人控制句柄
	* @param file 程序文件路径
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_loaded_program(const JKHD *handle, char *file);

	/**
	* @brief 获取当前机器人作业程序的执行行号
	* @param handle  机器人控制句柄
	* @param curr_line 当前行号查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_current_line(const JKHD *handle, int *curr_line);

	/**
	* @brief 获取机器人作业程序执行状态
	* @param handle  机器人控制句柄
	* @param status 作业程序执行状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_program_state(const JKHD *handle, ProgramState *status);

	/**
	* @brief 设置机器人运行倍率
	* @param handle  机器人控制句柄
	* @param rapid_rate 是程序运行倍率，设置范围为[0,1]
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_rapidrate(const JKHD *handle, double rapid_rate);

	/**
	* @brief 获取机器人运行倍率
	* @param handle 机器人控制句柄
	* @param rate 当前控制系统倍率
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_rapidrate(const JKHD *handle, double *rapid_rate);

	/**
	* @brief 设置指定编号的工具信息
	* @param handle 机器人控制句柄
	* @param id 工具编号
	* @param tcp 工具坐标系相对法兰坐标系偏置
	* @param name 指定工具的别名
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_tool_data(const JKHD *handle, int id, const CartesianPose *tcp, const char *name);

	/**
	* @brief 设置当前使用的工具ID
	* @param handle  机器人控制句柄
	* @param id 工具坐标系ID
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_tool_id(const JKHD *handle, const int id);

	/**
	* @brief 查询当前使用的工具ID
	* @param handle  机器人控制句柄
	* @param id 工具ID查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_tool_id(const JKHD *handle, int *id);

	/**
	* @brief 查询使用的工具信息
	* @param id 工具ID查询结果
	* @param tcp 工具坐标系相对法兰坐标系偏置
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_tool_data(const JKHD *handle, int id, CartesianPose *tcp);

	/**
	* @brief 设置指定编号的用户坐标系信息
	* @param handle 机器人控制句柄
	* @param id 用户坐标系编号
	* @param user_frame 用户坐标系偏置值
	* @param name 用户坐标系别名
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_user_frame_data(const JKHD *handle, int id, const CartesianPose *user_frame, const char *name);

	/**
	* @brief 设置当前使用的用户坐标系ID
	* @param handle  机器人控制句柄
	* @param id 用户坐标系ID
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_user_frame_id(const JKHD *handle, const int id);

	/**
	* @brief 查询当前使用的用户坐标系ID
	* @param handle  机器人控制句柄
	* @param id 获取的结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_user_frame_id(const JKHD *handle, int *id);

	/**
	* @brief 查询使用的用户坐标系信息
	* @param id 用户坐标系ID查询结果
	* @param tcp 用户坐标系偏置值
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_user_frame_data(const JKHD *handle, int id, CartesianPose *tcp);

	/**
	* @brief 控制器机器人进入或退出拖拽模式
	* @param handle  机器人控制句柄
	* @param enable  TRUE为进入拖拽模式，FALSE为退出拖拽模式
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t drag_mode_enable(const JKHD *handle, int robot_id, BOOL enable);

	/**
	* @brief 查询机器人是否处于拖拽模式
	* @param handle  机器人控制句柄
	* @param in_drag 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t is_in_drag_mode(const JKHD *handle, BOOL *in_drag);

	/**
	* @brief 获取机器人状态
	* @param handle  机器人控制句柄
	* @param state 机器人状态查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_robot_state(const JKHD *handle, RobotState *state);

	/**
	* @brief 获取当前设置下工具末端的位姿
	* @param handle  机器人控制句柄
	* @param tcp_position 工具末端位置查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_tcp_position(const JKHD *handle, CartesianPose *tcp_position);

	/**
	* @brief 获取当前设置下工具末端的位姿
	* @param handle  机器人控制句柄
	* @param tcp_position 工具末端位置查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_joint_position(const JKHD *handle, JointValue *joint_position);

	/**
	* @brief 查询机器人是否处于碰撞保护模式
	* @param handle  机器人控制句柄
	* @param in_collision 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t is_in_collision(const JKHD *handle, BOOL *in_collision);

	/**
	* @brief 查询机器人是否超出限位
	* @param handle  机器人控制句柄
	* @param on_limit 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t is_on_limit(const JKHD *handle, BOOL *on_limit);

	/**
	* @brief 查询机器人运动是否停止
	* @param handle  机器人控制句柄
	* @param in_pos 查询结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t is_in_pos(const JKHD *handle, BOOL *in_pos);

	/**
	 * @brief 设置机器人运动判断inpos的阈值，默认为0.003rad
	 * @param handle 机器人控制句柄
	 * @param thresholding 当关节角运动低于该值时，in_pos返回为1
	 * @param ERR_SUCC 成功
	 */
	DLLEXPORT_API errno_t set_in_pos_thresholding(const JKHD *handle, const double thresholding);

	/**
	 * @brief 获取机器人运动判断inpos的阈值，默认为0.003rad
	 * @param handle 机器人控制句柄
	 * @param thresholding 查询结果
	 * @param ERR_SUCC 成功
	 */
	DLLEXPORT_API errno_t get_in_pos_thresholding(const JKHD *handle, double *thresholding);

	/**
	* @brief 碰撞之后从碰撞保护模式恢复
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t collision_recover(const JKHD *handle);

	/**
	* @brief  错误状态清除
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t clear_error(const JKHD *handle);

	/**
	* @brief 设置机器人碰撞等级
	* @param handle  机器人控制句柄
	* @param level  碰撞等级，等级0-5 ，0为关闭碰撞，1为碰撞阈值25N，2为碰撞阈值50N，3为碰撞阈值75N，4为碰撞阈值100N，5为碰撞阈值125N
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_collision_level(const JKHD *handle, int robot_id, const int level);

	/**
	* @brief 碰撞之后从碰撞保护模式恢复
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_collision_level(const JKHD *handle, int robot_id, int *level);

	/**
	* @brief 计算指定位姿在当前工具、当前安装角度以及当前用户坐标系设置下的逆解
	* @param handle  机器人控制句柄
	* @param ref_pos 逆解计算用的参考关节空间位置
	* @param cartesian_pose 笛卡尔空间位姿值
	* @param joint_pos 计算成功时关节空间位置计算结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t kine_inverse(const JKHD *handle, int robot_id, const JointValue *ref_pos, const CartesianPose *cartesian_pose, JointValue *joint_pos);

	/**
	* @brief 计算指定关节位置在当前工具、当前安装角度以及当前用户坐标系设置下的位姿值
	* @param handle  机器人控制句柄
	* @param joint_pos 关节空间位置
	* @param cartesian_pose 笛卡尔空间位姿计算结果
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t kine_forward(const JKHD *handle, int robot_id, const JointValue *joint_pos, CartesianPose *cartesian_pose);


	/**
	* @brief 获取SDK版本号
	* @param handle  机器人控制句柄
	* @param version SDK版本号
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_sdk_version(const JKHD *handle, char *version);

	/**
	* @brief 终止当前机械臂运动
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t motion_abort(const JKHD *handle);

	/**
	* @brief 设置错误码文件路径，需要使用get_last_error接口时需要设置错误码文件路径，如果不使用get_last_error接口，则不需要设置该接口（使用英文路径）
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_errorcode_file_path(const JKHD *handle, char *path);

	/**
	* @brief 获取机器人运行过程中最后一个错误码,当调用clear_error时，最后一个错误码会清零
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_last_error(const JKHD *handle, ErrorCode *code);

	/**
	* @brief 设置是否开启调试模式，选择TRUE时，开始调试模式，此时会在标准输出流中输出调试信息，选择FALSE时，不输出调试信息
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_debug_mode(const JKHD *handle, BOOL mode);

	/**
	* @brief SERVO模式下不使用滤波器,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param handle  机器人控制句柄
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_use_none_filter(const JKHD *handle);

	/**
	* @brief SERVO模式下关节空间一阶低通滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param handle  机器人控制句柄
	* @param cutoffFreq 一阶低通滤波器截止频率
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_use_joint_LPF(const JKHD *handle, double cutoffFreq);

	/**
	* @brief SERVO模式下关节空间非线性滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param handle  机器人控制句柄
	* @param max_vr 笛卡尔空间姿态变化速度的速度上限值（绝对值）°/s
	* @param max_ar 笛卡尔空间姿态变化速度的加速度上限值（绝对值）°/s^2
	* @param max_jr 笛卡尔空间姿态变化速度的加加速度上限值（绝对值）°/s^3
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_use_joint_NLF(const JKHD *handle, double max_vr, double max_ar, double max_jr);

	/**
	* @brief SERVO模式下笛卡尔空间非线性滤波,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param handle  机器人控制句柄
	* @param max_vp 笛卡尔空间下移动指令速度的上限值（绝对值）。单位：mm/s
	* @param max_ap 笛卡尔空间下移动指令加速度的上限值（绝对值）。单位：mm/s^2
	* @param max_jp 笛卡尔空间下移动指令加加速度的上限值（绝对值）单位：mm/s^3
	* @param max_vr 笛卡尔空间姿态变化速度的速度上限值（绝对值）°/s
	* @param max_ar 笛卡尔空间姿态变化速度的加速度上限值（绝对值）°/s^2
	* @param max_jr 笛卡尔空间姿态变化速度的加加速度上限值（绝对值）°/s^3
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_use_carte_NLF(const JKHD *handle, double max_vp, double max_ap, double max_jp, double max_vr, double max_ar, double max_jr);

	/**
	* @brief SERVO模式下关节空间多阶均值滤波器,该指令在SERVO模式下不可设置，退出SERVO后可设置
	* @param handle  机器人控制句柄
	* @param max_buf 均值滤波器缓冲区的大小
	* @param kp 加速度滤波系数
	* @param kv 速度滤波系数
	* @param ka 位置滤波系数
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_move_use_joint_MMF(const JKHD *handle, int max_buf, double kp, double kv, double ka);

	/**
	* @brief SERVO模式下速度前瞻参数设置
	* @param handle  机器人控制句柄
	* @param max_buf 缓冲区的大小
	* @param kp 加速度滤波系数
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t servo_speed_foresight(const JKHD *handle, int max_buf, double kp);

	/**
	* @brief 设置SDK日志路径
	* @param handle  机器人控制句柄
	* @param filepath SDK日志路径
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_SDK_filepath(const JKHD *handle, char *filepath);

	/**
	* @brief 设置网络异常，SDK与机器人控制器失去连接后多长时间机器人控制器终止机械臂当前运动
	* @param handle  机器人控制句柄
	* @param millisecond 时间参数，单位毫秒
	* @param mnt 网络异常时机器人需要进行的动作类型
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_network_exception_handle(const JKHD *handle, float millisecond, ProcessType mnt);

	/**
	* @brief 设置机器人状态数据自动更新时间间隔
	* @param handle  机器人控制句柄
	* @param millisecond 时间参数，单位毫秒
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_status_data_update_time_interval(const JKHD *handle, float millisecond);

	/**
	* @brief 设置机器人阻塞等待超时时间
	* @param seconds 时间参数，单位秒
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_block_wait_timeout(const JKHD* handle, float seconds);


	/**
	* @brief 获取机器人DH参数
	* @param dhParam DH参数
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_dh_param(const JKHD *handle, DHParam *dhParam);

	/**
	* @brief 与控制器建立ftp链接
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t init_ftp_client(const JKHD *handle);

	/**
	* @brief 与控制器建立加密ftp链接(需要app登录且控制器版本支持)
	* @param password 机器人登陆密码
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t init_ftp_client_with_ssl(const JKHD* handle, char* password);


	/**
	* @brief 断开与控制器ftp链接
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t close_ftp_client(const JKHD *handle);
	/**
	* @brief 从控制器下载指定类型和名称的文件到本地
	* @param remote 控制器内部文件名绝对路径
	* @param local 下载到本地文件名绝对路径
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t download_file(const JKHD *handle, char *local, char *remote, int opt);

	/**
	* @brief 从控制器上传指定类型和名称的文件到本地
	* @param remote 控制器内部文件名绝对路径
	* @param local 下载到本地文件名绝对路径
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t upload_file(const JKHD *handle, char *local, char *remote, int opt);

	/**
	* @brief 从控制器删除指定类型和名称的文件
	* @param remote 控制器内部文件名
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t del_ftp_file(const JKHD *handle, char *remote, int opt);

	/**
	* @brief 重命名控制器指定类型和名称的文件
	* @param remote 控制器内部文件名原名称
	* @param des 重命名的目标名
	* @param opt 1单个文件 2文件夹
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t rename_ftp_file(const JKHD *handle, char *remote, char *des, int opt);

	/**
	* @brief 获取ftp文件列表
	* @param remotedir 查询列表 
	* @param type 1单个文件 2文件夹
	* @param ret 返回字符串
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_ftp_dir(const JKHD *handle, const char *remotedir, int type, char *ret);

	/**
	* @brief 设置7轴全运动学参数补偿
	* @param flag 1： 补偿；0：不补偿
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_full_dh_flag(const JKHD *handle, int flag);

	/**
	* @brief 设置重力相对机器人基座的方向
	* @param rpy rpy旋转角；T = rotx(rpy[0]) * roty(rpy[1]) * rotz(rpy[2])
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t set_gravity_direction(const JKHD *handle, const double* rpy);

	/**
	* @brief 读取重力相对机器人基座的方向
	* @param rpy rpy旋转角；T = rotx(rpy[0]) * roty(rpy[1]) * rotz(rpy[2])
	* @return ERR_SUCC 成功 其他失败
	*/
	DLLEXPORT_API errno_t get_gravity_direction(const JKHD *handle, double* rpy);

	/// @brief 多机器人同步运动指令
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param move_mode ABS(绝对运动) or INCR（相对运动）
	/// @param is_block TRUE(阻塞运动) or FALSE(非阻塞运动)
	/// @param joint_pos 两个机器人的位置指令
	/// @param vel 两个机器人速度指令
	/// @param acc 两个机器人的加速度指令
	/// @return 
	DLLEXPORT_API errno_t robot_run_multi_movj(const JKHD *handle, int robot_id, const MoveMode *move_mode, BOOL is_block, const JointValue *joint_pos, const double* vel, const double* acc);

	/// @brief 多机器人同步运动指令
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param move_mode ABS(绝对运动) or INCR（相对运动）
	/// @param is_block TRUE(阻塞运动) or FALSE(非阻塞运动)
	/// @param end_pos 两个机器人的位置指令
	/// @param vel 两个机器人速度指令
	/// @param acc 两个机器人的加速度指令
	/// @return 
	DLLEXPORT_API errno_t robot_run_multi_movl(const JKHD *handle, int robot_id, const MoveMode *move_mode, BOOL is_block, const CartesianPose* end_pos, const double* vel, const double* acc);

    /// @brief 获取两个机器人的DH参数
    /// @param dh_param dh参数， 2维
    /// @return 
	DLLEXPORT_API errno_t robot_get_multi_robot_dh(const JKHD *handle, DHParam *dh_param);

    /// @brief 获取两个机器人是否到位
    /// @param inpos 1 到位； 0 未到位； 2维
    /// @return 
	DLLEXPORT_API errno_t robot_is_inpos(const JKHD *handle, int* inpos);
	
	/// @brief 设置机器人末端工具负载
    /// @param robot_id  机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1)
    /// @param payload 机器人负载参数， 2维
    /// @return 
	DLLEXPORT_API errno_t robot_set_tool_payload(const JKHD *handle, int robot_id, const PayLoad* payload);

	DLLEXPORT_API errno_t robot_get_tool_payload(const JKHD *handle, PayLoad* payload);

	/// @brief 设置传感器灵敏度接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-20
	/// @param deadzone_percent 传感器灵敏度死区占默认最大死区的百分比，数据范围0-1
	/// @return 
	DLLEXPORT_API errno_t robot_set_ftsensor_deadzone(const JKHD *handle, int robot_id, int sensor_id, const double* deadzone_percent);

	DLLEXPORT_API errno_t robot_get_ftsensor_deadzone(const JKHD *handle, int robot_id, int sensor_id, double* deadzone_percent);

	/// @brief 设置力控坐标系接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param ftframe 力控坐标系 接受工具(0) 世界(1)
	/// @return 
	DLLEXPORT_API errno_t robot_get_cst_ftframe(const JKHD *handle, int robot_id, int* ftframe);

	DLLEXPORT_API errno_t robot_set_cst_ftframe(const JKHD *handle, int robot_id, int ftframe);

	/// @brief 设置恒力柔顺参数接口
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param axis 要设置的方向，数据范围0-5，依次代表x,y,z,rx,ry,rz
	/// @param enable 是否开启力控，接受关(0) 开(1)
	/// @param ftUser 力控刚度，需为正数，请勿设置为0，一般建议x,y,z设置10以上的数值，mx,my,mz设置1以上的数值
	/// @param ftReboundFK 回弹弹力系数，需为正数，可以设置为0
	/// @param ftConstant 目标力，请勿设置超出机器人承受范围的目标力
	/// @return 
	DLLEXPORT_API errno_t robot_set_cst_ftconfig(const JKHD *handle, int robot_id, int axis, int enable, double ftUser, double ftReboundFK, double ftConstant);

	DLLEXPORT_API errno_t robot_get_cst_ftconfig(const JKHD *handle, int robot_id, RobotAdmitCtrl* config);

	/// @brief 开启恒力柔顺控制接口，恒力柔顺控制可以配合直线或关节运动以及笛卡尔伺服运动模式使用，不可以配合拖拽模式或手动示教JOG使用
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @return 
	DLLEXPORT_API errno_t robot_enable_force_control(const JKHD *handle, int robot_id);

	/// @brief 关闭恒力柔顺控制接口，注意关闭力控将使力控立即失效但不会退出力控模式
	/// 直至机器人执行完成当前运动（或退出伺服运动模式）后力控模式才会真正退出，因此在此期间无法再次开启力控
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @return 
	DLLEXPORT_API errno_t robot_disable_force_control(const JKHD *handle, int robot_id);

	/// @brief 传感器校零接口，注意校零需要约1秒的时间，期间无法开启力控，固建议调用此接口后等待1秒。
	/// 一般建议在开启力控前都进行一次传感器校零，注意校零时传感器不要受到除负载重力以外的任何外力。
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @return
	DLLEXPORT_API errno_t robot_zero_ftsensor(const JKHD *handle, int robot_id, int sensor_id);

	/// @brief 设置传感器负载接口，注意传感器负载与机器人负载可以不同（也可以相同），需要单独设置
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param payload 负载数据，单位kg，mm
	/// @return
	DLLEXPORT_API errno_t robot_set_ftsensor_payload(const JKHD *handle, int robot_id, int sensor_id, PayLoad payload);

	DLLEXPORT_API errno_t robot_get_ftsensor_payload(const JKHD *handle, int robot_id, int sensor_id, PayLoad* payload);

	/// @brief 设置传感器数据平滑滤波器截止频率
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param filter 截止频率，需为正数，单位Hz
	/// @return
	DLLEXPORT_API errno_t robot_set_ftsensor_filter(const JKHD *handle, int robot_id, int sensor_id, double filter);

	DLLEXPORT_API errno_t robot_get_ftsensor_filter(const JKHD *handle, int robot_id, int sensor_id, double* filter);

	/// @brief 获取力控模式状态，注意当调用disable_force_control后但机器人尚未完成当前运动期间力控模式仍被视作开启状态
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param force_control_stat 0代表关闭，1代表开启
	/// @return
	DLLEXPORT_API errno_t robot_get_force_control_stat(const JKHD *handle, int robot_id, int* force_control_stat);

	/// @brief 获取传感器状态
	/// @param robot_id 机器人ID 接受LEFT(0) RIGHT(1) DUAL(-1) 
	/// @param sensor_id 传感器ID 数据范围1-199
	/// @param status 正常(1) 错误(-1)
	/// @param errcode 无数据(1) 数据错误(2) 过载(4)
	/// @param ft_original 传感器在自身坐标系下的原始读数
	/// @param ft_actual 传感器在法兰坐标系下的经过负载和零点补偿后的读数
	/// @return 
	DLLEXPORT_API errno_t robot_get_ftsensor_stat(const JKHD *handle, int robot_id, int sensor_id, int* status, int* errcode, double* ft_original, double* ft_actual);
	 
	/// @brief 查詢机器人当前是否超出软限位 
    /// @param robot_id 接受LEFT(0) RIGHT(1)
    /// @param limit 0 代表无超出，1代表超出
    /// @return 
	DLLEXPORT_API errno_t robot_is_on_soft_limit(const JKHD *handle, int robot_id, int* limit);


	/// @brief 确认机器人是否处于错误状态
	/// @param in_error 0 代表机器人处于正常状态，1代表机器人处于错误状态
	/// @return 
	DLLEXPORT_API errno_t robot_is_in_error(const JKHD *handle, int* in_error);

	/// @brief 设置机器人工具坐标系
	/// @param robot_id 接受LEFT(0) RIGHT(1)
	/// @param tool 工具坐标系
	/// @return 
	DLLEXPORT_API errno_t robot_set_tool_offset(const JKHD *handle, int robot_id, CartesianPose tool);

	/// @brief 获取机器人工具坐标系
	/// @param robot_id 接受LEFT(0) RIGHT(1)
	/// @param offset 工具坐标系
	/// @return 
	DLLEXPORT_API errno_t robot_get_tool_offset(const JKHD *handle, int robot_id, CartesianPose* offset);


	/// @brief 获取机器人的默认基安装
	/// @param robot_id 接受LEFT(0) RIGHT(1)
	/// @param base_offset 
	/// @return 
	DLLEXPORT_API errno_t robot_get_default_base(const JKHD *handle, int robot_id, CartesianPose* base_offset);
	
	DLLEXPORT_API errno_t ext_power_on(const JKHD *handle);
	
	
	DLLEXPORT_API errno_t ext_power_off(const JKHD *handle);
	
	
	DLLEXPORT_API errno_t ext_enable_on(const JKHD *handle);
	
	
	DLLEXPORT_API errno_t ext_enable_off(const JKHD *handle);
	
	
	DLLEXPORT_API errno_t ext_jog_to(const JKHD *handle, int slave_id, int pos, double vel, double acc);
	
	
	DLLEXPORT_API errno_t ext_servo_home(const JKHD *handle, int robot_id);
	
	
	DLLEXPORT_API errno_t ext_get_status(const JKHD *handle, int slave_id, ExtStatus&);
#ifdef __cpluscplus
}
#endif

#undef DLLEXPORT_API
#endif


