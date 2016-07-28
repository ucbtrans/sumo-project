clear all;
close all;
clc;

%%
dt = 0.01;
a = 1.0; b = 4.5; tau = 2.05; l = 5; gmin = 4;

sim_steps = ((270-240)/dt);
times = 240:dt:270;

v1 = [0]; x1 = [0];
for i = 1:sim_steps
    v1(i+1) = min(20,a*dt*(i-1));
    x1(i+1) = x1(i) + v1(i+1)*dt;
end

v2 = [0]; x2 = [-9];
g = [x1(1)-x2(1)];
for j = 1:sim_steps

    gt = g(j);
    gd = gmin + v1(j)*tau;
    vbar = (v1(j) + v2(j))/2;
    vsafe = v1(j) + (gt-gd)/(vbar/b+tau)
    v2(j+1) = max([0,min([20,v2(j)+a*dt,...
        vsafe])]);
    x2(j+1) = x2(j) + v2(j+1)*dt;
    g(j+1) = x1(j+1) - x2(j+1) - l;
end

plot(times,v1,'r-',times,v2,'b-');
legend('veh1','veh2')
    
    