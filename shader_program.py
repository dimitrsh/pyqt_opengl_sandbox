import os
import sys
import numpy as np
import OpenGL.GL as GL
from OpenGL.GL import (glCreateProgram, glLinkProgram, glDeleteProgram, 
                       glCreateShader, glShaderSource, glCompileShader, glAttachShader, glDeleteShader, 
                       glGetAttribLocation, glGetProgramiv, glGetShaderiv,
                       glGetUniformLocation, glGetShaderInfoLog, glGetProgramInfoLog, glBindAttribLocation,
                       GL_FLOAT, GL_TRUE, GL_FALSE, GL_COMPILE_STATUS, GL_LINK_STATUS, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER)

# this class is needed to create shader program and attach shaders to it. 

class ShaderProgram(object):
    def __init__(self, vertpath="", fragpath=""):
        # paths to files should be set correctly
        # yep it will contain paths to shaders.
        self.vertpath = vertpath
        self.fragpath = fragpath
        self.__DEBUG = False
        vflag = os.path.exists(self.vertpath)
        fflag = os.path.exists(self.fragpath)
        if not vflag:
            print ("Vertex shader file (--> %s <--) doesn't exist!"%self.vertpath)
        if not fflag:
            print ("Fragment shader file (--> %s <--) doesn't exist!"%self.fragpath)
        if not (fflag and vflag):
            sys.exit(1)
        self.attribs_dict  = {}
        self.attribs_count = 0
        self.initProgram()

    def setDebugMode(self, flag):
        self.__DEBUG = flag

    def getShader(self, shader_source, shader_type):
        try:
            shader_id = glCreateShader(shader_type)
            glShaderSource(shader_id, shader_source)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed:\n %s'%info)
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def analyze(self, vertex_text):
        # old shaders analyze : it binds attributes manually. Version #120 works fine. In case of newer one you should
        # do it by yourself: program.bindAttrib(<name>)
        # rewrite to the case of new ones.
        lines = vertex_text.split(';')
        comparer = lambda name : any(map(lambda x : x == name, sline))
        for line in lines:
            sline = line.split()
            main_beg = comparer('main')
            if main_beg:
                break
            attr_flag = comparer('attribute')
            if attr_flag:
                attr_name = sline[-1]
                self.bindAttrib(attr_name)

    def loadShader(self, path):
        source_file = open(path)
        shader_source = source_file.read()
        source_file.close()
        if self.__DEBUG:
            print "PATH : ", path
            print shader_source
            print "END OF SHADER ", path
        return shader_source

    def initProgram(self):
        # create unique shader program id
        self.program_id = glCreateProgram()
        # load and compile individual shaders
        vertsource = self.loadShader(self.vertpath)
        fragsource = self.loadShader(self.fragpath)
        vert_id = self.getShader(vertsource, GL_VERTEX_SHADER)
        frag_id = self.getShader(fragsource, GL_FRAGMENT_SHADER)
        # if it's ok, attach them to shader program
        glAttachShader(self.program_id, vert_id)
        glAttachShader(self.program_id, frag_id)
        self.analyze(vertsource) # in case of new (+#330 ;D) shaders - nothing will happen.
        # link program means make program obj with created executables for different programmable processors for shaders, 
        # that were attached.
        glLinkProgram(self.program_id)
        # if something went wrong
        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            # they should be deleted anyway
            glDeleteShader(vert_id)
            glDeleteShader(frag_id)
            raise RuntimeError("Error in program linking: %s"%info)
        # shaders are attached, program is linked -> full shader program with compiled executables is ready, 
        # no need in individual shaders ids, i suppose
        glDeleteShader(vert_id)
        glDeleteShader(frag_id)

    def bindAttrib(self, name):
        if not (name in self.attribs_dict):
            glBindAttribLocation(self.program_id, self.attribs_count, name)
            self.attribs_dict[name] = self.attribs_count
            self.attribs_count += 1
            return self.attribs_count - 1
        return self.attribs_dict[name]

    def attribLocation(self, name):
        if not (name in self.attribs_dict):
            return -1
        return self.attribs_dict[name]
        #return glGetAttribLocation(self.program_id, name)

    def uniformLocation(self, name):
        return glGetUniformLocation(self.program_id, name)

    def setUniformValue(self, name, *value):
        # 1-4 values of floats or ints(value[0] used to check the type)
        # or one numpy.array of floats or ints with shape (1,1)-(1,4)
        un_id = glGetUniformLocation(self.program_id, name)
        if self.__DEBUG:
            print "Set Uniform Vertex : ", self.vertpath
            print "Set Uniform Fragment : ", self.fragpath
            print "For '%s' name ID is %i"%(name, un_id)
        m = len(value)
        if m > 1:
            if isinstance(value[0], float):
                value = numpy.array(value, numpy.float32)
            else:
                value = numpy.array(value, numpy.int32)
        else:
            if m < 1:
                raise RuntimeError("Empty uniform value! Uniform variables in shader can only have 1-4 int32/float32 elements.")
            value = value[0]
        if isinstance(value, float):
            execution_command = 'GL.glUniform1f(%i, %s)'%(un_id, str(value))
            exec(execution_command)
            return
        elif value.shape[0] < 1 or value.shape[0] > 4:
            raise RuntimeError("Uniform variables in shader can only have 1-4 int32/float32 elements.")
        if un_id >= 0 and isinstance(value, np.ndarray):
            # please, don't try to do it at production and be carefully at home ;)
            n = value.shape[0]
            type_label = str(value[0].dtype)
            type_symb = 'i' if 'int' in type_label else 'f'
            line = ', '.join(map(str, value))
            execution_command = 'GL.glUniform%i%s(%i, %s)'%(n, type_symb, un_id, line)
            exec(execution_command)
        else:
            raise RuntimeError("Uniform id: %i, \n value type : %s \n Use int32/float32 numpy arrays only!"%(un_id, str(type(value))))

def main():
    # don't run this file - build will fall, because all of this is unnecessary without correct OpenGL context, 
    # which is set in triangle_test.py
    # i just want to show, how it should be called.
    program = ShaderProgram(vertpath="test_vert.glsl", fragpath="test_frag.glsl")

if __name__ == "__main__":
    main()