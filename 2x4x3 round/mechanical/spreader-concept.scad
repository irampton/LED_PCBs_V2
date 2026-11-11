// Preliminary concept only. Dimensions mm. PCB BACK face is z=0.
// Thermal interface is 0.3mm; metal contacts stop at z=-0.3.
// Obtain machining/clearance/flatness review before manufacture.
$fn=160;
difference() {
    union() {
        translate([0,0,-8.8]) cylinder(h=3,r=32);
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-8.639517, 2.333854], [-10.53347, 3.118355], [-9.653298, 5.243278], [-7.759345, 4.458777]]); // LED14
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-19.617949, 8.558977], [-21.83526, 9.477418], [-20.610673, 12.433832], [-18.393362, 11.515392]]); // LED15
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-27.4048, 9.619612], [-29.622111, 10.538053], [-28.397524, 13.494467], [-26.180213, 12.576027]]); // LED13
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-5.687725, 9.550381], [-6.606165, 11.767692], [-3.649751, 12.992279], [-2.731311, 10.774968]]); // LED2
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-7.819874, 19.924095], [-8.738314, 22.141406], [-5.781899, 23.365993], [-4.863459, 21.148682]]); // LED3
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-12.576027, 26.180213], [-13.494467, 28.397524], [-10.538053, 29.622111], [-9.619612, 27.4048]]); // LED1
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[2.731311, 10.774968], [3.649751, 12.992279], [6.606165, 11.767692], [5.687725, 9.550381]]); // LED17
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[8.558977, 19.617949], [9.477418, 21.83526], [12.433832, 20.610673], [11.515392, 18.393362]]); // LED18
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[9.619612, 27.4048], [10.538053, 29.622111], [13.494467, 28.397524], [12.576027, 26.180213]]); // LED16
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[9.550381, 5.687725], [11.767692, 6.606165], [12.992279, 3.649751], [10.774968, 2.731311]]); // LED5
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[19.924095, 7.819874], [22.141406, 8.738314], [23.365993, 5.781899], [21.148682, 4.863459]]); // LED6
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[26.180213, 12.576027], [28.397524, 13.494467], [29.622111, 10.538053], [27.4048, 9.619612]]); // LED4
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[10.774968, -2.731311], [12.992279, -3.649751], [11.767692, -6.606165], [9.550381, -5.687725]]); // LED20
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[19.617949, -8.558977], [21.83526, -9.477418], [20.610673, -12.433832], [18.393362, -11.515392]]); // LED21
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[27.4048, -9.619612], [29.622111, -10.538053], [28.397524, -13.494467], [26.180213, -12.576027]]); // LED19
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[5.687725, -9.550381], [6.606165, -11.767692], [3.649751, -12.992279], [2.731311, -10.774968]]); // LED8
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[7.819874, -19.924095], [8.738314, -22.141406], [5.781899, -23.365993], [4.863459, -21.148682]]); // LED9
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[12.576027, -26.180213], [13.494467, -28.397524], [10.538053, -29.622111], [9.619612, -27.4048]]); // LED7
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-2.731311, -10.774968], [-3.649751, -12.992279], [-6.606165, -11.767692], [-5.687725, -9.550381]]); // LED23
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-8.558977, -19.617949], [-9.477418, -21.83526], [-12.433832, -20.610673], [-11.515392, -18.393362]]); // LED24
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-9.619612, -27.4048], [-10.538053, -29.622111], [-13.494467, -28.397524], [-12.576027, -26.180213]]); // LED22
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-7.759345, -4.458777], [-9.653298, -5.243278], [-10.53347, -3.118355], [-8.639517, -2.333854]]); // LED11
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-16.074261, -7.902928], [-17.968214, -8.687429], [-18.848386, -6.562506], [-16.954433, -5.778005]]); // LED12
        translate([0,0,-5.8]) linear_extrude(height=5.5) polygon(points=[[-26.180213, -12.576027], [-28.397524, -13.494467], [-29.622111, -10.538053], [-27.4048, -9.619612]]); // LED10
    }
    for (x=[-3.5,3.5]) {
        translate([x,0,-10]) cylinder(h=12,d=2.7);
    }
}