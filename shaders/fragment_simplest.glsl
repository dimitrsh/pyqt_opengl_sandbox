#version 120

varying vec3 out_color;

void main(void) {
    gl_FragColor = vec4(out_color, 1.0);
}