


#!/usr/bin/env python
# license removed for brevity
import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import random
import sys
#import turtle

listenChannel = 'turtle1/pose'
postChannel = 'turtle1/cmd_vel'
pub = rospy.Publisher(postChannel, Twist, queue_size=1)
a = []
pointToAvoid = Pose()

waypoint = Pose()
alternate = Pose()

def fillList():
    #x=0
    #y=0
    #k=0
    #a[2][100]
    #for(i=0;i<10;i++):
    #    for(j=0;j<10;j++):
    #        a[0][k] = x
    #        a[1][k] = y
    #        x++
    #        k++
    #    y++

    x = 0
    y = 0
    for i in range (0,11):
        #if up or down

        for j in range (0,11):
            pathWay = Pose()
            pathWay.x = x
            pathWay.y = y

            if (i%2 == 0):
                y = y + 1
            else:
                y = y - 1

            a.append(pathWay)
        x = x + 1

#def fillListToAvoid(x, y):
#    badPoint = Pose()
#    badPoint.x = x
#    badPoint.y = y
#    badPoint.theta = 0

#    listToAvoid = [badPoint]

def changeWaypoint(good, bad, current):
    # won't work when going left to right
    # won't work for edge cases all the way to the right
    # won't work if the points to avoid are not in chronological order
    #what if waypoint is close to bad point

    alternateOne = Pose()
    alternateOne.x = bad.x + .5
    alternateOne.y = current.y
    alternateOne.theta = bad.theta

    alternateTwo = Pose()
    alternateTwo.x = bad.x + .5
    alternateTwo.y = bad.y + (bad.y - current.y)
    alternateTwo.theta = bad.theta

    backOnTrack = Pose()
    backOnTrack.x = good.x
    backOnTrack.y = bad.y + .5
    backOnTrack.theta = bad.theta

    old = Pose()
    old = good
    #a = [alternate] + [backOnTrack] + [old] + a
    a.insert(0,old)
    a.insert(0,backOnTrack)
    a.insert(0,alternateTwo)
    a.insert(0,alternateOne)

def sendCommand(v, w):
    stopMsg = Twist()
    stopMsg.linear.x = v
    stopMsg.angular.z = w
    pub.publish(stopMsg)

def distance(currentPos, desiredPos):
    return math.sqrt((currentPos.x-desiredPos.x)**2 + (currentPos.y-desiredPos.y)**2)

def angle_diff(a0,a1):
    return (((a0 - a1) + 3 * math.pi)%(2*math.pi)) - math.pi


def callback(data):

    # path planning stuff

    #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    #print("Turtle is at x=" + str(data.x) + " y=" + str(data.y) + " t=" + str(data.theta))

    # if so and so and send command...

    d = distance(data, waypoint)


    if d < .5:
        setWaypoint()

    distFromBadPoint = distance(data, pointToAvoid)

    if distFromBadPoint < .25:
        changeWaypoint(waypoint, pointToAvoid, data)


        #setWaypoint(, random.randint(1, 10), 0)
        #setWaypoint(random.randint(1, 10), random.randint(1, 10), 0)
        print("NEW WAYPOINT")
    #print("wapoint is: " + str(waypoint.x) + " " + str(waypoint.y))
    #print("location is: " + str(data.x) + " " + str(data.y))
    #print("diff is: " + str((waypoint.y-data.y)) + "/" + str((waypoint.x-data.x)))
    #other_heading = (waypoint.y-data.y) / (waypoint.x-data.x)
    #print(other_heading)

    heading_to_p = math.atan2((waypoint.y-data.y), (waypoint.x-data.x))


    heading_error = angle_diff(heading_to_p, data.theta)

    #print("distance: " + str(d) + " heading: " + str(heading_to_p) + " error: " + str(heading_error))
    #print("current heading: " + str(data.theta))

    angle_vel = heading_error * 10
    #if(data.theta < heading_to_p):
    #    angle_vel = 10
    #elif (data.theta > heading_to_p):
    #    angle_vel = -10

    #angle_vel = -10*heading_error
    linear_vel = d

    # SPIN!!!!!
    sendCommand(linear_vel, angle_vel)


def setWaypoint():

    if (len(a) == 0): # end contitions

        print("Done!")
        sys.exit(0)



    newPoint = a.pop(0)
    #a.pop(0)
    waypoint.x = newPoint.x
    waypoint.y = newPoint.y
    waypoint.theta = newPoint.theta
    print("Turtle should go to x=" + str(waypoint.x) + " y=" + str(waypoint.y) + " t=" + str(waypoint.theta))


def startup():

    fillList()
    pointToAvoid.x = 0
    pointToAvoid.y = 4.5
    pointToAvoid.theta = 0

    setWaypoint() #desired waypoint

    #subscribe to the turtle's position messages
    rospy.init_node('turtleCommandNode', anonymous=True)
    rospy.Subscriber(listenChannel, Pose, callback)


    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()



if __name__ == '__main__':
    startup()
