# -*- coding: utf-8 -*-

# PyQt4 imports
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtOpenGL

# OpenGL
from OpenGL import GLU
from OpenGL import GLUT
from OpenGL import GL
from OpenGL.arrays import ArrayDatatype

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from shader_program import ShaderProgram
import numpy

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

VERTEX_SHADER_SOURCE_2D_SIMPLE = os.path.join(CUR_DIR, "shaders", "vertex_simplest.glsl")
FRAGMENT_SHADER_SOURCE_2D_SIMPLE = os.path.join(CUR_DIR, "shaders", "fragment_simplest.glsl")

def getVAO(program, coords, colors, radii):
    # it generates vao and vbos.
    vao_id = glGenVertexArrays(1)
    glBindVertexArray(vao_id)
    vbo_id = glGenBuffers(3)

    fillBuffers(program, vbo_id, coords, colors, radii)

    glBindVertexArray(0)
    #glDisableVertexAttribArray(pos_id)
    #glDisableVertexAttribArray(col_id)
    #glDisableVertexAttribArray(rad_id)

    return vao_id, vbo_id # number for VAO and 3 numbers for VBOs. vbos are already filled.

def fillBuffers(program, vbo_id, coords, colors, radii):
	# use shader program named 'program' and allow the attributes to be used from VBOs
	# vbo_id - list for three vbo. This should mean, that vao is already created.
    rad_id = program.attribLocation('vin_radius') # float
    pos_id = program.attribLocation('vin_coord')  # vec3
    col_id = program.attribLocation('vin_color')  # vec3

    glBindBuffer(GL_ARRAY_BUFFER, vbo_id[0])
    glBufferData(GL_ARRAY_BUFFER, coords, GL_STATIC_DRAW)
    glVertexAttribPointer(pos_id, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(pos_id) # allow to watch
    # repeat it for colors.
    glBindBuffer(GL_ARRAY_BUFFER, vbo_id[1])
    glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)
    glVertexAttribPointer(col_id, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(col_id)
    #####
    glBindBuffer(GL_ARRAY_BUFFER, vbo_id[2])
    glBufferData(GL_ARRAY_BUFFER, radii, GL_STATIC_DRAW)
    glVertexAttribPointer(rad_id, 1, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(rad_id)

    glBindBuffer(GL_ARRAY_BUFFER, 0)

def changeVAO(program, vao_id, vbo_id, coords, colors, radii):
    glBindVertexArray(vao_id) # 
    fillBuffers(program, vbo_id, coords, colors, radii)
    glBindVertexArray(0)


class Scene2D(QtOpenGL.QGLWidget):
    def __init__(self, parent = None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        #self.structure_n_atoms_changed.connect(self.TEST)

        self.parent = parent

        self.lineWidth = 3.0
        self.pointSize = 4.0

        self.lines = []
        self.points = []

        self.lines = numpy.array(self.lines)
        self.points = numpy.array(self.points)

        self.drawAllLines = self.drawSimpleLines

        # some actions log.
        # every click, press or smth else should produce 

        self.background_color = numpy.zeros(4, numpy.float32) + 1.0
        #self.drawtype = 'simple'

        self.drawAllPoints = self.drawSimplePoints

        self.width = 800
        self.height = 600
        self.setInitialState()
        

    def initializeGL(self):
        # contain the main data
        self.points_vao_id = None
        # to clear it properly or to rewrite
        self.points_vbo_id = None # positions, color, radii.
        ###
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)

        self.shader_simple = ShaderProgram(vertpath = VERTEX_SHADER_SOURCE_2D_SIMPLE, fragpath = FRAGMENT_SHADER_SOURCE_2D_SIMPLE)
        self.main_shader_program = self.shader_simple

        self.qglClearColor(QtGui.QColor(255, 255, 255))
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_MODELVIEW)

    def updateVAO(self, coords, colors, radii):
        # only here this should be done
        flatten_coords = numpy.array(coords.flatten(), numpy.float32)
        flatten_colors = numpy.array(colors.flatten(), numpy.float32)
        radii = numpy.array(radii, numpy.float32)
        #print radii[:10]
        self.atoms_current_radii = radii
        #print "update Shader program : ", self.main_atoms_shader_program
        if self.atoms_vao_id:
            #print "Updating spheres"
            changeVAO(self.main_atoms_shader_program, self.atoms_vao_id, self.atoms_vbo_id, 
                                    flatten_coords, flatten_colors, radii)
        else:
            #print "Init spheres"
            self.atoms_vao_id, self.atoms_vbo_id = getVAO(self.main_atoms_shader_program, 
                                                                        flatten_coords, flatten_colors, radii)

    def setInitialState(self):
        #self.main_shader_program = self.shader_simple
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -65)
        # PROJECTION MATRIX UPDATE
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.identity = glGetDouble(GL_PROJECTION_MATRIX)
        self.aspect = self.width / float(self.height)
        GLU.gluPerspective(45.0, self.aspect, 0.2, 400000.0)
        self.proj_matrix = glGetDouble(GL_PROJECTION_MATRIX)
        glMatrixMode(GL_MODELVIEW)

        self.updateGL()

    def resizeGL(self, width, height):
        if height == 0: height = 1
        #glViewport(self.posx, self.posy, self.posx + width, self.posy + height)
        glViewport(0, 0, width, height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.identity = glGetDouble(GL_PROJECTION_MATRIX)
        self.aspect = width / float(height)

        self.width = width
        self.height = height
        GLU.gluPerspective(45.0, self.aspect, 0.2, 400000.0)

        self.proj_matrix = glGetDouble(GL_PROJECTION_MATRIX)
        glMatrixMode(GL_MODELVIEW)
        # only here should it be. Set aspect, viewport in shaders.
        glUseProgram(self.main_shader_program.program_id)
        viewport_data = numpy.array([0.0, 0.0, float(self.width), float(self.height)], numpy.float32)
        aspect_data = numpy.array([self.aspect], numpy.float32)
        self.main_shader_program.setUniformValue('viewport', viewport_data)
        self.main_shader_program.setUniformValue('aspect', aspect_data)
        glUseProgram(0)

    def lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glLightModelfv(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.5,0.5,0.5, 0.5])


        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.9,0.9,0.9,1]);
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)


        ambient = [0.6, 0.6, 0.6, 0.6]
        diffuse = [0.8, 0.6, 1.0, 0.8]
        specular = [0,0, 0, 1.0]
        position = [-10, 20, 10]

        glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, ambient)
        glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, diffuse)
        glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, position)
        glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, specular)

    def blend(self):
        glEnable(GL_ALPHA_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

     
    def paintGL(self):
        print "Updating"
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.lighting()
        self.drawAllLines(self.lineWidth)
        self.drawAllPoints(self.pointSize)

    def drawSimplePoints(self, point_size):
        glPointSize(point_size) # 4.0
        glUseProgram(self.main_atoms_shader_program.program_id)
        # use vao with coords and colors buffers for triangle
        glBindVertexArray(self.atoms_vao_id)
        # how to draw
        glDrawArrays(GL_POINTS, 0, self.points.shape[0])
        # turn this off.
        glUseProgram(0)
        glBindVertexArray(0)

    def drawColorData(self, structure):
        if self.showColorTypeStruct:
            atom_draw = self.drawAtom
            if structure.n_atoms > 0: 
                crd = structure.coords
                if self.show_atoms:
                    self.cur_call_list = self.atom
                    map(atom_draw,  zip(crd, structure.atom_types))
                else:
                    glEnable(GL_LIGHTING)
                    glDisable(GL_POINT_SMOOTH)
                    if hasattr(structure, "atoms"):
                        if self.view_need_update("TYPES"):
                            self.updateVAO_right_colors(structure)
                        self.drawAtomsVAO(structure)


    def drawSimpleLines(self, linewidth):
        glDisable(GL_LIGHT0)
        glLineWidth(linewidth) # 3
        glColor3d(0,0,0) # black lines

        glVertexPointerd(self.lines)
        glEnableClientState(GL_VERTEX_ARRAY)
        glDrawArrays(GL_LINES, 0, self.lines.shape[0])

        glEnable(GL_LIGHT0)
        glLineWidth(self.defaultLineWidth) # 2
