Non-bonded interactions
=======================
   
**Overview**

The pygamd MD engine provides a few of functions for non-bonded interactions.
However, it supports well self-defined analytical functions via writting codes of 
device function in script.

==============================    ============================
:ref:`non-bonded`                 :py:class:`force.nonbonded`
:ref:`self-defined-function`      :py:class:`force.nonbonded`
:ref:`non-bonded_c`               :py:class:`force.nonbonded_c`
:ref:`self-defined-function_c`    :py:class:`force.nonbonded_c`
==============================    ============================


.. _non-bonded:

Non-bonded functions
--------------------

Description:

   The function describing non-bonded interactions could be either the one called from non-bonded interaction function libary, or the one defined by user himself in script.
   Non-bonded interaction function libary contains Lennard-Jones function named as 'lj' and harmonic function named as 'harmonic'.
   
   Lennard-Jones function ('lj')
    .. math::
        :nowrap:

        \begin{eqnarray*}
        V_{\mathrm{LJ}}(r)  = & 4 \epsilon \left[ \left( \frac{\sigma}{r} \right)^{12} -
                          \alpha \left( \frac{\sigma}{r} \right)^{6} \right] & r < r_{\mathrm{cut}} \\
                            = & 0 & r \ge r_{\mathrm{cut}} \\
        \end{eqnarray*}

    The following coefficients must be set per unique pair of particle types:

    - :math:`\epsilon` - the depth of the potential well (in energy units)
    - :math:`\sigma` - the collision diameter (in distance units)
    - :math:`\alpha` - the factor of attraction (unitless)
    - :math:`r_{\mathrm{cut}}` - cutoff radius (in distance units)
      - *note*: equal to or smaller than the global rcut specified in ``force.nonbonded``
   
   
   Harmonic function ('harmonic')
    .. math::
        :nowrap:

        \begin{eqnarray*}
        V_{\mathrm{H}}(r) = \frac{1}{2}\alpha \left( r - r_{\mathrm{cut}} \right)^{2}, r < r_{\mathrm{cut}} 
        \end{eqnarray*}

    Coefficients:

    - :math:`\alpha` - spring constant (in units of energy/distance^2)
    - :math:`r_{\mathrm{cut}}` - cutoff radius (in distance units)
      - *note*: equal to or smaller than the global rcut specified in ``force.nonbonded`` 

.. py:class:: force.nonbonded(info, rcut, func, exclusion=None)

   Constructor of non-bonded interaction calculation object.
	  
   :param info: system information.
   :param rcut: cut-off radius of interactions.
   :param func: function name.
   :param exclusion: a python list of exclusions, the candidates are 'bond', 'angle', 'dihedral', 
                the default is None.    

   .. py:function:: setParams(type_i, type_j, param)
 
      specifies interaction parameters with type_i, type_j, a list of parameters.  
   
   Example::
   
      fn = pygamd.force.nonbonded(info=mst, rcut=3.0, func='lj')
      fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 3.0])
      app.add(fn)


      fn = pygamd.force.nonbonded(info=mst, rcut=3.0, func='lj', exclusion=['bond'])
      fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 3.0])
      app.add(fn)


.. _self-defined-function:

Self-defined functions
----------------------

Description:

   The device function for non-bonded interactions could be written in script and conveyed 
   to kernel funciton for calculation. The function has three parameters where rsq, param, and fp
   are square of distance, interaction parameters, and force and potential, respectively.
   
   With the potential form of non-bonded interactions :math:`p(r)`, the expression of parameters in script are: 

   * p = :math:`p(r)`
   * f = :math:`-(\partial p(r)/\partial r)(1/r)`

   Function code template::
   
   		@cuda.jit(device=True)
		def func(rsq, param, fp):
			rcut = param[0]
			p1 = param[1]
			p2 = param[2]
			p3 = param[3]
			...
			if rsq<rcut*rcut:
				calculation codes
				...
				fp[0]=f
				fp[1]=p
				
		fn = pygamd.force.nonbonded(info, rcut, func)
		fn.setParams(type_i, type_j, param=[rcut, p1, p2, p3, ...])
		....
		app.add(fn)		
   
   Example::
   
		from numba import cuda
		import numba as nb
		
		@cuda.jit(device=True)
		def lj(rsq, param, fp):
			epsilon = param[0]
			sigma = param[1]
			alpha = param[2]
			rcut = param[3]
			if rsq<rcut*rcut:
				sigma2 = sigma*sigma
				r2inv = sigma2/rsq;
				r6inv = r2inv * r2inv * r2inv;
				f = nb.float32(4.0) * epsilon * r2inv * r6inv * (nb.float32(12.0) 
					* r6inv - nb.float32(6.0) * alpha)/sigma2
				p = nb.float32(4.0) * epsilon * r6inv * ( r6inv - nb.float32(1.0))
				fp[0]=f
				fp[1]=p
				
		fn = pygamd.force.nonbonded(info=mst, rcut=3.0, func=lj)
		fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 3.0])
		app.add(fn)	
 
