#!/usr/bin/env python

import sys
import numpy as np
import ase
import os
from ase import Atoms
from ase.io import read, write, lammpsdata
from ase import neighborlist as nbl
from ase.io.trajectory import Trajectory


if __name__ == "__main__":
    for file in sys.argv[1:]:
        DIR='../neighborlist/'+'/'.join(file.split('/')[-2:])+'/'
        try:
            os.mkdir(DIR)
        except OSError as error:
            continue
        ATOMS = read(file,format='espresso-in')
        # for atom in ATOMS:
        #     if atom.symbol=='He':
        #         atom.symbol='Si'
        # mep=lammpsdata.read_lammps_data(file,style='atomic',sort_by_id=True)
        nl=nbl.build_neighbor_list(ATOMS,[2.5]*len(ATOMS),skin=0,bothways=True,self_interaction=False)


        for atom in ATOMS:
            output=[]
            atoms=ATOMS.copy()
            # ind=np.array(range(len(ATOMS)))

            hpos=atoms[atom.index].position.copy()
            indices, offsets = nl.get_neighbors(atom.index)
            if len(indices)<10:
                print(len(indices))
            for i, offset in zip(indices, offsets):
                atoms.positions[i]=atoms.positions[i] + np.dot(offset, atoms.get_cell())-hpos
            D=[np.dot(pos,pos) for pos in atoms.positions[indices]]
            nbind=np.argsort(np.array(D))
            output.append(atoms[indices[nbind[0:10]]])
            # print(output)
            write(DIR+str(atom.index)+'.xyz',output)
    # write('final.gif', mep,format='gif', interval=1)
