#pragma once
#include "posemath.h"

typedef struct ZucPose
{
    PmCartesian tran;
    double a, b, c;
    double u, v, w;
} ZucPose;

template <typename T> class RobJointData
{
public:
    static const size_t MAX_AXIS = 9;
    RobJointData() { memset(val, 0, MAX_AXIS * sizeof(T)); }
    T& operator[](size_t idx) { return val[idx]; }

    T val[MAX_AXIS];
    std::string val_str() const
    {
        std::string res = "";
        for (size_t i = 0; i < MAX_AXIS; i++) { res += std::to_string(static_cast<double>(val[i])) + ","; }
        return res;
    }
};

class RobJointVal : public RobJointData<double>
{
public:
    RobJointVal() : RobJointData<double>() {}
    RobJointVal(const double v[MAX_AXIS])
    {
        for (size_t i = 0; i < MAX_AXIS; i++) { val[i] = v[i]; }
    }
    RobJointVal(std::vector<double> v)
    {
        size_t minsize = v.size() < MAX_AXIS ? v.size() : MAX_AXIS;
        for (size_t i = 0; i < minsize; i++) { val[i] = v[i]; }
    }
    RobJointVal(ZucPose Pose)
    {
        val[0] = Pose.tran.x;
        val[1] = Pose.tran.y;
        val[2] = Pose.tran.z;
        val[3] = Pose.a;
        val[4] = Pose.b;
        val[5] = Pose.c;
        val[6] = Pose.u;
    }
    void array_value(double v[MAX_AXIS])
    {
        for (size_t i = 0; i < MAX_AXIS; i++) { v[i] = val[i]; }
    }
    std::vector<double> vector_value()
    {
        std::vector<double> v;
        for (size_t i = 0; i < MAX_AXIS; i++) { v.push_back(val[i]); }
        return v;
    }
    bool near(RobJointVal& jpos, double tol)
    {
        for (size_t i = 0; i < MAX_AXIS; i++)
        {
            if (fabs(val[i] - jpos[i]) > tol)
            {
                return false;
            }
        }
        return true;
    }
};



