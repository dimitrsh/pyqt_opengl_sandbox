#version 120

attribute vec3 vin_coord;
attribute vec3 vin_color;
attribute float vin_radius;

varying vec2 center;
varying float radius;
varying vec3 out_color;
varying float depth_value;

void main() {
    vec4 vin_coord_ = vec4(vin_coord, 1.0);
    gl_Position   = gl_ModelViewProjectionMatrix * vin_coord_;
    gl_FrontColor = gl_Color;
    out_color = vin_color;
}