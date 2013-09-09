#!/usr/bin/env python
# robot_gr1.py - example of direct GR(1) specification
#
# 21 Jul 2013, Richard M. Murray (murray@cds.caltech.edu)
"""
This example illustrates the use of TuLiP to synthesize a reactive
controller for a GR(1) specification.  We code the specification
directly in GR(1) form and then use TuLiP to synthesize a reactive
controller.

The system is modeled as a discrete transition system in which the
robot can be located anyplace no a 2x3 grid of cells:

    +----+----+----+
    | X3 | X4 | X5 |
    +----+----+----+
    | X0 | X1 | X2 |
    +----+----+----+

The robot is allowed to transitions between any two adjacent cells;
diagonal motions are not allowed.  The robot should continuously
revisit the cell X5.

The environment consists of a single state called 'park' that
indicates that the robot should move to cell X0.

The system specification in its simplest form is given by

  []<>park -> []<>X5 && [](park -> <>X0)

We must convert this specification into GR(1) form, which in TuLiP
will be a specification of the form:

  env_init && []env_safe && []<>env_prog ->
      sys_init && []sys_safe && []<>sys_prog
"""

# Import the packages that we need
from tulip import spec, synth


#
# Environment specification
#
# The environment can issue a park signal that the robot just respond
# to by moving to the lower left corner of the grid.  We assume that
# the park signal is turned off infinitely often.
#
env_vars = {'park'}
env_init = set()                # empty set
env_safe = set()                # empty set
env_prog = '!park'              # []<>(!park)

#
# System dynamics
#
# The system specification describes how the system is allowed to move
# and what the system is required to do in response to an environmental
# action.  
#
def mutex(varnames):
    mutex = set()
    if len(varnames) > 1:
        for p in varnames:
            mut_str = p+' -> ! ('
            first = True
            for q in varnames:
                if p != q:
                    if not first:
                        mut_str += ' || '
                    first = False
                    mut_str+=q
            mut_str += ')'
            mutex |= {mut_str}
    return mutex
    
    
sys_vars = {'X0', 'X1', 'X2', 'X3', 'X4', 'X5'}
sys_init = {'X0'}
sys_safe = {
    'X0 -> next(X1 || X3)',
    'X1 -> next(X0 || X4 || X2)',
    'X2 -> next(X1 || X5)',
    'X3 -> next(X0 || X4)',
    'X4 -> next(X3 || X1 || X5)',
    'X5 -> next(X4 || X2)',
}

sys_safe |= mutex({'X0', 'X1', 'X2', 'X3', 'X4', 'X5'})

sys_prog = set()                # empty set

# 
# System specification
#
# The system specification is that the robot should repeatedly revisit
# the upper right corner of the grid while at the same time responding
# to the park signal by visiting the lower left corner.  The LTL
# specification is given by 
#
#     []<> X5 && [](park -> <>X0)
#
# Since this specification is not in GR(1) form, we introduce an
# environment variable X0reach that is initialized to True and the
# specification [](park -> <>X0) becomes
#
#     [](next(X0reach) == X0 || (X0reach && !park))
#

# Augment the system description to make it GR(1)
sys_vars |= {'X0reach'}
sys_init |= {'X0reach'}
sys_safe |= {'next(X0reach) == X0 || (X0reach && !park)'}
sys_prog |= {'X0reach'}

# Create a GR(1) specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)

#
# Controller synthesis
#
# At this point we can synthesize the controller using one of the available
# methods.  Here we make use of gr1c.
#

ctrl = synth.synthesize('jtlv', specs)


# if the spec is unrealizable, ctrl is a list of counterexamples
if isinstance(ctrl, list):
    print "Counterexample: environment winning initial states: \n",ctrl

else:
# Generate a graphical representation of the controller for viewing,
# or a textual representation if pydot is missing.
    if not ctrl.save('robot_gr1.png', 'png'):
        print(ctrl)
    ctrl.states.select_current([0])
    ctrl.simulate(inputs_sequence='random', iterations=100)
