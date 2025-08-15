#pragma once
#include <string>
#include <memory>
#include "zucpos2.h"
#include <iostream>
#include <stdbool.h>
#include <vector>
namespace kine {
#define deg_to_rad PM_PI/180.0 
#define rad_to_deg 180.0/PM_PI
#define SINGULAR_FUZZ   0.000001
#define FLAG_FUZZ       0.000001

/* flags for inverse kinematics */
#define JAKA_SHOULDER_RIGHT 0x01
#define JAKA_ELBOW_DOWN     0x02
#define JAKA_WRIST_FLIP     0x04
#define JAKA_SINGULAR       0x08  /* joints at a singularity */

/* flags for forward kinematics */
#define JAKA_UNREACH        0x01  /* pose out of reach */

#define DOF_7_EPS_AVOID_LIMIT 0.01
#define MAX_ITER_TIMES 6
#define CART_TOLERANCE_REGULAR 1e-6
#define CART_TOLERANCE_SINGULAR 0.1

#define ROBOT_DOF 7

#define PINV_MAX 10
#define GET_SIGN(a, b) ((b) >= 0.0 ? fabs(a) : -fabs(a))
#define GET_MAX(a, b) (a > b ? a : b)
#define GET_MIN(a, b) (a < b ? a : b)

const size_t KINE_MAX_JOINTS = 9;
const size_t KINE_MAX_JOINTS_2 = 18;

struct DHParam
{
    double alpha[KINE_MAX_JOINTS];
    double a[KINE_MAX_JOINTS];
    double d[KINE_MAX_JOINTS];
    double joint_homeoff[KINE_MAX_JOINTS];
    // DHParam& operator=(DHParam cpdata_);
};

typedef struct RobotDH
{
    RobJointVal alpha;
    RobJointVal a;
    RobJointVal d;
    RobJointVal joint_homeoff;
    std::string get_robot_dh_str() const
    {
        std::string str = "";
        str += "DH_A = :" + a.val_str() + "\n";
        str += "DH_D = :" + d.val_str() + "\n";
        str += "DH_ALPHA = :" + alpha.val_str() + "\n";
        str += "DH_OFFSET = :" + joint_homeoff.val_str() + "\n";
        return str;
    }
} RobotDH;

typedef struct Robot_joint_Pos_Limit {
    double Joint_Pos_Up[KINE_MAX_JOINTS];
    double Joint_Pos_low[KINE_MAX_JOINTS];
    int set(double jointlimit[KINE_MAX_JOINTS*2]);
} Robot_joint_Pos_Limit;

typedef struct Robot_joint_Vel_Limit {
    double Joint_Vel_Up[7];
    //double Joint_Vel_low[Robot_DOF];
} Robot_joint_Vel_Limit;

typedef struct Robot_joint_Acc_Limit {
    double Joint_Acc_Up[7];
    //double Joint_Acc_low[Robot_DOF];
} Robot_joint_Acc_Limit;
typedef struct  {
    Robot_joint_Pos_Limit Joint_Pos_Limit;
    Robot_joint_Vel_Limit Joint_Vel_Limit;
    Robot_joint_Acc_Limit Joint_Acc_Limit;
} Robot_joint_Limit;

typedef struct {
    double k;
    double alpha;
}joint_lim_Algo_param;
struct Config_7dof_generate
{
    // Robot_joint_Limit Robot_Lim_7;
    Robot_joint_Limit Robot_Lim_7;
};

struct fixed_one_joint_param{
    int fixed_joint_num;
    double fixed_angle;
    // fixed_one_joint_param& operator=(fixed_one_joint_param cpdata_);
};
struct Config_7dof
{
    // Robot_joint_Limit Robot_Lim_7;
    joint_lim_Algo_param JL_Algo_param = {.k = 0.0001, .alpha = 10 };
    int dof_7_inv_type = 1;
	double joint_offset_fix[7];//
    double Joint_Pos_Up[7];
    double Joint_Pos_low[7];
    double Joint_Vel_Up[7];
    double Joint_Acc_Up[7];

