
#include<stdio.h>
#include <GLFW/glfw3.h>
#include <learnopengl/shader.h>
#include<math.h>
#include <iostream>
#include <cuda.h>
#define N 100000
#define SCR_WIDTH 2000
#define dt 0.001
#define SCR_HEIGHT 1000
#define FACTOR 0.001
#define RADIUS 2 //Change this between 25 and 1,25 corresponds to n<=10 and 1 corresponds to n=10000
#define EPSILON 1 //Included with distance to avoid infinite acceleration
//Struct for 2-D points with two doubles as members
typedef struct points{
  double x;
  double y;
  points():x(0),y(0)
  {
  }
  points(double x1,double y1):x(x1),y(y1)
  {
  }
}point;

//Struct for storing components of 2-D velocity
typedef struct velocities{
  double vx;
  double vy;
  velocities():vx(0),vy(0)
  {
  }
  velocities(double vx1,double vy1):vx(vx1),vy(vy1)
  {
  }
}velocity;

//Struct for storing 2-D acceleration
typedef struct accelerations{
  double ax;
  double ay;
  accelerations():ax(0),ay(0)
  {
  }
  accelerations(double ax1,double ay1):ax(ax1),ay(ay1)
  {
  }
}acceleration;

point* pos = new point[N];
velocity* vel = new velocity[N];
acceleration* acc = new acceleration[N];

double distance( point curr , point aff );
void framebuffer_size_callback(GLFWwindow* window, int width, int height); //Function to change display on every window resize


__global__ void calculateForce( double* posi , acceleration* acc , velocity* vel , int *np){
        int n = *np;
        int i = threadIdx.x + blockIdx.x*blockDim.x;
        if( i < n ){
            int j;
            for ( j = 0 ; j < n ; j++){
                if( i == j )
                  continue;
                double d = sqrt((posi[2*i]-posi[2*j])*(posi[2*i]-posi[2*j])+(posi[2*i+1]-posi[2*j+1])*(posi[2*i+1]-posi[2*j+1])+EPSILON);

                if( d<4*FACTOR*RADIUS ){

                  continue;
                }
                double d3 = d*d*d;
                acc[i].ax += ( posi[2*j] - posi[2*i] )/d3;
                acc[i].ay += (  posi[2*j+1] - posi[2*i+1] )/d3;
                //Objects are too close
                //Elastic collisio
                /*
                if( d<5*FACTOR*RADIUS ){
                  //Switching velocities for collision
                  double temp;
                  temp = vel[i].vx;
                  vel[i].vx = vel[j].vx;
                  vel[j].vx = temp;
                  temp = vel[i].vy;
                  vel[i].vy = vel[j].vy;
                  vel[j].vy = temp;
                  acc[i].ax -= 2*( posi[2*j] - posi[2*i] )/d3;
                  acc[i].ay -= 2*( posi[2*j+1] - posi[2*i+1] )/d3;
                }*/

          }
          vel[i].vx += acc[i].ax*dt;
          posi[2*i] += vel[i].vx*dt;
          vel[i].vy += acc[i].ay*dt;
          posi[2*i+1] += vel[i].vy*dt;
          acc[i].ax = 0;
          acc[i].ay = 0;
        }
  }

int main( void ){

    int i,n,j,*dev_n;
    double *dev_pos;
    acceleration *dev_acc;
    velocity *dev_vel;
    std::cout<<"Enter the number of particles:"<<std::endl;
    std::cin>>n;
    //Initiating the window to draw
    GLFWwindow* window;
    //Initiating the GLFW window
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    #ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // uncomment this statement to fix compilation on OS X
  #endif
    window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", NULL, NULL);
    glfwMakeContextCurrent(window);
    //Creating a viewport
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);


    //For loop generating random doubles which constitutes the position of the particles
    for( i = 0 ; i < n ; i++ ){

        pos[i].x = 2*(float)rand()/(float)(RAND_MAX)-1.1;

        if( pos[i].x < -0.9){
            pos[i].x += 0.2;
        }

        pos[i].y = 2*(float)rand()/(float)(RAND_MAX)-1.1;

        if( pos[i].y < -0.9){
            pos[i].y += 0.2;
        }
        //Prevent intersection of elements at initialization
        //Delete this for large number of paricles
        for( j = 0 ; j < i ; j++ ){
            double d = distance(pos[i],pos[j]);
            if( d < 2*FACTOR*RADIUS ){
               i--;
               break;
            }
        }
      }


    cudaMalloc((void**)&dev_pos,N*sizeof(point));
    cudaMalloc((void**)&dev_vel,N*sizeof(point));
    cudaMalloc((void**)&dev_acc,N*sizeof(point));
    cudaMalloc((void**)&dev_n,sizeof(int));
    cudaMemcpy(dev_n,&n,sizeof(int),cudaMemcpyHostToDevice);

    //Creating a vertex array object
    unsigned int VAO;
    glGenVertexArrays(1, &VAO);

    //Creating a vertex buffer object
    unsigned int VBO;
    glGenBuffers(1,&VBO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);

    double posi[2*n];
    for( i = 0 ; i < n ; i++){
        posi[2*i] = pos[i].x;
        posi[2*i+1] = pos[i].y;
    }
    //Copying the data into gpu's memory
    glBufferData(GL_ARRAY_BUFFER, sizeof(posi), posi, GL_DYNAMIC_DRAW);
    glBindVertexArray(VAO);


    //Creatiing a vertex attribute pointer for the points
    glVertexAttribPointer(0, 2, GL_DOUBLE, GL_FALSE, 2*sizeof(double), (void*)(0));
    glEnableVertexAttribArray(0);

    Shader shader("vertex_shader_source", "fragment_shader_source");
    cudaMemcpy(dev_pos,posi,2*n*sizeof(double),cudaMemcpyHostToDevice);
    cudaMemcpy(dev_vel,vel,n*sizeof(velocity),cudaMemcpyHostToDevice);
    cudaMemcpy(dev_acc,acc,n*sizeof(acceleration),cudaMemcpyHostToDevice);
    glEnable(GL_POINT_SMOOTH);
    glEnable(GL_BLEND);
    glEnable( GL_POINT_SPRITE );
    while (!glfwWindowShouldClose(window))
    {

        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        shader.use();
        //Copying the data into gpu's memory
        glBindBuffer(GL_ARRAY_BUFFER, VBO);
        glBufferData(GL_ARRAY_BUFFER, sizeof(posi), posi, GL_DYNAMIC_DRAW);
        glBindVertexArray(VAO);
        glPointSize(2*RADIUS);
        glDrawArrays(GL_POINTS,0,n);
        glfwSwapBuffers(window);
        glfwPollEvents();
        calculateForce<<<65535,1024>>>(dev_pos,dev_acc,dev_vel,dev_n);  //For larger values of n change this to 63353 instead of (n+1023)/1024
        cudaMemcpy(posi,dev_pos,2*n*sizeof(double),cudaMemcpyDeviceToHost);

      }
      glfwTerminate();
      return 0;
}


double distance( point curr , point aff ){
    return sqrt((curr.x-aff.x)*(curr.x-aff.x)+(curr.y-aff.y)*(curr.y-aff.y));
}

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
  {
      glViewport(0, 0, width, height);
  }
