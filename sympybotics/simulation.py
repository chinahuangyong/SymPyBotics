import numpy
import sympybotics

class Simulation:

    def __init__(self, rbt, parms, sampling_time):

        self.rbt = rbt
        self.parms = parms
        self.sampling_time = sampling_time
        self.dof = self.rbt.rbtdef.dof

        self.q = numpy.zeros(self.dof)
        self.dq = numpy.zeros(self.dof)
        self.ddq = numpy.zeros(self.dof)
        self.tau = numpy.zeros(self.dof)
        self.tau_e = numpy.zeros(self.dof)

        self.M_func = sympybotics.robotcodegen.robot_code_to_func('python', self.rbt.M_code, 'M', 'inertia_func', self.rbt.rbtdef)
        self.c_func = sympybotics.robotcodegen.robot_code_to_func('python', self.rbt.c_code, 'c', 'coriolis_func', self.rbt.rbtdef)
        self.g_func = sympybotics.robotcodegen.robot_code_to_func('python', self.rbt.g_code, 'g', 'gravity_func', self.rbt.rbtdef)

  
    # calculate derivative of state value
    def update_states(self, tau, tau_e):
        
        exec(self.M_func)
        exec(self.c_func)
        exec(self.g_func)

        global sin, cos, sign
        sin = numpy.sin
        cos = numpy.cos
        sign = numpy.sign
 
        self.M = numpy.array( locals()['inertia_func'](self.parms, self.q)).reshape(self.dof, self.dof)
        self.c = numpy.array( locals()['coriolis_func'](self.parms, self.q, self.dq))
        self.g = numpy.array( locals()['gravity_func'](self.parms, self.q))

        self.ddq = numpy.linalg.solve(self.M, tau - self.c - self.g - tau_e)    
        self.dq = self.dq + self.ddq * self.sampling_time
        self.q = self.q + self.dq * self.sampling_time