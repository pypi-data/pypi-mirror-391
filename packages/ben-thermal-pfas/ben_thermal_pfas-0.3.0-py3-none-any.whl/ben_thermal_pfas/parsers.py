from .molecule_structures import xyz_atom,xyz_molecule


class g16_input:
    def __init__(self,charge:int,spin_multiplicity:int,input_line:str,input_xyz_molecule:xyz_molecule,file_name:str,check_point_file_name:str,nproc:int=36,mem:int=5,notes_line="notes line",bottom_file_inputs = ""):
        """A g16_input file object for basic input
        
Parameters
----------


charge (int): the charge of the system

spin_multiplicity (int): the spin multiplicity of the system

input_line (str): the input line for the file

input_xyz_molecule (xyz_molecule): the geometry of the molecule

file_name (str): the name of the input file.

check_point_file_name (str): the name of the checkpoint file

nproc (int): the number of processors used for the job.

mem (int): the memmory allocated for the job

notes_line (str): information put in the notes line of the input file

bottom_file_inputs (str): information placed at the bottom of the file.

Returns
-------

g16_input"""

        self.charge = charge
        self.spin_multiplicity = spin_multiplicity
        self.input_line = input_line
        self.xyz_molecule = input_xyz_molecule
        self.file_name = file_name
        self.check_point_file_name = check_point_file_name
        self.nproc = nproc
        self.mem = mem
        self.notes_line = notes_line
        self.bottom_file_inputs = bottom_file_inputs

    def __str__(self):
        return f"""%chk={self.check_point_file_name}
%nproc={self.nproc}
%mem={self.mem}GB
#p {self.input_line}

{self.notes_line}

{self.charge} {self.spin_multiplicity}
{str(self.xyz_molecule)}

{self.bottom_file_inputs}


"""
    def write_file(self,new_file_name=None):
        """Writes an input file. If no file name is specified, then it formats the original file.
    Parameters
    ----------
    
    file_name (str): optional name for file to write to.
    
    Returns
    -------
    None, writes  input file"""
        if new_file_name == None:
            with open(self.file_name,"w") as file:
                file.write(str(self))
        else:
            with open(new_file_name,"w") as file:
                file.write(str(self))
        pass

    @classmethod
    def from_file(cls,file_name:str):
        """Creates a g16 input object from a specified file.
        Parameters
        ----------
        
        file_name (str): path to input file
        
        Returns
        -------
        g16_input"""
        file_name = file_name
        charge = None
        spin_multiplicity = None
        input_line = ""
        this_xyz_molecule = []
        check_point_file_name = None
        nproc = 36
        mem = 5
        notes_line = None
        bottom_file_inputs = ""

        with open(file_name,"r") as file:
            file_lines = file.readlines()
        
        file_lines = [line.strip() for line in file_lines]

        prev_num_blank_lines = 0
        num_blank_lines = 0

        for line in file_lines:
            prev_num_blank_lines = num_blank_lines
            if line == "":
                num_blank_lines += 1
                continue
            if line[:5] == "%chk=":
                check_point_file_name = line.split("=")[-1]
            if line[:7] == "%nproc=":
                nproc = int(line.split("=")[-1])
            if line[:5] == "%mem=":
                mem = int(line.split("=")[-1][:-2])
            if line[0] == "#" or input_line !="" and num_blank_lines == 0:
                split_line = line.split()
                if line[0][0] == "#":
                    input_line += " ".join(line[1:])
                else:
                    input_line += " ".join(line[1:])
            if num_blank_lines == 1:
                notes_line += line
            if num_blank_lines == 2:
                if charge == None and spin_multiplicity == None:
                    split_line = line.split()
                    charge = int(split_line[0])
                    spin_multiplicity = int(split_line[1])
                else:
                    this_xyz_molecule.append(xyz_atom.from_string(line))
            if num_blank_lines >2 :
                bottom_file_inputs += line + "\n"
                if prev_num_blank_lines != num_blank_lines:
                    bottom_file_inputs += "\n"
            bottom_file_inputs = bottom_file_inputs.strip()

        if notes_line == None:
            notes_line = "notes line"
        if check_point_file_name == None:
            check_point_file_name = file_name.split(".")[0]+".chk"
        
        return cls(charge,spin_multiplicity,input_line,xyz_molecule(this_xyz_molecule),file_name,check_point_file_name,nproc,mem,notes_line)





