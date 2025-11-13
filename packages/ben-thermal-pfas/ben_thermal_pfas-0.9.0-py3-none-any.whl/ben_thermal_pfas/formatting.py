from .parsers import g16_input

def choose_input_charge(file_name:str,default_charge =0):
    """Chooses a charge based on the name of a file
    
Parameters  
----------

file_name (str): the name of the input file

default_charge (int): If the charge can't be found in the file name, then it uses this value

Returns
-------
(int) the charge"""
    potential_charges = {
        "_c0_":0, 
        "_cm1_":-1,
        "_cm2_":-2, 
        "_c1_":1,
        "_c2_":2,    
    }

    for option in potential_charges.keys():
        if option in file_name:
            return potential_charges[option]
    print(f"Charge not specified in file name. Returning {default_charge} by default.")
    return default_charge


def choose_input_spin(file_name:str,default_spin_multiplicity =1):
    """Chooses a spin multiplicity based on the name of a file
    
Parameters  
----------

file_name (str): the name of the input file

default_spin_multiplicity (int): If the spin multiplicity can't be found in the file name, then it uses this value

Returns
-------
(int) the spin multiplicity"""   
    potential_spin_multiplicity = { 
        "_s1":1,
        "_s2":2, 
        "_s3":3,
        "_s4":4,    
    }

    for option in potential_spin_multiplicity.keys():
        if option in file_name:
            return potential_spin_multiplicity[option]
    print(f"Spin multiplicity not specified in file name. Returning {default_spin_multiplicity} by default.")
    return default_spin_multiplicity



def base_modify_input(input_file:str,temperature=273.15,pressure=1,eps=78,transition_state = False,functional="m062x",basis="6-311+g(d,p)"):
    """
    
Paramters
---------
input_file (str): path to the file.

temperature (float): the temperature in K of the system.

pressure (float): the pressure in atm of the system.

eps (float): the dielectric constant.

transtion_state (bool): whether or not opimizing a transition state

functional (str): the functional of the calculation

basis (str): the basis set

Returns
-------
None: writes to the input file"""
    chosen_input = f"opt=(calcfc,maxcycles=500) freq=(noraman) {functional} {basis} temperature={temperature} pressure={pressure} scrf=read"
    if transition_state:
        chosen_input_input = f"opt=(calcfc,ts,noeigen,maxcycles=500) freq=(noraman) {functional} {basis} temperature={temperature} pressure={pressure} scrf=read"

    my_file = g16_input.from_file(input_file)
    my_file.charge = choose_input_charge(input_file)
    my_file.spin_multiplicity = choose_input_spin(input_file)
    my_file.input_line = chosen_input
    my_file.bottom_file_inputs = f"eps={eps}"

    my_file.check_point_file_name= my_file.check_point_file_name.split("\\")[-1]
    my_file.write_file()
