#include "particles.h"
#include <math.h>

float points::distance( points point ){

    return sqrt((x-point.x)*(x-point.x) + (y-point.y)*(y-point.y));

}

float points::calculateForcex( points point, float d ){

    return m*point.m*(point.x-x)/(d*d*d);

}

float points::calculateForcey( points point, float d ){

    return m*point.m*(point.y-y)/(d*d*d);

}
