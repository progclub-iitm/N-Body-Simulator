#ifndef PARTICLES_H
#define PARTICLES_H

class points{

  public:
    float vx = 0;
    float x;
    float y;
    float vy = 0;
    float ax;
    float ay;
    float fx;
    float fy;
    float m = 1;
    float radius = 20;

    float distance( points point );
    float calculateForcex( points point, float d );
    float calculateForcey( points point, float d );

};

#endif
