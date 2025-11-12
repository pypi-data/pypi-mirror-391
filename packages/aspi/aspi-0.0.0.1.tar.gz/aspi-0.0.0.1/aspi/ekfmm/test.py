import scipy
import numpy as np

data=scipy.io.loadmat('project.mat')


xyzM=data['xyzM']
xyzA=data['xyzA']
xyzB=data['xyzB']
xyzC=data['xyzC']
xyzMp=data['xyzMp']

from tomo import projection,barycentric_coords

xyzMp2=projection(xyzM, xyzA, xyzB, xyzC)
np.linalg.norm(xyzMp-xyzMp2)


data=scipy.io.loadmat('barycentric_coords.mat')
xyzA=data['xyzA']
xyzB=data['xyzB']
xyzC=data['xyzC']
xyzMp=data['xyzMp']

wA=data['wA']
wB=data['wB']
wC=data['wC']

[wA2, wB2, wC2] = barycentric_coords(xyzMp, xyzA, xyzB, xyzC);


print(np.linalg.norm(wA.flatten()-wA2.flatten()))
print(np.linalg.norm(wB.flatten()-wB2.flatten()))
print(np.linalg.norm(wC.flatten()-wC2.flatten()))

data=scipy.io.loadmat('indexes_delaunay_triangle.mat')

from tomo import indexes_delaunay_triangle

# lons=np.linspace(lonmin,lonmin+lonstep*(nlon-1),nlon) #lonmin:lonstep:lonmin+lonstep*(nlon-1);
# lats=np.linspace(latmin,latmin+latstep*(nlat-1),nlat)
# [LONS,LATS]=np.meshgrid(lons,lats);

# grid_struct['lons']=lons;
# grid_struct['lats']=lats;
# grid_struct['LONS']=LONS;
# grid_struct['LATS']=LATS;
# grid_struct['nx']=len(lons);
# grid_struct['ny']=len(lats);
# grid_struct['dx']=lonstep;
# grid_struct['dy']=latstep;
# nlon=nx;nlat=ny;lonstep=dx;latstep=dy;lonmin=ox;latmin=oy;

grid_struct={'lons': data['xs'], 'lats': data['ys'], 
'nx': len(data['xs'].flatten()), 'ny': len(data['ys'].flatten()),
'dx': data['dx'], 'dy': data['dy']
}

iA=data['iA']
iB=data['iB']
iC=data['iC']

[iA2,iB2,iC2]=indexes_delaunay_triangle(grid_struct, data['lons_M'], data['lats_M'])

print(np.linalg.norm(iA-iA2))
print(np.linalg.norm(iB-iB2))
print(np.linalg.norm(iC-iC2))



###
# This is a DEMO script to benchmark between Pyefkmm and bh_tomo (Matlab) packages
#
# By Yangkang Chen, Feb 24, 2025
#
# First download the benchmark data output from bh_tomo package
# https://github.com/aaspip/data/blob/main/bench_raytracing2d.mat

import scipy
data=scipy.io.loadmat('../demos/bench_raytracing2d.mat')
ox=float(data['g'][0][0][0]);
oz=float(data['g'][0][0][1]);
dx=float(data['g'][0][0][2]);
dz=float(data['g'][0][0][3]);
nx=int(data['g'][0][0][4]);
nz=int(data['g'][0][0][5]);
ox=0;
oz=0;
dx=0.2;
dz=0.2;
nx=41;
nz=41;


slowness=data['s']
vel=1.0/slowness.reshape([nz,nx],order='F')

rays=data['rays']

rays=[ii[0] for ii in rays]

# from tomo import formL2d
# G=formL2d(rays, ax=[ox,dx,nx],ay=[oz,dz,nz])

# import matplotlib.pyplot as plt
# # plt.imshow(G[0,:].reshape(nx,nz,order='F'))
# plt.imshow(G[1,:].reshape(nx,nz,order='F'))
# plt.show()
# 
# 
# plt.imshow(G[8,:].reshape(nx,nz,order='F').transpose());
# plt.colorbar()
# plt.show()
# 
# plt.imshow(G[15,:].reshape(nx,nz,order='F').transpose());
# plt.colorbar()
# plt.show()


# import matplotlib.pyplot as plt
# plt.figure(figsize=(16, 8))
# plt.subplot(121)
# 
# plt.imshow(vel,cmap=plt.cm.jet, interpolation='none', extent=[0,dx*(nx-1),dz*(nz-1),0]);
# plt.xlabel('Lateral (km)');plt.ylabel('Depth (km)');
# plt.colorbar(orientation='horizontal',shrink=0.6,label='Velocity (km/s)');
# 
# #put receiver
# for ii in data['Rx']:
# 	plt.plot(ii[0],ii[1],marker='v',markersize=12,color='b')
# #put 2D rays
# for ii in range(len(rays)):
# 	plt.plot(rays[ii][0][:,0],rays[ii][0][:,1],color='k')
# #put source
# for ii in data['Tx']:
# 	plt.plot(0,0,marker='*',markersize=12,color='red')
# plt.title('bh_tomo package')

# ##########################################################################################
# ## Below is for pyekfmm
# ##########################################################################################
# import numpy as np
# import pyekfmm as fmm
# 
# vxyz=np.transpose(vel, (1,0));
# sx=0;
# sy=0;
# sz=0;
# dy=dx;ny=1;
# 
# t=fmm.eikonal(vel.transpose().flatten(order='F'),xyz=np.array([sx,sy,sz]),ax=[0,dx,nx],ay=[0,dy,ny],az=[0,dz,nz],order=2);
# time=t.reshape(nx,nz,order='F');#first axis (vertical) is x, second is y, third is z
# tzx=np.transpose(time, (1,0));
# rays2=[]
# for ii in data['Rx']:
# 	rx=float(ii[0])
# 	rz=float(ii[1])
# 	paths=fmm.ray2d(time,source=[0,0],receiver=[rx,rz],step=0.01,trim=1,ax=[0,dx,nx],ay=[0,dz,nz])#,trim=0.01
# 	rays2.append(paths.transpose())
# 
# 
# # import matplotlib.pyplot as plt
# plt.subplot(122)
# plt.imshow(vel,cmap=plt.cm.jet, interpolation='none', extent=[0,dx*(nx-1),dz*(nz-1),0]);
# plt.xlabel('Lateral (km)');plt.ylabel('Depth (km)');
# plt.colorbar(orientation='horizontal',shrink=0.6,label='Velocity (km/s)');
# 
# #put receiver
# for ii in data['Rx']:
# 	plt.plot(ii[0],ii[1],marker='v',markersize=12,color='b')
# #put 2D rays
# for ii in range(len(rays2)):
# 	plt.plot(rays2[ii][:,0],rays2[ii][:,1],color='k')
# #put source
# for ii in data['Tx']:
# 	plt.plot(0,0,marker='*',markersize=12,color='red')
# plt.title('Pyekfmm package')
# 
# plt.savefig('test_pyekfmm_raytracing2d_benchmarkWITHbhtomo.png',format='png',dpi=300,bbox_inches='tight', pad_inches=0)
# 
# plt.show()
# 	
# 





