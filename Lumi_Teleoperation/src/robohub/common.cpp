#include "common.h"
#include "JAKAZuRobot.h"

// 检查并清除故障， 部分故障无法直接清除，需要下电
int check_error(JAKAZuRobot &robot, bool need_reset)
{
    int error[2] = {};
    robot.robot_is_in_error(error);
    if (error[0] || error[1])
    {
        printf("error happens\n");
        if (need_reset)
        {
            robot.clear_error();    // 使能前可以清除一下故障，以免使能失败
        }
        return 1;
    }
    return 0;
}

// 查询上电、上使能状态
int check_state(JAKAZuRobot &robot)
{
    RobotState state;
    robot.get_robot_state(&state);
    printf("Dual Robot State: %s %s %s\n", state.estoped ? "estoped" : "Safe", state.poweredOn ? "powered" : "off", state.servoEnabled ? "enabled" : "disabled");
    return 0;
}

int check_inpos(JAKAZuRobot &robot)
{
    int inpos[2] = {};
    robot.robot_is_inpos(inpos);
    if (inpos[0] && inpos[1])
    {
        printf("Both robots are inpos\n");
        return 1;
    }
    printf("inpos state %d %d\n", inpos[0], inpos[1]);
    return 0;
}