#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <std_msgs/String.h>
#include <geometry_msgs/Twist.h>
#include <string.h>
#include <iostream>
#define RAD2DEG(x) ((x)*180./M_PI)

using namespace std;


class PubandSub{
    private:
        ros::NodeHandle nh;
        ros::Subscriber sub_scan;
        ros::Subscriber sub_cam;
        ros::Publisher pub;
        geometry_msgs::Twist pubmsg;
        int noise_count = 0;
        string spin_msg = "";
        int m1_motor = 0;
        int m2_motor = 0;
    
    public:
        PubandSub(){
            sub_scan = nh.subscribe<sensor_msgs::LaserScan>("/scan", 1, &PubandSub::process_lidar,this);
            sub_cam = nh.subscribe<std_msgs::String>("/cam", 1, &PubandSub::process_cam,this);
            pub = nh.advertise<geometry_msgs::Twist>("/main",1);
        }

        void process_cam(const std_msgs::String::ConstPtr& msg){
            spin_msg = msg->data.c_str();
        }

        void process_lidar(const sensor_msgs::LaserScan::ConstPtr& scan){
            for(int i = 0; i < scan->ranges.size(); i+=5) {
                float degree = RAD2DEG(scan->angle_min + scan->angle_increment * i);
                int angle = (int)degree;
                float distance = scan->ranges[i];
                if(-50 < angle && angle < 30 && distance != 0.0){
                    if(distance < 0.5){
                        noise_count += 1;
                        if(noise_count > 30) noise_count = 100;
                        m1_motor = 0;
                        m2_motor = 0;

                        // avoid
                        // if(angle > 0){
                        //     m1_motor += 20;
                        //     m2_motor = 0;
                        // }
                        // else if(angle < 0){
                        //     m1_motor = 0;
                        //     m2_motor += 20;
                        // }

                    }
                    else{
                        noise_count -= 4;
                        if(noise_count < 8){
                            noise_count = 0;
                            if(spin_msg == "Right"){
                                m1_motor += 20;
                                m2_motor = 0;     
                            }
                            else if(spin_msg == "Left"){
                                m1_motor = 0;
                                m2_motor += 20;
                            }
                            else if(spin_msg == "Straight"){
                                m1_motor += 100;
                                m2_motor += 100;
                            }
                            else{
                                m1_motor = 0;
                                m2_motor = 0;
                            }
                        }
                    }
                    pubmsg.linear.x = m1_motor;
                    pubmsg.angular.z = m2_motor;
                    pub.publish(pubmsg);
                }
            }
        }
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "teleop");
    PubandSub PaS;
    ros::spin();
    return 0;
}