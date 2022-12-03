pairs = galamost.PairForceTable(all_info, neighbor_listSR,  npoints_in_table)
pairs.setPotential('PEB','PEB', 'table_PEB-PEB.dat', 0 ,1)
pairs.setPotential('PEB','PEO', 'table_PEB-PEO.dat', 0 ,1)
pairs.setPotential('PEB','PEC', 'table_PEB-PEC.dat', 0 ,1)
pairs.setPotential('PEO','PEO', 'table_PEO-PEO.dat', 0 ,1)
pairs.setPotential('PEC','PEO', 'table_PEC-PEO.dat', 0 ,1)
pairs.setPotential('PEC','PEC', 'table_PEC-PEC.dat', 0 ,1)
app.add(pairs)
bonds = galamost.BondForceTable(all_info, npoints_in_table)
bonds.setPotential('peo10-10.CG:1', 'table_peo10-10.CG-1.dat', 0 ,1)
bonds.setPotential('peo10-10.CG:2', 'table_peo10-10.CG-2.dat', 0 ,1)
bonds.setPotential('peo10-10.CG:3', 'table_peo10-10.CG-3.dat', 0 ,1)
app.add(bonds)
angles = galamost.AngleForceTable(all_info, npoints_in_table-1)
angles.setPotential('peo10-10.CG:4', 'table_peo10-10.CG-4.dat', 0 ,1)
angles.setPotential('peo10-10.CG:5', 'table_peo10-10.CG-5.dat', 0 ,1)
angles.setPotential('peo10-10.CG:6', 'table_peo10-10.CG-6.dat', 0 ,1)
app.add(angles)