.. _non-bonded_c:

Non-bonded functions for charged beads
--------------------------------------

Description:

   The function describing non-bonded interactions including electrostatic part could be either the one called from non-bonded interaction function libary, or the one defined by user himself in script.
   
   Lennard-Jones-coulomb function ('lj_coulomb')
    .. math::
        :nowrap:

        \begin{eqnarray*}
        V_{\mathrm{LJ}}(r)  = & 4 \epsilon \left[ \left( \frac{\sigma}{r} \right)^{12} -
                          \alpha \left( \frac{\sigma}{r} \right)^{6} \right] + f\frac{q_{i} q_{j}}{\epsilon_{r}r} & r < r_{\mathrm{cut}} \\
                            = & 0 & r \ge r_{\mathrm{cut}} \\
        \end{eqnarray*}

    Following coefficients need being set per pair of particle types:

    - :math:`\epsilon` - the depth of the potential well (in energy units)
    - :math:`\sigma` - the collision diameter (in distance units)
    - :math:`\alpha` - the factor of attraction (unitless)
    - :math:`\epsilon_{r}` - dielectric coefficient : :math:`f= 1/4\pi \epsilon_0=138.935\text{ }kJ\text{ }mol^{-1}\text{ }nm\text{ }e^{-2}`
    - :math:`r_{\mathrm{cut}}` - cutoff radius (in distance units)
      - *note*: equal to or smaller than the global rcut specified in ``force.nonbonded_c``
   
.. py:class:: force.nonbonded_c(info, rcut, func, exclusion=None)

   Constructor of non-bonded interaction calculation object.
	  
   :param info: system information.
   :param rcut: cut-off radius of interactions.
   :param func: function name.
   :param exclusion: a python list of exclusions, the candidates are 'bond', 'angle', 'dihedral', 
                the default is None.    

   .. py:function:: setParams(type_i, type_j, param)
 
      specifies interaction parameters with type_i, type_j, a list of parameters.  
   
   Example::
   
      fn = pygamd.force.nonbonded_c(info=mst, rcut=3.0, func='lj_coulomb')
      fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 15.0, 3.0])
      app.add(fn)


      fn = pygamd.force.nonbonded_c(info=mst, rcut=3.0, func='lj_coulomb', exclusion=['bond'])
      fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 15.0, 3.0])
      app.add(fn)


.. _self-defined-function_c:

Self-defined functions for charged beads
----------------------------------------

Description:

   The device function for non-bonded interactions could be written in script and conveyed 
   to kernel funciton for calculation. The function has three parameters where rsq, qi, qj, param, and fp
   are the square of distance, qi and qj, interaction parameters, and force and potential, respectively.
   
   With the potential form of non-bonded interactions :math:`p(r)`, the expression of parameters in script are: 

   * p = :math:`p(r)`
   * f = :math:`-(\triangle p(r)/\triangle r)(1/r)`

   Function code template::
   
   		@cuda.jit(device=True)
		def func(rsq, qi, qj, param, fp):
			rcut = param[0]
			p1 = param[1]
			p2 = param[2]
			p3 = param[3]
			...
			if rsq<rcut*rcut:
				calculation codes
				...
				fp[0]=f
				fp[1]=p
				
		fn = pygamd.force.nonbonded_c(info, rcut, func)
		fn.setParams(type_i, type_j, param=[rcut, p1, p2, p3, ...])
		....
		app.add(fn)
   
   Example::
   
		from numba import cuda
		import numba as nb
		
		@cuda.jit(device=True)
		def lj_coulomb(rsq, qi, qj, param, fp):
			epsilon = param[0]
			sigma = param[1]
			alpha = param[2]
			epsilonr = param[3]
			rcut = param[4]
			coulomb_eff = 138.935/epsilonr
			if rsq<rcut*rcut:
				sigma2 = sigma*sigma
				r2inv = sigma2/rsq;
				r6inv = r2inv * r2inv * r2inv;
				f = nb.float32(4.0) * epsilon * r2inv * r6inv * (nb.float32(12.0) 
					* r6inv - nb.float32(6.0) * alpha)/sigma2 + coulomb_eff*qi*qj*r2inv*rinv
				p = nb.float32(4.0) * epsilon * r6inv * ( r6inv - nb.float32(1.0)) 
					+ coulomb_eff*qi*qj*rinv
				fp[0]=f
				fp[1]=p
				
		fn = pygamd.force.nonbonded_c(info=mst, rcut=3.0, func=lj_coulomb)
		fn.setParams(type_i="a", type_j="a", param=[1.0, 1.0, 1.0, 15.0, 3.0])
		app.add(fn)	
 