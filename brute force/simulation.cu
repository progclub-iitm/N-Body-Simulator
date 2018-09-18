#include<stdio.h>
#include <GLFW/glfw3.h>
#include <learnopengl/shader.h>
#include<math.h>
#include <iostream>
#include "particles.h"
#define SCR_WIDTH 1000
#define SCR_HEIGHT 1000

float factor = (float)1/SCR_HEIGHT;

void framebuffer_size_callback(GLFWwindow* window, int width, int height); //Function to change display on every window resize

void initiate(GLFWwindow** window);

int main(){

    printf("Enter the number of particles:       ");

    int i,n,j;
    int k;
    float d;
    scanf("%d",&n);

    //Initiating the window to draw
    GLFWwindow* window;
    initiate(&window);

    float temp;

    points point[n];
    float pos[2*n];

    for(i=0,j=0;i<n;i++,j++){
        point[i].x = 2*(float)rand()/(float)(RAND_MAX)-1.1;
        if(point[i].x<-0.9){
            point[i].x+=0.2;
        }

        pos[j] = point[i].x;

        point[i].y = 2*(float)rand()/(float)(RAND_MAX)-1.1;
        if(point[i].y<-0.9){
            point[i].y+=0.2;
        }
        j++;

        pos[j] = point[i].y;

        for(k=0;k<i;j++){
            if(i!=k){
                d = point[i].distance(point[k]);
                if(d<4*factor*point[i].radius){
                    i--;
                    j-=2;
                }
            }
          }
    }

      //Creating a vertex array object
      unsigned int VAO;
      glGenVertexArrays(1, &VAO);

      //Creating a vertex buffer object
      unsigned int VBO;
      glGenBuffers(1,&VBO);
      glBindBuffer(GL_ARRAY_BUFFER, VBO);

      //Copying the data into gpu's memory
      glBufferData(GL_ARRAY_BUFFER, sizeof(pos), pos, GL_DYNAMIC_DRAW);
      glBindVertexArray(VAO);


      //Creatiing a vertex attribute pointer for the points
      glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2*sizeof(float), (void*)(0));
      glEnableVertexAttribArray(0);

      Shader shader("vertex_shader_source", "fragment_shader_source");

      glEnable(GL_POINT_SMOOTH);
      glEnable(GL_BLEND);
      glEnable( GL_POINT_SPRITE );
    float mass;

    double dt = 0.00001;
    if(n>50){
        dt = 0.000001;
        for(i=0;i<n;i++){
            point[i].radius = 7;
        }
    }
    else if(n>25){
        dt = 0.000001;
        for(i=0;i<n;i++){
            point[i].radius = 10;
        }
      }
    else if(n>10){
        dt = 0.000001;
        for(i=0;i<n;i++){
            point[i].radius = 15;
        }
      }

    float radius;
    while (!glfwWindowShouldClose(window))
    {
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        //Copying the data into gpu's memory
        glBufferData(GL_ARRAY_BUFFER, sizeof(pos), pos, GL_DYNAMIC_DRAW);
        glBindVertexArray(VAO);

        shader.use();
        for(i=0,k=0;i<n;i++,k++){

            mass = point[i].m;
            radius = point[i].radius;
            glPointSize(2*radius);
            glDrawArrays(GL_POINTS,i,1);
            for(j=0;j<n;j++){

              if( i != j ){
                d = point[i].distance(point[j]);

                point[i].fx += point[i].calculateForcex( point[j], d);
                point[i].fy += point[i].calculateForcey( point[j], d);

                if(d<4*factor*point[i].radius){
                    temp = point[i].vx;
                    point[i].vx = point[j].vx;
                    point[j].vx = temp;
                    temp = point[i].vy;
                    point[i].vy = point[j].vy;
                    point[j].vy = temp;
                    point[i].fx -= 2*point[i].calculateForcex( point[j], d);
                    point[i].fy -= 2*point[i].calculateForcey( point[j], d);
              }
              }

            }
            point[i].ax = point[i].fx / mass;
            point[i].ay = point[i].fy / mass;
            point[i].vx += point[i].ax*dt;
            point[i].vy += point[i].ay*dt;
            point[i].fx = 0;
            point[i].fy = 0;

            point[i].x += point[i].vx*dt;
            point[i].y += point[i].vy*dt;

            pos[k] = point[i].x;
            if(pos[k]+2*factor*point[i].radius > 1 || pos[k]-2*factor*point[i].radius<-1){
                point[i].vx = -point[i].vx;
            }
            k++;
            pos[k] = point[i].y;
            if(pos[k]+2*factor*point[i].radius > 1 || pos[k]-2*factor*point[i].radius<-1){
                point[i].vy = -point[i].vy;
            }
        }

        glfwSwapBuffers(window);
        glfwPollEvents();

      }


      glfwTerminate();
      return 0;
}



void framebuffer_size_callback(GLFWwindow* window, int width, int height)
  {
      glViewport(0, 0, width, height);
  }


void initiate(GLFWwindow** window){
    //Initiating the GLFW window
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    *window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", NULL, NULL);
    glfwMakeContextCurrent(*window);
    //Creating a viewport
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT);
    glfwSetFramebufferSizeCallback(*window, framebuffer_size_callback);

}
