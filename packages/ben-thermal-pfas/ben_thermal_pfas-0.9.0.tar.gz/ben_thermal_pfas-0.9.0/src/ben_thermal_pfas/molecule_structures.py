import numpy as np

class xyz_atom:
    def __init__(self,atom_type:str,x_coord:float,y_coord:float,z_coord:float):
        self.atom_type = atom_type
        self.coords = np.array([x_coord,y_coord,z_coord])

    def __str__(self):

        return f"{self.atom_type}    {self.coords[0]:.8f}    {self.coords[1]:.8f}    {self.coords[2]:.8f}"
    
    def as_array(self):
        return [self.atom_type,self.coords]
    
    def translate_atom(self,translation_vector:np.array):
        self.coords = self.coords + translation_vector
    
    @classmethod
    def from_string(cls,atom_string:str):
        atom_list = atom_string.strip().split()
        atom_type = atom_list[0]
        x_coord = float(atom_list[1])
        y_coord = float(atom_list[2])
        z_coord = float(atom_list[3])
        return cls(atom_type,x_coord,y_coord,z_coord)

    

class xyz_molecule:
    def __init__(self,xyz_atom_array:np.array):
        self.xyz_atom_array = np.array(xyz_atom_array)

    def __str__(self):
        final_string = ""
        for atom in self.xyz_atom_array:
            final_string += str(atom)+"\n"
        return final_string.strip()
    
    def as_array(self):
        return [atom.as_array() for atom in self.xyz_atom_array]
    
    def add_atom(self,new_xyz_atom:xyz_atom):
        np.append(self.xyz_atom_array,new_xyz_atom)

    def translate_molecule(self,translation_vector:np.array):
        for atom in self.xyz_atom_array:
            atom.translate_atom(translation_vector)