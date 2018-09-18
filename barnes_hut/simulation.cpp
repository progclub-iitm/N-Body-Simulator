//N-Body simulation with barnes hut coded by devakrishna


//Includes for opengl
#include<stdio.h>
#include <GLFW/glfw3.h>
#include <learnopengl/shader.h>
#include<math.h>
#include <iostream>

#define N 100000
#define DEPTH 100
#define SCR_WIDTH 1000
#define THETA 0.5
#define dt 0.00001
#define SCR_HEIGHT 1000
#define FACTOR 0.001
#define RADIUS 1 //Change this between 25 and 1,25 corresponds to n<=10 and 1 corresponds to n=10000
#define EPSILON 1
void framebuffer_size_callback(GLFWwindow* window, int width, int height); //Function to change display on every window resize

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

//Struct storing elements of a node
typedef struct nodes{
    int mass;
    point com;
    int index;
    struct nodes* ptr[4];
    nodes(double x,double y,int i):mass(1),index(i)
    {
      com.x = x;
      com.y = y;
      ptr[0] = NULL;
      ptr[1] = NULL;
      ptr[2] = NULL;
      ptr[3] = NULL;
    }
}node;

point* pos = new point[N];
velocity* vel = new velocity[N];
acceleration* acc = new acceleration[N];

int n;
node* root = NULL;
int depth = 0;
void insert(node* curr,int i,double xl=-1,double yl=-1,double xr=1,double yr=1);
void traverse(node* curr);
double distance( point curr , point aff );
void updateAcceleration(node* curr,node* aff = root,double xl=-1,double xr=1);
void updatePos(node* curr);
node* deleteTree(node* node);

int main(){

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
  std::cout<<"Enter the Number of particles: "<<std::endl;

  std::cin>>n;
  int i,j;

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
    for( j = 0 ; j < i ; j++ ){
        double d = distance(pos[i],pos[j]);
        if( d < 2*FACTOR*RADIUS ){
           i--;
           break;
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
        root = new node(pos[0].x,pos[0].y,0);
        //Main loop
        for( i = 1 ; i < n ; i++){
            insert(root,i);
            depth = 0;
        }
        updatePos(root);
        root = deleteTree(root);
        for( i = 0 ; i < n ; i++){
            posi[2*i] = pos[i].x;
            posi[2*i+1] = pos[i].y;
        }
      }
      glfwTerminate();
      return 0;

  }

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
  {
      glViewport(0, 0, width, height);
  }



//Inserting the particle i at the curr node
void insert(node* curr,int i,double xl,double yl,double xr,double yr){
      if(curr==NULL){
        return;
      }
      depth++;
      //Has children
      if( curr->index == -1 ){
          double divx = (xl+xr)/2;
          double divy = (yl+yr)/2;
          //Updating center of mass and total mass when the node already has a children
          curr->mass+=1;
          curr->com.x = (curr->com.x*curr->mass+pos[i].x)/(curr->mass+1);
          curr->com.y = (curr->com.y*curr->mass+pos[i].y)/(curr->mass+1);
          if( pos[i].x > divx ){
              if( pos[i].y > divy ){
                if( curr->ptr[0] != NULL ){
                  insert( curr->ptr[0],i,divx,divy,xr,yr);
                  return;
                }
                curr->ptr[0] = new node(pos[i].x,pos[i].y,i);
                return;
              }
              if( curr->ptr[3] != NULL ){
                insert( curr->ptr[3],i,divx,yl,xr,divy);
                return;
              }
              curr->ptr[3] = new node(pos[i].x,pos[i].y,i);
              return;
          }
          if( pos[i].y > divy ){
            if( curr->ptr[1] != NULL ){
              insert( curr->ptr[1],i,xl,divy,divx,yr);
              return;
            }
            curr->ptr[1] = new node(pos[i].x,pos[i].y,i);
            return;
          }
          if( curr->ptr[2] != NULL ){
            insert( curr->ptr[2],i,xl,yl,divx,divy);
            return;
          }
          curr->ptr[2] = new node(pos[i].x,pos[i].y,i);
          return;
      }

      int index = curr->index;
      //If the points are so close with no children
      if( depth >= DEPTH ){
        curr->index = -1;
        curr->ptr[0] = new node(pos[i].x,pos[i].y,i);
        curr->ptr[1] = new node(pos[index].x,pos[index].y,i);
        curr->com.x = (pos[i].x+pos[index].x)/2;
        curr->com.y = (pos[i].y+pos[index].y)/2;
        curr->mass = 2;
        return;
      }

      //If the points are sufficiently far with no children
      curr->index = -1;
      insert(curr,index,xl,yl,xr,yr);
      insert(curr,i,xl,yl,xr,yr);
      curr->mass = 2;
      curr->com.x = (pos[i].x+pos[index].x)/2;
      curr->com.y = (pos[i].y+pos[index].y)/2;
      return;
}

//Traversing the tree delete after completion
void traverse(node*curr){
    if(curr==NULL)
      return;
    std::cout<<curr->com.x<<"   "<<curr->com.y<<std::endl;
    int i;
    for( i = 0 ; i < 4; i++){
      traverse(curr->ptr[i]);
    }
    return;
}

double distance( point curr , point aff ){
    return sqrt((curr.x-aff.x)*(curr.x-aff.x)+(curr.y-aff.y)*(curr.y-aff.y)+EPSILON);
}

//Updating acceleration of curr node
void updateAcceleration(node* curr , node* aff, double xl ,double xr){
    if( aff == NULL || curr == NULL || aff == curr )
      return;
    double d = distance( curr->com , root->com );
    double s = abs(xr-xl);

    double d3 = d*d*d;
    //Treating the eff node as single body
    if( s/d < THETA || aff->index != -1 ){

        acc[curr->index].ax += aff->mass*( aff->com.x - curr->com.x )/d3;
        acc[curr->index].ay += aff->mass*( aff->com.y - curr->com.y )/d3;

        return;
    }
    int i;
    double div1 = (xl+xr)/2;
    updateAcceleration(curr,root->ptr[0],div1,xr);
    updateAcceleration(curr,root->ptr[1],xl,div1);
    updateAcceleration(curr,root->ptr[2],xl,div1);
    updateAcceleration(curr,root->ptr[3],div1,xr);
}

//Updating position of curr node
void updatePos(node* curr){
    if( curr == NULL )
      return;
    //Internal node
    if( curr->index == -1 ){
        int i;
        for( i = 0 ; i < 4 ; i++ ){
          updatePos( curr->ptr[i] );
        }
        return;
    }

    //For external nodes
    updateAcceleration( curr );
    //Updating velocity
    vel[curr->index].vx += acc[curr->index].ax*dt;
    vel[curr->index].vy += acc[curr->index].ay*dt;

    //Updating the position
    pos[curr->index].x += vel[curr->index].vx*dt;
    pos[curr->index].y += vel[curr->index].vy*dt;

    //Resetting the accelerations
    acc[curr->index].ax = 0;
    acc[curr->index].ay = 0;
    return;
}

node* deleteTree(node* node){
    if (node == NULL) return NULL;
    int i;
    /* first delete all subtrees */
    for( i = 0 ; i < 4 ;i++)
      node->ptr[i] = deleteTree(node->ptr[i]);
    delete node;
    return NULL;
}