    fixed_one_joint_param fixed_joint_param = {.fixed_joint_num = 6, .fixed_angle = 0.0 };
    ZucPose user2T0_dual_arm;
    int enable_dual_arm_user2T0;
    // Config_7dof& operator=(Config_7dof cpdata_);
};

struct Config_Zu
{
    int inv_range_limit_flag = 0; //0 deflaut 1 拓展为360 2296068 拓展为360 允许范围为无穷 by LZX
};
typedef enum
{
    NUMERIC_JACOBIAN_METHOD = 0,
    JACOBIAN_ITERATE_METHOD,
    HALF_ANALYTICAL_METHOD
}MaxSolveMode;

struct Config_Max
{
    MaxSolveMode maxslovemode = NUMERIC_JACOBIAN_METHOD;
};

enum Axis_type
{
    Rot_Axis = 0,
    Tran_Axis
};
struct Config_Ext
{
    // std::vector<Axis_type> aixs_type_all;
    Axis_type aixs_type_all[KINE_MAX_JOINTS];
    int aixs_num;

    Config_Ext();
    // Config_Ext(const Config_Ext& cpdata_) : aixs_type_all(cpdata_.aixs_type_all), aixs_num(cpdata_.aixs_num){};
    int Config_Ext_init_vec(std::vector<int> data_);
    Axis_type& operator[](int num_);
    Config_Ext(std::vector<int> data_);
    // Config_Ext& operator=(const Config_Ext& cpdata_);
};

class KineItf
{
public:
    struct Robot_Config
    { 
        bool full_dh_com;
        RobotDH robot_dh;
        DHParam dh_param;
        Config_Zu conf_zu;
        Config_7dof conf_7dof;
        Config_Max conf_max;
        Config_Ext conf_ext;
        // Robot_Config& operator=(const Robot_Config& cpdata_);
    };
    struct kine_Conf
    {
        unsigned long int iflags;
        // unsigned long int fflags;
        double Arm_a;
        unsigned short numerical_ite_times = 6;
    };

    Robot_Config Robot_Conf;

    virtual ~KineItf() = default;
    virtual int init(Robot_Config& cfg) = 0;

    virtual int fkine(RobJointVal joint, ZucPose& pose, const ZucPose* toolOffset, const ZucPose* user_offset, const PmRpy* base_offset = nullptr) = 0;
    virtual int fkine(RobJointVal joint, ZucPose& pose, const ZucPose* toolOffset, const ZucPose* user_offset, const ZucPose* base_offset) = 0;
    virtual int fkine(RobJointVal joint, ZucPose& pose) = 0;

    virtual int ikine(ZucPose pose, RobJointVal& joint, kine_Conf& conf, const ZucPose* toolOffset, const ZucPose* user_offset, const PmRpy* base_offset = nullptr) = 0;
    virtual int ikine(ZucPose pose, RobJointVal& joint, kine_Conf& conf, const ZucPose* toolOffset, const ZucPose* user_offset, const ZucPose* base_offset) = 0;
    virtual int ikine(ZucPose pose, RobJointVal& joint, kine_Conf& conf) = 0;

    virtual int fkine_elbow(RobJointVal joint, ZucPose& pose, const ZucPose* user_offset, const PmRpy* base_offset) = 0;
    virtual int fkine_elbow(RobJointVal joint, ZucPose& pose, const ZucPose* user_offset, const ZucPose* base_offset) = 0;
    virtual int fkine_elbow(RobJointVal joint, ZucPose& pose) = 0;

    virtual int fkine_wrist(ZucPose& pose) = 0;
    virtual int fkine_wrist(ZucPose& pose, const ZucPose* toolOffset, const ZucPose* user_offset, const ZucPose* base_offset) = 0;
    virtual int fkine_wrist(ZucPose& pose, const ZucPose* toolOffset, const ZucPose* user_offset, const PmRpy* base_offset = nullptr) = 0;
protected:
};
const uint8_t KINETYPE_ZU = 0;
const uint8_t KINETYPE_MINI = 1;
const uint8_t KINETYPE_ATOM = 2;
const uint8_t KINETYPE_MAX = 3;
const uint8_t KINETYPE_A = 4;
const uint8_t KINETYPE_EXT = 9;

std::shared_ptr<KineItf> create_kine(uint8_t type);
}  // namespace kine
